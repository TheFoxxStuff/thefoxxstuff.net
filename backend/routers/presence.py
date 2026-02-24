"""
Presence system — WebSocket + Redis Pub/Sub.

Архитектура:
  - Клиент подключается → сразу регистрируется в Redis (online)
  - При любом изменении → redis.publish("presence_changes", data)
  - Все активные WS-обработчики подписаны через pubsub-клиент
  - Мгновенные обновления, нет polling

Grace period (только для навигации между страницами):
  - При закрытии вкладки (code 1000/аномальное) → удаляем сразу после короткой паузы (2 сек)
  - При SvelteKit-навигации (code 1001 "going away") → grace period 5 сек
  - Если юзер переподключился за grace period → удаление отменяется
  - publish("leave") вызывается ПОСЛЕ реального удаления из Redis
"""

import asyncio
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt
from bson import ObjectId

from cache import get_redis, get_pool
from database import get_db
from config import settings
from auth import ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/presence", tags=["presence"])

# ─── Конфигурация ─────────────────────────────────────────────────────────────
PRESENCE_TTL        = 90   # TTL одной записи пользователя (сек)
HEARTBEAT_TIMEOUT   = 70   # Ждём сообщение от клиента не более 70 сек
PROFILE_CACHE_TTL   = 300  # Кеш профиля 5 мин
MAX_ONLINE_USERS    = 100  # Лимит в UI-ответе

GRACE_NAVIGATE      = 8    # Сек — при SPA-навигации (code 1001)
GRACE_CLOSE         = 5    # Сек — при закрытии/реконнекте

PUBSUB_CHANNEL = "presence_changes"

# ─── Redis ключи ──────────────────────────────────────────────────────────────
def _user_key(uid: str) -> str:
    return f"presence:user:{uid}"

def _viewing_key(entity_type: str, entity_id: str) -> str:
    return f"presence:viewing:{entity_type}:{entity_id}"

def _profile_key(uid: str) -> str:
    return f"presence:profile:{uid}"

def _grace_key(uid: str) -> str:
    return f"presence:grace:{uid}"

# ─── Сериализация ─────────────────────────────────────────────────────────────
def _serialize_user(user: dict, entity_type=None, entity_id=None) -> dict:
    return {
        "user_id":      str(user.get("_id") or user.get("user_id", "")),
        "username":     user.get("username", ""),
        "display_name": user.get("display_name") or user.get("username", ""),
        "avatar_thumb": user.get("avatar_thumb"),
        "role":         user.get("role", "user"),
        "entity_type":  entity_type,
        "entity_id":    entity_id,
        "ts":           time.time(),
    }

def _serialize_for_response(data: dict) -> dict:
    return {
        "user_id":      data["user_id"],
        "username":     data["username"],
        "display_name": data["display_name"],
        "avatar_thumb": data["avatar_thumb"],
        "role":         data["role"],
    }

# ─── Инвалидация кэша профиля (вызывается после обновления профиля) ──────────
async def invalidate_profile_cache(user_id: str):
    """Удаляет кэш профиля из Redis — следующий presence heartbeat подтянет свежие данные."""
    redis = get_redis()
    if redis:
        try:
            await redis.delete(_profile_key(user_id))
        except Exception as e:
            logger.debug(f"Failed to invalidate profile cache for {user_id}: {e}")

# ─── Получение пользователя по токену ────────────────────────────────────────
async def _get_user(token: str) -> Optional[dict]:
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

    try:
        cached = await redis.get(_profile_key(user_id))
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        user_dict = {
            "_id":          str(user["_id"]),
            "username":     user.get("username", ""),
            "display_name": user.get("display_name", ""),
            "avatar_thumb": user.get("avatar_thumb"),
            "role":         user.get("role", "user"),
        }
        await redis.setex(_profile_key(user_id), PROFILE_CACHE_TTL, json.dumps(user_dict))
        return user_dict
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None

# ─── Чтение состояния из Redis ────────────────────────────────────────────────
async def _fetch_online(redis) -> list:
    try:
        user_ids = await redis.smembers("presence:online")
        if not user_ids:
            return []
        user_ids = list(user_ids)[:MAX_ONLINE_USERS]
        pipe = redis.pipeline()
        for uid in user_ids:
            pipe.get(_user_key(uid))
        results = await pipe.execute()

        users = []
        stale_ids = []
        for uid, raw in zip(user_ids, results):
            if not raw:
                # Запись протухла (TTL истёк) — убираем из Set
                stale_ids.append(uid)
                continue
            try:
                users.append(_serialize_for_response(json.loads(raw)))
            except Exception:
                pass

        # Чистим протухшие ID из Set
        if stale_ids:
            pipe2 = redis.pipeline()
            for uid in stale_ids:
                pipe2.srem("presence:online", uid)
            await pipe2.execute()

        return users
    except Exception as e:
        logger.error(f"Failed to fetch online: {e}")
        return []


