"""
Presence system — WebSocket + Redis pub/sub.

Архитектура:
  - Каждый клиент подключается к /api/presence/ws?token=...
  - Сервер хранит состояние в Redis (TTL ключи)
  - При любом изменении публикует в Redis канал → все WS получают обновление
  - Heartbeat приходит через WS сообщение (не HTTP)
  - Disconnect детектится мгновенно

Redis ключи:
  presence:user:{user_id}            → JSON профиль + страница, TTL 60s
  presence:viewing:{type}:{id}       → Set user_id, TTL 60s
  presence:user_profile:{user_id}    → кеш профиля MongoDB, TTL 300s

Redis pub/sub канал:
  presence:updates                   → broadcast всем WS соединениям
"""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt
from bson import ObjectId

from cache import get_redis
from database import get_db
from config import settings
from auth import ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/presence", tags=["presence"])

# TTL для ключей присутствия (сек). Клиент шлёт heartbeat каждые 30 сек.
PRESENCE_TTL = 60


# ─── Вспомогательные функции ──────────────────────────────────────────────────

def _serialize_user(user: dict, entity_type: str = None, entity_id: str = None) -> dict:
    return {
        "user_id": str(user["_id"]),
        "username": user.get("username", ""),
        "display_name": user.get("display_name") or user.get("username", ""),
        "avatar_thumb": user.get("avatar_thumb"),
        "role": user.get("role", "user"),
        "entity_type": entity_type,
        "entity_id": entity_id,
    }


