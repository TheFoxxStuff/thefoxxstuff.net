"""
Presence system — отслеживание онлайн пользователей и что они смотрят.

Redis ключи:
  presence:user:{user_id}            → JSON с профилем + текущей страницей, TTL 45s
  presence:viewing:{type}:{id}       → Set user_id'ов, TTL 45s

Heartbeat отправляется с фронта каждые 30 сек.
"""

import json
from fastapi import APIRouter, Depends, Query
from auth import get_optional_user, get_current_user
from cache import get_redis
from config import settings

router = APIRouter(prefix="/api/presence", tags=["presence"])

HEARTBEAT_TTL = 45  # секунды до "оффлайн"
API_BASE = settings.upload_dir  # для avatar URL


def _avatar_url(path: str | None) -> str | None:
    if not path:
        return None
    # Формат: avatars/thumb/xxx.jpg — отдаём через /api/upload/file/
    return path  # фронт сам собирает URL через API_BASE


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


@router.post("/heartbeat")
async def heartbeat(
    entity_type: str = Query(None, description="Тип контента: music/blog/arts/home"),
    entity_id: str = Query(None, description="ID контента (если на странице контента)"),
    user: dict = Depends(get_optional_user),
):
    """
    Фронт вызывает каждые 30 сек.
    Обновляет TTL присутствия в Redis.
    Только авторизованные пользователи видны в онлайн-списке.
    """
    if not user:
        # Анонимы — просто ОК, не трекаем
        return {"ok": True, "tracked": False}

    redis = get_redis()
    if not redis:
        return {"ok": True, "tracked": False}

    user_id = str(user["_id"])
    payload = _serialize_user(user, entity_type, entity_id)

    # Главный ключ присутствия юзера
    user_key = f"presence:user:{user_id}"

    # Снимаем старый viewing ключ если юзер переключился
    try:
        old_raw = await redis.get(user_key)
        if old_raw:
            old = json.loads(old_raw)
            old_type = old.get("entity_type")
            old_id = old.get("entity_id")
            if (old_type != entity_type or old_id != entity_id) and old_type and old_id:
                await redis.srem(f"presence:viewing:{old_type}:{old_id}", user_id)
    except Exception:
        pass

    # Обновляем присутствие
    await redis.setex(user_key, HEARTBEAT_TTL, json.dumps(payload))

    # Если смотрит конкретный контент — добавляем в Set
    if entity_type and entity_id:
        viewing_key = f"presence:viewing:{entity_type}:{entity_id}"
        await redis.sadd(viewing_key, user_id)
        await redis.expire(viewing_key, HEARTBEAT_TTL)

    return {"ok": True, "tracked": True}


@router.delete("/heartbeat")
async def leave(
    entity_type: str = Query(None),
    entity_id: str = Query(None),
    user: dict = Depends(get_optional_user),
):
    """Вызывается при уходе со страницы (visibilitychange / beforeunload)."""
    if not user:
        return {"ok": True}

    redis = get_redis()
    if not redis:
        return {"ok": True}

    user_id = str(user["_id"])

    await redis.delete(f"presence:user:{user_id}")

    if entity_type and entity_id:
        await redis.srem(f"presence:viewing:{entity_type}:{entity_id}", user_id)

    return {"ok": True}


@router.get("/online")
async def get_online_users():
    """
    Список авторизованных пользователей онлайн.
    Публичный endpoint — используется на главной странице.
    Возвращает базовый профиль без чувствительных данных.
    """
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}

    try:
        # Сканируем все ключи присутствия
        keys = await redis.keys("presence:user:*")
        if not keys:
            return {"users": [], "count": 0}

        # Батч-получение
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
                    # Что смотрят — не показываем в глобальном списке (приватность)
                })
            except Exception:
                continue

        return {"users": users, "count": len(users)}

    except Exception as e:
        return {"users": [], "count": 0}


@router.get("/viewing/{entity_type}/{entity_id}")
async def get_viewing(entity_type: str, entity_id: str):
    """
    Кто сейчас смотрит конкретный контент.
    Публичный endpoint — показывается под музыкой/постом/артом.
    """
    redis = get_redis()
    if not redis:
        return {"users": [], "count": 0}

    try:
        viewing_key = f"presence:viewing:{entity_type}:{entity_id}"
        user_ids = await redis.smembers(viewing_key)

        if not user_ids:
            return {"users": [], "count": 0}

        # Получаем профили из presence ключей
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

        return {"users": users, "count": len(users)}

    except Exception as e:
        return {"users": [], "count": 0}