async def _fetch_viewing(redis, entity_type: str, entity_id: str) -> list:
    try:
        user_ids = await redis.smembers(_viewing_key(entity_type, entity_id))
        if not user_ids:
            return []
        user_ids = list(user_ids)[:MAX_ONLINE_USERS]
        pipe = redis.pipeline()
        for uid in user_ids:
            pipe.get(_user_key(uid))
        results = await pipe.execute()

        users = []
        stale_ids = []
        for uid, raw in zip(user_ids, results):
            if not raw:
                stale_ids.append(uid)
                continue
            try:
                users.append(_serialize_for_response(json.loads(raw)))
            except Exception:
                pass

        if stale_ids:
            vk = _viewing_key(entity_type, entity_id)
            pipe2 = redis.pipeline()
            for uid in stale_ids:
                pipe2.srem(vk, uid)
            await pipe2.execute()

        return users
    except Exception as e:
        logger.error(f"Failed to fetch viewing: {e}")
        return []

# ─── Запись presence ──────────────────────────────────────────────────────────
async def _set_presence(redis, user: dict, entity_type: Optional[str], entity_id: Optional[str]):
    user_id = str(user.get("_id") or user.get("user_id"))
    key = _user_key(user_id)

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

    payload = _serialize_user(user, entity_type, entity_id)

    pipe = redis.pipeline()
    # Отменяем отложенное удаление если было (юзер переподключился)
    pipe.delete(_grace_key(user_id))
    if old_entity:
        pipe.srem(_viewing_key(old_entity[0], old_entity[1]), user_id)
    pipe.setex(key, PRESENCE_TTL, json.dumps(payload))
    pipe.sadd("presence:online", user_id)
    # НЕ ставим expire на presence:online — Set живёт пока в нём есть записи
    if entity_type and entity_id:
        vk = _viewing_key(entity_type, entity_id)
        pipe.sadd(vk, user_id)
        pipe.expire(vk, PRESENCE_TTL)
    await pipe.execute()

# ─── Удаление presence с grace period ────────────────────────────────────────
async def _del_presence_graceful(redis, user_id: str, entity_type, entity_id, close_code: int):
    """
    Удаляем с паузой — различаем навигацию и закрытие вкладки.
    
    close_code 1001 = браузер "going away" (SPA-навигация, F5)
    close_code 1000 = нормальное закрытие
    остальные       = аномальное закрытие (сеть упала и т.д.)
    
    publish("leave") вызывается ПОСЛЕ реального удаления из Redis
    чтобы все клиенты получили актуальный state без юзера.
    """
    grace = GRACE_NAVIGATE if close_code == 1001 else GRACE_CLOSE
    marker = f"{time.time()}"  # уникальный маркер этой сессии

    # Записываем маркер — если юзер переподключится, он удалит его
    try:
        await redis.setex(_grace_key(user_id), grace + 1, marker)
    except Exception:
        pass

    asyncio.create_task(_do_del(redis, user_id, entity_type, entity_id, marker, grace))


async def _do_del(redis, user_id: str, entity_type, entity_id, marker: str, grace: int):
    """Реальное удаление после паузы — только если юзер не переподключился."""
    await asyncio.sleep(grace)
    try:
        current = await redis.get(_grace_key(user_id))
        # Redis может вернуть bytes — декодируем для сравнения
        if isinstance(current, bytes):
            current = current.decode()
        if current != marker:
            # Маркер изменился — юзер переподключился, отменяем
            logger.debug(f"Grace cancelled for {user_id} (reconnected)")
            return

        # Удаляем из Redis
        pipe = redis.pipeline()
        pipe.delete(_user_key(user_id))
        pipe.srem("presence:online", user_id)
        pipe.delete(_grace_key(user_id))
        if entity_type and entity_id:
            pipe.srem(_viewing_key(entity_type, entity_id), user_id)
        await pipe.execute()

        # Публикуем leave ТОЛЬКО после реального удаления
        # Теперь все клиенты получат актуальный state — без этого юзера
        await _publish_change(redis, "leave", user_id, entity_type, entity_id)

        logger.debug(f"Presence deleted for {user_id} (grace={grace}s)")

    except Exception as e:
        logger.error(f"_do_del error for {user_id}: {e}")

