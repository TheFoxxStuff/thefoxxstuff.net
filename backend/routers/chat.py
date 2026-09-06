"""
Guest chat — WebSocket + Redis Pub/Sub.

Раньше список соединений и rate-limit жили в памяти процесса (обычный dict/list).
Это ломалось при 2+ uvicorn воркерах (см. Dockerfile --workers 2): сообщение,
отправленное клиентом на воркере A, никогда не долетало до клиентов на воркере B,
а счётчик "online" и rate-limit тоже были не общими.

Теперь, по аналогии с presence.py:
  - Список онлайн-соединений — Redis Set (SADD/SREM/SCARD), общий для всех воркеров.
  - Новое сообщение публикуется в Redis Pub/Sub — его получают все WS-хендлеры
    на всех воркерах/репликах и рассылают своим локальным клиентам.
  - Rate limit — атомарный Redis SET NX PX, тоже общий для всех воркеров.
"""

import asyncio
import html
import json
import logging
import re
import uuid
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt

from cache import get_pool, get_redis
from config import settings
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

CHAT_CHANNEL   = "chat:messages"
ONLINE_SET_KEY = "chat:online"
RATE_LIMIT_MS  = 1500  # мин. интервал между сообщениями одного юзера

MAX_MSG_LENGTH       = 500
MAX_STORED_MESSAGES  = 200  # keep last N in DB


def sanitize(text: str) -> str:
    """Sanitize message text"""
    text = html.escape(text.strip())
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace
    return text[:MAX_MSG_LENGTH]


def serialize_message(doc: dict) -> dict:
    created_at = doc.get("created_at", datetime.utcnow())
    return {
        "type": "message",
        "_id": str(doc["_id"]),
        "username": doc.get("username", "Guest"),
        "display_name": doc.get("display_name", ""),
        "avatar_thumb": doc.get("avatar_thumb"),
        "role": doc.get("role", "user"),
        "text": doc.get("text", ""),
        "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
    }


@router.get("/messages")
async def get_messages(limit: int = Query(50, le=100)):
    """Get recent chat messages"""
    db = get_db()
    cursor = db.chat_messages.find().sort("created_at", -1).limit(limit)
    messages = []
    async for doc in cursor:
        messages.append(serialize_message(doc))
    messages.reverse()
    return messages


async def _online_count(redis) -> int:
    try:
        return await redis.scard(ONLINE_SET_KEY)
    except Exception:
        return 0


async def _publish(redis, payload: dict):
    try:
        await redis.publish(CHAT_CHANNEL, json.dumps(payload, default=str))
    except Exception as e:
        logger.debug(f"chat publish failed: {e}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await websocket.accept()

    redis = get_redis()
    if not redis:
        # Без Redis нет ни общей рассылки, ни общего rate-limit — не притворяемся.
        await websocket.close(code=1000, reason="Redis unavailable")
        return

    db = get_db()

    user_info = {
        "user_id": None,
        "username": "Guest",
        "display_name": "",
        "avatar_thumb": None,
        "role": "guest",
    }

    if token:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                user = await db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    user_info = {
                        "user_id": str(user["_id"]),
                        "username": user.get("username", "Guest"),
                        "display_name": user.get("display_name", ""),
                        "avatar_thumb": user.get("avatar_thumb"),
                        "role": user.get("role", "user"),
                    }
        except (JWTError, Exception):
            pass

    conn_id   = uuid.uuid4().hex
    is_active = True

    await redis.sadd(ONLINE_SET_KEY, conn_id)
    await _publish(redis, {"type": "online_count", "count": await _online_count(redis)})

    # ── Redis Pub/Sub — рассылка сообщений со всех воркеров ────────────────
    async def pubsub_loop():
        pool = get_pool()
        if not pool:
            return
        from redis.asyncio import Redis as AioRedis
        sub_client = AioRedis(connection_pool=pool)
        pubsub = sub_client.pubsub()
        try:
            await pubsub.subscribe(CHAT_CHANNEL)
            async for message in pubsub.listen():
                if not is_active or websocket.client_state != WebSocketState.CONNECTED:
                    break
                if message["type"] != "message":
                    continue
                try:
                    await websocket.send_text(message["data"])
                except Exception:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"chat pubsub loop error: {e}")
        finally:
            try:
                await pubsub.unsubscribe(CHAT_CHANNEL)
                await pubsub.close()
                await sub_client.aclose()
            except Exception:
                pass

    # ── Приём сообщений от этого клиента ────────────────────────────────
    async def recv_loop():
        nonlocal is_active
        try:
            cursor = db.chat_messages.find().sort("created_at", -1).limit(50)
            history = []
            async for doc in cursor:
                history.append(serialize_message(doc))
            history.reverse()
            await websocket.send_text(json.dumps({"type": "history", "messages": history}, default=str))

            while True:
                data = await websocket.receive_text()

                try:
                    payload_in = json.loads(data)
                except json.JSONDecodeError:
                    continue

                if payload_in.get("type") != "message":
                    continue

                if not user_info.get("user_id"):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "text": "Login required to send messages",
                    }))
                    continue

                text = payload_in.get("text", "").strip()
                if not text:
                    continue
                text = sanitize(text)
                if not text:
                    continue

                # Rate limit — атомарно и общо для всех воркеров.
                # Если юзер шлёт слишком часто — просто молча игнорируем сообщение,
                # без "Slow down" (раньше присылали error, теперь этого не делаем).
                uid = user_info["user_id"]
                allowed = await redis.set(f"chat:ratelimit:{uid}", "1", nx=True, px=RATE_LIMIT_MS)
                if not allowed:
                    continue

                # Re-fetch user info (in case profile was updated)
                user = await db.users.find_one({"_id": ObjectId(uid)})
                if user:
                    user_info["display_name"] = user.get("display_name", "")
                    user_info["avatar_thumb"] = user.get("avatar_thumb")
                    user_info["username"] = user.get("username", "Guest")
                    user_info["role"] = user.get("role", "user")

                msg_doc = {
                    "user_id": uid,
                    "username": user_info["username"],
                    "display_name": user_info.get("display_name", ""),
                    "avatar_thumb": user_info.get("avatar_thumb"),
                    "role": user_info.get("role", "user"),
                    "text": text,
                    "created_at": datetime.utcnow(),
                }
                result = await db.chat_messages.insert_one(msg_doc)
                msg_doc["_id"] = result.inserted_id

                await _publish(redis, serialize_message(msg_doc))

                # Cleanup old messages
                total = await db.chat_messages.count_documents({})
                if total > MAX_STORED_MESSAGES:
                    oldest = db.chat_messages.find().sort("created_at", 1).limit(total - MAX_STORED_MESSAGES)
                    ids = [doc["_id"] async for doc in oldest]
                    if ids:
                        await db.chat_messages.delete_many({"_id": {"$in": ids}})

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.debug(f"chat recv error: {e}")
        finally:
            is_active = False

    recv_task   = asyncio.create_task(recv_loop())
    pubsub_task = asyncio.create_task(pubsub_loop())

    try:
        done, pending = await asyncio.wait(
            [recv_task, pubsub_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    finally:
        is_active = False
        try:
            await redis.srem(ONLINE_SET_KEY, conn_id)
            await _publish(redis, {"type": "online_count", "count": await _online_count(redis)})
        except Exception as e:
            logger.debug(f"chat cleanup error: {e}")
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass
