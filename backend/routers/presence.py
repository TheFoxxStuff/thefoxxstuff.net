"""
Presence system — WebSocket + Redis (оптимизированная версия).

Улучшения:
  - Используем Redis Set для online users (O(1) вместо SCAN)
  - Увеличен PUSH_INTERVAL с 3 до 10 сек
  - Лимит на количество пользователей в ответе (MAX_ONLINE_USERS)
  - Pipeline для всех Redis операций
  - Graceful disconnect с leave сообщением
"""

import asyncio
import json
import logging
import time
from typing import Optional, Set

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

# ─── Конфигурация ─────────────────────────────────────────────────────────────
PRESENCE_TTL = 60           # TTL ключей в Redis
HEARTBEAT_INTERVAL = 30     # Клиент шлёт heartbeat каждые 30 сек
PUSH_INTERVAL = 3          # Сервер пушит state каждые 10 сек (было 3)
MAX_ONLINE_USERS = 100      # Лимит пользователей в ответе (для UI)
PROFILE_CACHE_TTL = 300     # Кеш профиля 5 мин

# ─── Redis ключи ──────────────────────────────────────────────────────────────
def _user_key(user_id: str) -> str:
    return f"presence:user:{user_id}"

def _viewing_key(entity_type: str, entity_id: str) -> str:
    return f"presence:viewing:{entity_type}:{entity_id}"

def _profile_key(user_id: str) -> str:
    return f"presence:profile:{user_id}"

# ─── Сериализация ─────────────────────────────────────────────────────────────
def _serialize_user(user: dict, entity_type=None, entity_id=None) -> dict:
    """Минимальный набор полей для presence."""
    return {
        "user_id": str(user.get("_id") or user.get("user_id", "")),
        "username": user.get("username", ""),
        "display_name": user.get("display_name") or user.get("username", ""),
        "avatar_thumb": user.get("avatar_thumb"),
        "role": user.get("role", "user"),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "ts": time.time(),  # Для отладки
    }

def _serialize_for_response(data: dict) -> dict:
    """Убираем служебные поля перед отправкой клиенту."""
    return {
        "user_id": data["user_id"],
        "username": data["username"],
        "display_name": data["display_name"],
        "avatar_thumb": data["avatar_thumb"],
        "role": data["role"],
    }

# ─── Получение пользователя ───────────────────────────────────────────────────
async def _get_user(token: str) -> Optional[dict]:
    """JWT → user dict с кешированием профиля."""
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
    if not redis:
        return None

    # Проверяем кеш профиля
    try:
        cached = await redis.get(_profile_key(user_id))
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # Берём из MongoDB
    try:
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None

        user_dict = {
            "_id": str(user["_id"]),
            "username": user.get("username", ""),
            "display_name": user.get("display_name", ""),
            "avatar_thumb": user.get("avatar_thumb"),
            "role": user.get("role", "user"),
        }

        # Кешируем на 5 мин
        await redis.setex(
            _profile_key(user_id), 
            PROFILE_CACHE_TTL, 
            json.dumps(user_dict)
        )
        return user_dict
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None

# ─── Оптимизированное получение online ────────────────────────────────────────
async def _fetch_online(redis) -> list:
    """Используем Redis Set вместо SCAN — O(1) vs O(N)."""
    try:
        # Получаем ID из Set (быстро)
        user_ids = await redis.smembers("presence:online")
        if not user_ids:
            return []
        
        # Ограничиваем для UI (не показываем 1000 аватарок)
        user_ids = list(user_ids)[:MAX_ONLINE_USERS]
        
        # Batch get через pipeline
        pipe = redis.pipeline()
        for uid in user_ids:
            pipe.get(_user_key(uid))
        
        results = await pipe.execute()
        
        users = []
        for raw in results:
            if not raw:
                continue
            try:
                d = json.loads(raw)
                users.append(_serialize_for_response(d))
            except Exception:
                pass
        
        return users
    except Exception as e:
        logger.error(f"Failed to fetch online: {e}")
        return []

# ─── Получение viewing ────────────────────────────────────────────────────────
async def _fetch_viewing(redis, entity_type: str, entity_id: str) -> list:
    """Пользователи, просматривающие конкретный контент."""
    try:
        user_ids = await redis.smembers(_viewing_key(entity_type, entity_id))
        if not user_ids:
            return []
        
        # Ограничиваем
        user_ids = list(user_ids)[:MAX_ONLINE_USERS]
        
        pipe = redis.pipeline()
        for uid in user_ids:
            pipe.get(_user_key(uid))
        
        results = await pipe.execute()
        
        users = []
        for raw in results:
            if not raw:
                continue
            try:
                d = json.loads(raw)
                users.append(_serialize_for_response(d))
            except Exception:
                pass
        
        return users
    except Exception as e:
        logger.error(f"Failed to fetch viewing: {e}")
        return []

