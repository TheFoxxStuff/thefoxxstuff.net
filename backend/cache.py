"""
Redis cache module for TheFoxxStuff API.
Provides simple async caching with automatic JSON serialization.
"""
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
            max_connections=10,
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


# ─── high-level helpers ───────────────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    """Return deserialized value or None."""
    if _redis is None:
        return None
    try:
        raw = await _redis.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.debug("cache_get error [%s]: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    """Serialize and store value with TTL (seconds)."""
    if _redis is None:
        return
    try:
        await _redis.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.debug("cache_set error [%s]: %s", key, exc)


async def cache_delete(key: str) -> None:
    if _redis is None:
        return
    try:
        await _redis.delete(key)
    except Exception as exc:
        logger.debug("cache_delete error [%s]: %s", key, exc)


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern. Returns count deleted."""
    if _redis is None:
        return 0
    try:
        keys = await _redis.keys(pattern)
        if keys:
            return await _redis.delete(*keys)
        return 0
    except Exception as exc:
        logger.debug("cache_delete_pattern error [%s]: %s", pattern, exc)
        return 0


# ─── rate limiting via Redis (replaces in-memory defaultdict) ────────────────

async def is_rate_limited(client_ip: str, limit: int = 120, window: int = 60) -> bool:
    """
    Sliding window rate limiter using Redis.
    Returns True if request should be blocked.
    Falls back to False (allow) when Redis is unavailable.
    """
    if _redis is None:
        return False
    key = f"rl:{client_ip}"
    try:
        pipe = _redis.pipeline()
        await pipe.incr(key)
        await pipe.expire(key, window)
        results = await pipe.execute()
        count = results[0]
        return count > limit
    except Exception as exc:
        logger.debug("rate_limit error [%s]: %s", client_ip, exc)
        return False
