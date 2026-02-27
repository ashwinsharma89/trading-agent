"""
Redis cache with in-memory fallback.
"""
import json
import logging
from datetime import timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import redis; fall back to in-memory dict if unavailable
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed – using in-memory cache")

_memory_store: dict[str, tuple[Any, float]] = {}


class CacheClient:
    def __init__(self, redis_url: str, default_ttl: int = 900):
        self._url = redis_url
        self._default_ttl = default_ttl
        self._redis: Optional[Any] = None

    async def connect(self):
        if not REDIS_AVAILABLE:
            return
        try:
            self._redis = aioredis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}) – using in-memory cache")
            self._redis = None

    async def get(self, key: str) -> Optional[Any]:
        if self._redis:
            try:
                raw = await self._redis.get(key)
                if raw:
                    return json.loads(raw)
                return None
            except Exception:
                pass

        # In-memory fallback
        import time
        if key in _memory_store:
            value, expires_at = _memory_store[key]
            if expires_at == 0 or time.time() < expires_at:
                return value
            del _memory_store[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self._default_ttl
        raw = json.dumps(value, default=str)

        if self._redis:
            try:
                await self._redis.setex(key, ttl, raw)
                return
            except Exception:
                pass

        # In-memory fallback
        import time
        expires_at = time.time() + ttl if ttl else 0
        _memory_store[key] = (json.loads(raw), expires_at)

    async def delete(self, key: str) -> None:
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        _memory_store.pop(key, None)

    async def exists(self, key: str) -> bool:
        cached = await self.get(key)
        return cached is not None

    async def close(self):
        if self._redis:
            await self._redis.aclose()


# Module-level singleton – initialised in app lifespan
_cache: Optional[CacheClient] = None


def get_cache() -> CacheClient:
    if _cache is None:
        raise RuntimeError("Cache not initialised – call init_cache() first")
    return _cache


async def init_cache(redis_url: str, default_ttl: int = 900) -> CacheClient:
    global _cache
    _cache = CacheClient(redis_url, default_ttl)
    await _cache.connect()
    return _cache