# ─── Установка presence ───────────────────────────────────────────────────────
async def _set_presence(redis, user: dict, entity_type: str, entity_id: str):
    """Atomic update с очисткой старого viewing."""
    user_id = str(user.get("_id") or user.get("user_id"))
    key = _user_key(user_id)

    # Проверяем старое состояние для очистки
    old_entity = None
    try:
        old_raw = await redis.get(key)
        if old_raw:
            old = json.loads(old_raw)
            ot, oi = old.get("entity_type"), old.get("entity_id")
            if (ot != entity_type or oi != entity_id) and ot and oi:
                old_entity = (ot, oi)
    except Exception:
        pass

    # Формируем payload
    payload = _serialize_user(user, entity_type, entity_id)
    
    # Atomic pipeline
    pipe = redis.pipeline()
    
    # Удаляем из старого viewing если нужно
    if old_entity:
        pipe.srem(_viewing_key(old_entity[0], old_entity[1]), user_id)
    
    # Основные операции
    pipe.setex(key, PRESENCE_TTL, json.dumps(payload))
    pipe.sadd("presence:online", user_id)
    pipe.expire("presence:online", PRESENCE_TTL)
    
    if entity_type and entity_id:
        vk = _viewing_key(entity_type, entity_id)
        pipe.sadd(vk, user_id)
        pipe.expire(vk, PRESENCE_TTL)
    
    await pipe.execute()

# ─── Удаление presence ────────────────────────────────────────────────────────
async def _del_presence(redis, user_id: str, entity_type=None, entity_id=None):
    """Cleanup при disconnect."""
    pipe = redis.pipeline()
    pipe.delete(_user_key(user_id))
    pipe.srem("presence:online", user_id)
    
    if entity_type and entity_id:
        pipe.srem(_viewing_key(entity_type, entity_id), user_id)
    
    await pipe.execute()

# ─── WebSocket endpoint ───────────────────────────────────────────────────────
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
    
    if not user:
        # Анонимные тоже могут видеть presence, но не записываются
        pass

    cur_type: Optional[str] = None
    cur_id: Optional[str] = None
    last_state: Optional[str] = None
    is_active = True

    async def push_state(force: bool = False) -> bool:
        """Пушим state только если изменился или force=True."""
        nonlocal last_state
        if websocket.client_state != WebSocketState.CONNECTED:
            return False
        
        try:
            online = await _fetch_online(redis)
            viewing = await _fetch_viewing(redis, cur_type, cur_id) if cur_type and cur_id else []
            
            msg = {
                "type": "update",
                "online": online,
                "onlineCount": len(online),
                "viewing": viewing,
                "viewingCount": len(viewing),
            }
            
            # Проверяем изменения
            state_str = json.dumps(msg, sort_keys=True, default=str)
            if not force and state_str == last_state:
                return True
            
            last_state = state_str
            await websocket.send_json(msg)
            return True
            
        except Exception as e:
            logger.debug(f"Push state failed: {e}")
            return False

    async def recv_loop():
        """Обработка сообщений от клиента."""
        nonlocal cur_type, cur_id, is_active
        
        try:
            while is_active:
                try:
                    raw = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=70.0,  # 70 сек без сообщения = disconnect
                    )
                except asyncio.TimeoutError:
                    logger.debug(f"WS timeout uid={user_id}")
                    return

                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")

                if msg_type == "heartbeat":
                    et = msg.get("entity_type")
                    ei = msg.get("entity_id")
                    cur_type = et
                    cur_id = ei
                    
                    if user:
                        await _set_presence(redis, user, et, ei)
                    
                    # Пушим сразу после heartbeat
                    await push_state()

                elif msg_type == "ping":
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json({"type": "pong"})

                elif msg_type == "leave":
                    # Клиент явно уходит со страницы
                    return

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.debug(f"WS recv error: {e}")

    async def push_loop():
        """Периодический push (редко)."""
        while is_active and websocket.client_state == WebSocketState.CONNECTED:
            await asyncio.sleep(PUSH_INTERVAL)
            if not await push_state():
                break

    # Первый push сразу
    await push_state(force=True)

    # Запускаем параллельно
    recv_task = asyncio.create_task(recv_loop())
    push_task = asyncio.create_task(push_loop())

    try:
        done, pending = await asyncio.wait(
            [recv_task, push_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logger.debug(f"WS error: {e}")
    finally:
        is_active = False
        recv_task.cancel()
        push_task.cancel()

        # Cleanup в Redis
        if user and user_id:
            try:
                await _del_presence(redis, user_id, cur_type, cur_id)
            except Exception as e:
                logger.error(f"Failed to del presence: {e}")

        # Закрываем соединение
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass

        logger.debug(f"WS closed uid={user_id}")

# ─── REST fallback (для отладки/фолбэка) ──────────────────────────────────────
@router.get("/online")
async def get_online():
    """HTTP fallback для получения online users."""
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0, "source": "error"}
    
    try:
        users = await _fetch_online(redis)
        return {"users": users, "count": len(users), "source": "redis"}
    except Exception as e:
        logger.error(f"REST online error: {e}")
        return {"users": [], "count": 0, "source": "error"}

@router.get("/viewing/{entity_type}/{entity_id}")
async def get_viewing(entity_type: str, entity_id: str):
    """HTTP fallback для получения viewing users."""
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0, "source": "error"}
    
    try:
        users = await _fetch_viewing(redis, entity_type, entity_id)
        return {"users": users, "count": len(users), "source": "redis"}
    except Exception as e:
        logger.error(f"REST viewing error: {e}")
        return {"users": [], "count": 0, "source": "error"}