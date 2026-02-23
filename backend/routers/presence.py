"""
Presence system — WebSocket + Redis.

Архитектура (без pub/sub — надёжнее на малом трафике):
  - Клиент подключается к /api/presence/ws?token=...
  - Шлёт heartbeat каждые 30 сек через WS
  - Сервер обновляет Redis TTL-ключи
  - Сервер сам опрашивает Redis каждые 3 сек и пушит state если изменилось
  - Disconnect детектируется мгновенно через WS close

Redis ключи:
  presence:user:{user_id}          → JSON профиль, TTL 60s
  presence:viewing:{type}:{id}     → Set user_id, TTL 60s
  presence:profile:{user_id}       → кеш профиля из MongoDB, TTL 300s
"""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt
from bson import ObjectId

from cache import get_redis
from database import get_db
from config import settings
from auth import ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/presence", tags=["presence"])

PRESENCE_TTL = 60   # сек — TTL ключей в Redis
PUSH_INTERVAL = 3   # сек — как часто сервер пушит обновлённый state клиенту


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _user_key(user_id: str) -> str:
    return f"presence:user:{user_id}"

def _viewing_key(entity_type: str, entity_id: str) -> str:
    return f"presence:viewing:{entity_type}:{entity_id}"

def _profile_key(user_id: str) -> str:
    return f"presence:profile:{user_id}"


def _serialize(user: dict, entity_type=None, entity_id=None) -> dict:
    return {
        "user_id":      str(user.get("_id") or user.get("user_id", "")),
        "username":     user.get("username", ""),
        "display_name": user.get("display_name") or user.get("username", ""),
        "avatar_thumb": user.get("avatar_thumb"),
        "role":         user.get("role", "user"),
        "entity_type":  entity_type,
        "entity_id":    entity_id,
    }