# ─── Публикация события ───────────────────────────────────────────────────────
async def _publish_change(redis, change_type: str, user_id: str,
                          entity_type: Optional[str], entity_id: Optional[str]):
    try:
        msg = json.dumps({
            "change":      change_type,
            "user_id":     user_id,
            "entity_type": entity_type,
            "entity_id":   entity_id,
            "ts":          time.time(),
        })
        await redis.publish(PUBSUB_CHANNEL, msg)
    except Exception as e:
        logger.debug(f"Failed to publish change: {e}")

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

    user    = await _get_user(token)
    user_id = str(user.get("_id") or user.get("user_id")) if user else None

    cur_type:   Optional[str] = None
    cur_id:     Optional[str] = None
    is_active   = True
    close_code  = 1000  # будет обновлён в onclose

    # ── Push текущего состояния ───────────────────────────────────────────
    async def push_state() -> bool:
        if websocket.client_state != WebSocketState.CONNECTED:
            return False
        try:
            online  = await _fetch_online(redis)
            viewing = await _fetch_viewing(redis, cur_type, cur_id) if (cur_type and cur_id) else []
            await websocket.send_json({
                "type":         "update",
                "online":       online,
                "onlineCount":  len(online),
                "viewing":      viewing,
                "viewingCount": len(viewing),
            })
            return True
        except Exception as e:
            logger.debug(f"Push state failed: {e}")
            return False

    # ── Redis Pub/Sub — мгновенные обновления ─────────────────────────────
    async def pubsub_loop():
        pool = get_pool()
        if not pool:
            return

        from redis.asyncio import Redis as AioRedis
        sub_client = AioRedis(connection_pool=pool)
        pubsub     = sub_client.pubsub()

        try:
            await pubsub.subscribe(PUBSUB_CHANNEL)
            async for message in pubsub.listen():
                if not is_active:
                    break
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                if message["type"] != "message":
                    continue
                if not await push_state():
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Pubsub loop error: {e}")
        finally:
            try:
                await pubsub.unsubscribe(PUBSUB_CHANNEL)
                await pubsub.close()
                await sub_client.aclose()
            except Exception:
                pass

    # ── Обработка сообщений от клиента ───────────────────────────────────
    async def recv_loop():
        nonlocal cur_type, cur_id, is_active, close_code

        try:
            while is_active:
                try:
                    raw = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=float(HEARTBEAT_TIMEOUT),
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
                    et = msg.get("entity_type") or None
                    ei = msg.get("entity_id")   or None

                    prev_type, prev_id = cur_type, cur_id
                    cur_type, cur_id = et, ei

                    if user:
                        await _set_presence(redis, user, et, ei)
                        change = "move" if (prev_type != et or prev_id != ei) else "heartbeat"
                        await _publish_change(redis, change, user_id, et, ei)

                    await push_state()

                elif msg_type == "ping":
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json({"type": "pong"})

                elif msg_type == "leave":
                    # SPA-навигация: клиент явно говорит что уходит со страницы
                    # НЕ закрываем соединение — просто обновляем entity
                    cur_type = None
                    cur_id   = None
                    if user:
                        await _set_presence(redis, user, None, None)
                        await _publish_change(redis, "move", user_id, None, None)

        except WebSocketDisconnect as e:
            close_code = getattr(e, 'code', 1000)
        except Exception as e:
            logger.debug(f"WS recv error: {e}")

    # ── Старт ─────────────────────────────────────────────────────────────
    if user:
        await _set_presence(redis, user, None, None)
        await _publish_change(redis, "join", user_id, None, None)

    await push_state()

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
    except Exception as e:
        logger.debug(f"WS error: {e}")
    finally:
        is_active = False
        recv_task.cancel()
        pubsub_task.cancel()

        if user and user_id:
            try:
                # Grace period зависит от типа закрытия
                await _del_presence_graceful(redis, user_id, cur_type, cur_id, close_code)
            except Exception as e:
                logger.error(f"Failed to schedule presence deletion: {e}")

        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass

        logger.debug(f"WS closed uid={user_id} code={close_code}")


# ─── REST fallback ────────────────────────────────────────────────────────────
@router.get("/online")
async def get_online():
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
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0, "source": "error"}
    try:
        users = await _fetch_viewing(redis, entity_type, entity_id)
        return {"users": users, "count": len(users), "source": "redis"}
    except Exception as e:
        logger.error(f"REST viewing error: {e}")
        return {"users": [], "count": 0, "source": "error"}
