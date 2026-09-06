"""
Redis cache module for TheFoxxStuff API.

Паттерны:
- Cache-Aside с защитой от Cache Stampede (asyncio.Lock)
- Батчинг счётчиков просмотров (30-секундный буфер)
- Rate limiting через Redis (корректно при 2+ воркерах)
- Graceful fallback — API работает если Redis недоступен
"""
import asyncio
import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis, ConnectionPool
from config import settings

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None
_redis: Optional[Redis] = None


async def init_cache() -> None:
    global _pool, _redis
    try:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=50,
            decode_responses=True,
        )
        _redis = Redis(connection_pool=_pool)
        await _redis.ping()
        logger.info("Redis connected: %s", settings.redis_url)
    except Exception as exc:
        logger.warning("Redis unavailable, caching disabled: %s", exc)
        _redis = None


async def close_cache() -> None:
    global _redis, _pool
    if _redis:
        await _redis.aclose()
    if _pool:
        await _pool.aclose()
    _redis = None
    _pool = None


def get_redis() -> Optional[Redis]:
    return _redis

def get_pool():
    """Возвращает ConnectionPool Redis для pub/sub subscriber-клиентов."""
    return _pool



# ─── Базовые хелперы ─────────────────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    """Вернуть десериализованное значение или None."""
    if _redis is None:
        return None
    try:
        raw = await _redis.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.debug("cache_get [%s]: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    """Сериализовать и сохранить значение с TTL (секунды)."""
    if _redis is None:
        return
    try:
        await _redis.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.debug("cache_set [%s]: %s", key, exc)


async def cache_delete(key: str) -> None:
    if _redis is None:
        return
    try:
        await _redis.delete(key)
    except Exception as exc:
        logger.debug("cache_delete [%s]: %s", key, exc)


async def cache_delete_pattern(pattern: str) -> int:
    """Удалить все ключи по паттерну. Возвращает кол-во удалённых."""
    if _redis is None:
        return 0
    try:
        keys = await _redis.keys(pattern)
        if keys:
            return await _redis.delete(*keys)
        return 0
    except Exception as exc:
        logger.debug("cache_delete_pattern [%s]: %s", pattern, exc)
        return 0


# ─── Защита от Cache Stampede ─────────────────────────────────────────────────
#
# FIX: раньше лок был обычным asyncio.Lock в словаре процесса — при 2+ воркерах
# (см. Dockerfile --workers 2) он защищал stampede только внутри своего процесса,
# а словарь ключей никогда не чистился (медленная утечка памяти). Теперь лок —
# в Redis (SET NX PX), общий для всех воркеров/реплик, с TTL — не течёт.

_STAMPEDE_LOCK_TTL_MS = 5000
_STAMPEDE_POLL_INTERVAL = 0.1
_STAMPEDE_MAX_WAIT = 5.0

async def cache_get_or_set(key: str, fetcher, ttl: int) -> Any:
    """
    Атомарный get-or-set: только один запрос идёт в DB при cache miss.
    Остальные ждут (poll) и получают результат из кэша, как только он появится.
    """
    cached = await cache_get(key)
    if cached is not None:
        return cached

    if _redis is None:
        return await fetcher()

    lock_key = f"lock:{key}"
    waited = 0.0
    while waited < _STAMPEDE_MAX_WAIT:
        try:
            acquired = await _redis.set(lock_key, "1", nx=True, px=_STAMPEDE_LOCK_TTL_MS)
        except Exception:
            # Redis недоступен — не блокируемся, просто идём в DB
            return await fetcher()

        if acquired:
            try:
                cached = await cache_get(key)
                if cached is not None:
                    return cached
                result = await fetcher()
                await cache_set(key, result, ttl)
                return result
            finally:
                try:
                    await _redis.delete(lock_key)
                except Exception:
                    pass

        # Кто-то другой уже считает — ждём и проверяем кэш
        await asyncio.sleep(_STAMPEDE_POLL_INTERVAL)
        waited += _STAMPEDE_POLL_INTERVAL
        cached = await cache_get(key)
        if cached is not None:
            return cached

    # Лок не отпустили за разумное время — не ждём вечно, считаем сами
    return await fetcher()


# ─── Батчинг счётчиков просмотров ────────────────────────────────────────────

VIEWS_BUFFER_TTL = 35  # чуть больше чем интервал flush (30s), страховка

async def increment_view_buffer(entity_type: str, entity_id: str) -> None:
    """
    Накапливает просмотры в Redis-буфере.
    Фоновая задача flush_view_buffers() сбрасывает их в MongoDB каждые 30 сек.
    Если Redis недоступен — просто пропускаем (views.py пишет напрямую).
    """
    if _redis is None:
        return
    key = f"views:buf:{entity_type}:{entity_id}"
    try:
        await _redis.incr(key)
        await _redis.expire(key, VIEWS_BUFFER_TTL)
    except Exception as exc:
        logger.debug("increment_view_buffer [%s:%s]: %s", entity_type, entity_id, exc)


async def flush_view_buffers(db) -> None:
    """
    Сбрасывает все накопленные счётчики из Redis в MongoDB одним батчем.
    Вызывается из фоновой задачи в lifespan.
    """
    if _redis is None:
        return
    try:
        keys = await _redis.keys("views:buf:*")
        if not keys:
            return

        pipe = _redis.pipeline()
        for key in keys:
            pipe.getdel(key)  # атомарно читаем и удаляем
        results = await pipe.execute()

        from datetime import datetime
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        for key, count_str in zip(keys, results):
            if not count_str:
                continue
            count = int(count_str)
            # views:buf:{entity_type}:{entity_id}
            parts = key.split(":", 3)
            if len(parts) != 4:
                continue
            _, _, entity_type, entity_id = parts

            # Обновляем view_records
            await db.view_records.update_one(
                {"entity_type": entity_type, "entity_id": entity_id, "date": today},
                {"$inc": {"count": count},
                 "$setOnInsert": {"entity_type": entity_type, "entity_id": entity_id, "date": today}},
                upsert=True,
            )
            # Обновляем daily_views
            await db.daily_views.update_one(
                {"entity_type": entity_type, "date": today},
                {"$inc": {"count": count},
                 "$setOnInsert": {"entity_type": entity_type, "date": today}},
                upsert=True,
            )
            # Обновляем счётчик на самом документе
            from bson import ObjectId
            collection_map = {"music": "music", "blog": "blog", "arts": "arts"}
            col = collection_map.get(entity_type)
            if col and ObjectId.is_valid(entity_id):
                await db[col].update_one(
                    {"_id": ObjectId(entity_id)},
                    {"$inc": {"views": count}},
                )

        logger.debug("Flushed %d view buffer keys to MongoDB", len(keys))
    except Exception as exc:
        logger.warning("flush_view_buffers error: %s", exc)


# ─── Rate limiting (Redis sliding window) ────────────────────────────────────

async def is_rate_limited(client_ip: str, limit: int = 120, window: int = 60) -> bool:
    """
    Sliding window rate limiter через Redis.
    Возвращает True если запрос нужно заблокировать.
    Fallback: False (разрешить) если Redis недоступен.
    """
    if _redis is None:
        return False
    key = f"rl:{client_ip}"
    try:
        pipe = _redis.pipeline()
        await pipe.incr(key)
        await pipe.expire(key, window)
        results = await pipe.execute()
        return results[0] > limit
    except Exception as exc:
        logger.debug("rate_limit [%s]: %s", client_ip, exc)
        return False