async def _get_user(token: str) -> Optional[dict]:
    """JWT → user dict. Профиль кешируется в Redis 5 мин."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    redis = get_redis()

    # Кеш профиля — не ходим в MongoDB при каждом heartbeat
    if redis:
        try:
            cached = await redis.get(_profile_key(user_id))
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    user_dict = dict(user)
    user_dict["_id"] = str(user_dict["_id"])

    if redis:
        try:
            await redis.setex(_profile_key(user_id), 300, json.dumps(user_dict, default=str))
        except Exception:
            pass

    return user_dict


async def _fetch_online(redis) -> list:
    try:
        keys = []
        async for k in redis.scan_iter("presence:user:*"):
            keys.append(k)
        if not keys:
            return []
        pipe = redis.pipeline()
        for k in keys:
            pipe.get(k)
        results = await pipe.execute()
        users = []
        for raw in results:
            if not raw:
                continue
            try:
                d = json.loads(raw)
                users.append({
                    "user_id":      d["user_id"],
                    "username":     d["username"],
                    "display_name": d["display_name"],
                    "avatar_thumb": d["avatar_thumb"],
                    "role":         d["role"],
                })
            except Exception:
                pass
        return users
    except Exception:
        return []


async def _fetch_viewing(redis, entity_type: str, entity_id: str) -> list:
    try:
        ids = await redis.smembers(_viewing_key(entity_type, entity_id))
        if not ids:
            return []
        pipe = redis.pipeline()
        for uid in ids:
            pipe.get(_user_key(uid))
        results = await pipe.execute()
        users = []
        for raw in results:
            if not raw:
                continue
            try:
                d = json.loads(raw)
                users.append({
                    "user_id":      d["user_id"],
                    "username":     d["username"],
                    "display_name": d["display_name"],
                    "avatar_thumb": d["avatar_thumb"],
                    "role":         d["role"],
                })
            except Exception:
                pass
        return users
    except Exception:
        return []


async def _set_presence(redis, user: dict, entity_type: str, entity_id: str):
    user_id = str(user.get("_id") or user.get("user_id"))
    key = _user_key(user_id)

    # Убираем из старого viewing если страница изменилась
    try:
        old_raw = await redis.get(key)
        if old_raw:
            old = json.loads(old_raw)
            ot, oi = old.get("entity_type"), old.get("entity_id")
            if (ot != entity_type or oi != entity_id) and ot and oi:
                await redis.srem(_viewing_key(ot, oi), user_id)
    except Exception:
        pass

    payload = _serialize(user, entity_type, entity_id)
    await redis.setex(key, PRESENCE_TTL, json.dumps(payload))

    if entity_type and entity_id:
        vk = _viewing_key(entity_type, entity_id)
        await redis.sadd(vk, user_id)
        await redis.expire(vk, PRESENCE_TTL)


async def _del_presence(redis, user_id: str, entity_type=None, entity_id=None):
    await redis.delete(_user_key(user_id))
    if entity_type and entity_id:
        await redis.srem(_viewing_key(entity_type, entity_id), user_id)


# ─── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws")
async def presence_ws(
    websocket: WebSocket,
    token: str = Query(None),
):
    await websocket.accept()

    redis = get_redis()
    if not redis:
        await websocket.close(code=1011, reason="Redis unavailable")
        return

    user = await _get_user(token)
    user_id = str(user.get("_id") or user.get("user_id")) if user else None

    cur_type: Optional[str] = None
    cur_id:   Optional[str] = None

    # Последний отправленный state — чтобы не пушить дубликаты
    last_state: Optional[str] = None

    async def push_state():
        nonlocal last_state
        if websocket.client_state != WebSocketState.CONNECTED:
            return False
        try:
            online  = await _fetch_online(redis)
            viewing = await _fetch_viewing(redis, cur_type, cur_id) if cur_type and cur_id else []
            msg = {
                "type":         "update",
                "online":       online,
                "onlineCount":  len(online),
                "viewing":      viewing,
                "viewingCount": len(viewing),
            }
            # Пушим только если состояние изменилось
            state_str = json.dumps(msg, sort_keys=True)
            if state_str == last_state:
                return True
            last_state = state_str
            await websocket.send_json(msg)
            return True
        except Exception:
            return False

    # Получаем сообщения от клиента
    async def recv_loop():
        nonlocal cur_type, cur_id
        try:
            while True:
                try:
                    raw = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=70.0,  # 70 сек без heartbeat = disconnect
                    )
                except asyncio.TimeoutError:
                    logger.debug("WS presence timeout uid=%s", user_id)
                    return

                try:
                    msg = json.loads(raw)
                except Exception:
                    continue

                t = msg.get("type")

                if t == "heartbeat":
                    et = msg.get("entity_type") or None
                    ei = msg.get("entity_id")   or None
                    cur_type = et
                    cur_id   = ei
                    if user:
                        await _set_presence(redis, user, et, ei)
                    await push_state()

                elif t == "ping":
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json({"type": "pong"})

                elif t == "leave":
                    return

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.debug("WS recv error: %s", e)

    # Периодический push state (даже без heartbeat от клиента)
    async def push_loop():
        while websocket.client_state == WebSocketState.CONNECTED:
            await asyncio.sleep(PUSH_INTERVAL)
            ok = await push_state()
            if not ok:
                break

    # Первый push сразу при подключении
    await push_state()

    # Запускаем оба цикла параллельно
    recv_task = asyncio.create_task(recv_loop())
    push_task = asyncio.create_task(push_loop())

    try:
        done, pending = await asyncio.wait(
            [recv_task, push_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()
    except Exception as e:
        logger.debug("WS presence outer error: %s", e)
    finally:
        recv_task.cancel()
        push_task.cancel()

        if user and user_id:
            try:
                await _del_presence(redis, user_id, cur_type, cur_id)
            except Exception:
                pass

        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass

        logger.debug("WS presence closed uid=%s", user_id)


# ─── REST fallback ─────────────────────────────────────────────────────────────

@router.get("/online")
async def get_online():
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}
    try:
        users = await _fetch_online(redis)
        return {"users": users, "count": len(users)}
    except Exception:
        return {"users": [], "count": 0}


@router.get("/viewing/{entity_type}/{entity_id}")
async def get_viewing(entity_type: str, entity_id: str):
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}
    try:
        users = await _fetch_viewing(redis, entity_type, entity_id)
        return {"users": users, "count": len(users)}
    except Exception:
        return {"users": [], "count": 0}