async def _get_user_by_token(token: str) -> Optional[dict]:
    """Декодируем JWT и возвращаем юзера. Профиль кешируем в Redis на 5 мин."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    redis = get_redis()

    # Проверяем кеш профиля — убираем MongoDB запрос при каждом heartbeat
    if redis:
        cached = await redis.get(f"presence:user_profile:{user_id}")
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass

    # Идём в MongoDB
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    # Сериализуем для кеша (ObjectId → str)
    user_data = dict(user)
    user_data["_id"] = str(user_data["_id"])

    if redis:
        await redis.setex(
            f"presence:user_profile:{user_id}",
            300,  # 5 минут
            json.dumps(user_data, default=str),
        )

    return user_data


async def _get_online_users(redis) -> list[dict]:
    """Получить список всех онлайн пользователей из Redis."""
    keys = []
    async for key in redis.scan_iter("presence:user:*"):
        keys.append(key)

    if not keys:
        return []

    pipe = redis.pipeline()
    for key in keys:
        pipe.get(key)
    results = await pipe.execute()

    users = []
    for raw in results:
        if not raw:
            continue
        try:
            data = json.loads(raw)
            users.append({
                "user_id": data["user_id"],
                "username": data["username"],
                "display_name": data["display_name"],
                "avatar_thumb": data["avatar_thumb"],
                "role": data["role"],
            })
        except Exception:
            continue

    return users


async def _get_viewing_users(redis, entity_type: str, entity_id: str) -> list[dict]:
    """Кто смотрит конкретный контент."""
    viewing_key = f"presence:viewing:{entity_type}:{entity_id}"
    user_ids = await redis.smembers(viewing_key)

    if not user_ids:
        return []

    pipe = redis.pipeline()
    for uid in user_ids:
        pipe.get(f"presence:user:{uid}")
    results = await pipe.execute()

    users = []
    for raw in results:
        if not raw:
            continue
        try:
            data = json.loads(raw)
            users.append({
                "user_id": data["user_id"],
                "username": data["username"],
                "display_name": data["display_name"],
                "avatar_thumb": data["avatar_thumb"],
                "role": data["role"],
            })
        except Exception:
            continue

    return users


async def _publish_update(redis, entity_type: str = None, entity_id: str = None):
    """
    Публикуем событие обновления в Redis pub/sub.
    Все подключённые WS получат актуальное состояние.
    """
    payload = json.dumps({
        "entity_type": entity_type,
        "entity_id": entity_id,
    })
    await redis.publish("presence:updates", payload)


async def _update_presence(redis, user: dict, entity_type: str, entity_id: str):
    """Обновить присутствие пользователя в Redis + опубликовать изменение."""
    user_id = str(user["_id"]) if "_id" in user else user["user_id"]
    user_key = f"presence:user:{user_id}"
    payload = _serialize_user(user, entity_type, entity_id)

    # Снимаем старый viewing если страница изменилась
    old_raw = await redis.get(user_key)
    if old_raw:
        try:
            old = json.loads(old_raw)
            old_type = old.get("entity_type")
            old_id = old.get("entity_id")
            if (old_type != entity_type or old_id != entity_id) and old_type and old_id:
                await redis.srem(f"presence:viewing:{old_type}:{old_id}", user_id)
        except Exception:
            pass

    # Сохраняем присутствие
    await redis.setex(user_key, PRESENCE_TTL, json.dumps(payload))

    # Добавляем в viewing если смотрит контент
    if entity_type and entity_id:
        viewing_key = f"presence:viewing:{entity_type}:{entity_id}"
        await redis.sadd(viewing_key, user_id)
        await redis.expire(viewing_key, PRESENCE_TTL)

    await _publish_update(redis, entity_type, entity_id)


async def _remove_presence(redis, user_id: str, entity_type: str = None, entity_id: str = None):
    """Удалить присутствие пользователя из Redis + опубликовать изменение."""
    await redis.delete(f"presence:user:{user_id}")

    if entity_type and entity_id:
        await redis.srem(f"presence:viewing:{entity_type}:{entity_id}", user_id)

    await _publish_update(redis, entity_type, entity_id)


# ─── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws")
async def presence_websocket(
    websocket: WebSocket,
    token: str = Query(None),
):
    """
    Главный WebSocket для presence.

    Клиент шлёт JSON сообщения:
      { "type": "heartbeat", "entity_type": "blog", "entity_id": "abc123" }
      { "type": "leave" }

    Сервер пушит JSON при любом изменении:
      { "type": "update", "online": [...], "viewing": [...], "viewingCount": N, "onlineCount": N }
    """
    await websocket.accept()

    redis = get_redis()
    if not redis:
        await websocket.send_json({"type": "error", "message": "Service unavailable"})
        await websocket.close()
        return

    # Аутентификация
    user = None
    user_id = None
    if token:
        user = await _get_user_by_token(token)
        if user:
            user_id = str(user.get("_id") or user.get("user_id"))

    # Текущая страница пользователя
    current_entity_type = None
    current_entity_id = None

    # Подписываемся на Redis pub/sub в отдельной корутине
    pubsub = redis.pubsub()
    await pubsub.subscribe("presence:updates")

    async def send_state(entity_type=None, entity_id=None):
        """Отправить текущее состояние клиенту."""
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        try:
            online = await _get_online_users(redis)
            viewing = []
            et = entity_type or current_entity_type
            eid = entity_id or current_entity_id
            if et and eid:
                viewing = await _get_viewing_users(redis, et, eid)

            await websocket.send_json({
                "type": "update",
                "online": online,
                "onlineCount": len(online),
                "viewing": viewing,
                "viewingCount": len(viewing),
            })
        except Exception:
            pass

    async def listen_pubsub():
        """Слушаем Redis pub/sub и пушим обновления клиенту."""
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                try:
                    data = json.loads(message["data"])
                    # Отправляем state — клиент сам разберёт что ему нужно
                    await send_state(
                        data.get("entity_type"),
                        data.get("entity_id"),
                    )
                except Exception:
                    continue
        except Exception:
            pass

    # Запускаем pubsub listener параллельно
    pubsub_task = asyncio.create_task(listen_pubsub())

    # Сразу шлём текущее состояние при подключении
    await send_state()

    try:
        while True:
            # Ждём сообщение от клиента с таймаутом
            # Если 70 сек нет heartbeat — считаем disconnected
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=70.0)
            except asyncio.TimeoutError:
                # Клиент не слал heartbeat — отключаем
                logger.debug("WS presence timeout, disconnecting user_id=%s", user_id)
                break

            try:
                msg = json.loads(raw)
            except Exception:
                continue

            msg_type = msg.get("type")

            if msg_type == "heartbeat":
                entity_type = msg.get("entity_type")
                entity_id = msg.get("entity_id")

                current_entity_type = entity_type
                current_entity_id = entity_id

                if user:
                    await _update_presence(redis, user, entity_type, entity_id)
                else:
                    # Аноним — просто шлём текущее состояние
                    await send_state(entity_type, entity_id)

            elif msg_type == "leave":
                if user and user_id:
                    await _remove_presence(redis, user_id, current_entity_type, current_entity_id)
                break

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.debug("WS presence error: %s", e)
    finally:
        # Чистим при любом отключении
        pubsub_task.cancel()
        try:
            await pubsub.unsubscribe("presence:updates")
            await pubsub.aclose()
        except Exception:
            pass

        if user and user_id:
            try:
                await _remove_presence(redis, user_id, current_entity_type, current_entity_id)
            except Exception:
                pass

        logger.debug("WS presence closed for user_id=%s", user_id)


# ─── REST fallback (для совместимости / анонимов) ─────────────────────────────

@router.get("/online")
async def get_online_users():
    """REST fallback — публичный список онлайн."""
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}
    try:
        users = await _get_online_users(redis)
        return {"users": users, "count": len(users)}
    except Exception:
        return {"users": [], "count": 0}


@router.get("/viewing/{entity_type}/{entity_id}")
async def get_viewing(entity_type: str, entity_id: str):
    """REST fallback — кто смотрит контент."""
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}
    try:
        users = await _get_viewing_users(redis, entity_type, entity_id)
        return {"users": users, "count": len(users)}
    except Exception:
        return {"users": [], "count": 0}
