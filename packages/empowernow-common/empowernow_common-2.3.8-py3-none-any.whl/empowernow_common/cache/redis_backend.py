"""Redis-backed implementation of :pyclass:`~empowernow_common.cache.CacheBackend`.

Requires `redis>=4.3` (official redis-py) which ships an optional *asyncio*
interface.  The backend is *optional* – gracefully degrades if the dependency
is absent or Redis is unreachable.
"""

from __future__ import annotations

import time
from typing import Generic, TypeVar, Optional, Any

from . import CacheBackend

try:
    import redis.asyncio as aioredis  # type: ignore
except ImportError:  # pragma: no cover – optional
    aioredis = None  # type: ignore

T = TypeVar("T")


class RedisCacheBackend(CacheBackend[T], Generic[T]):
    """Redis cache with per-key TTL using *redis.asyncio.Redis*.

    Parameters
    ----------
    redis_url:
        e.g. ``redis://localhost:6379/0``.  If *None* the backend is disabled
        and behaves like an empty cache (all operations are no-ops).
    prefix:
        Optional key prefix to avoid collisions when the same Redis instance is
        shared across applications.
    """

    def __init__(
        self, redis_url: str | None = None, *, prefix: str = "encache:"
    ) -> None:
        self._enabled = bool(redis_url and aioredis)
        self._prefix = prefix
        self._redis: Optional[aioredis.Redis] = (
            aioredis.from_url(redis_url, encoding="utf-8", decode_responses=False)
            if self._enabled
            else None
        )

    # Utility -------------------------------------------------------------

    def _mk(self, key: str) -> str:
        return f"{self._prefix}{key}"

    # CacheBackend interface ---------------------------------------------

    def get(self, key: str) -> Optional[T]:
        if not self._enabled or not self._redis:
            return None
        raw = self._redis.get(self._mk(key))  # async coroutine
        # return await raw
        import anyio

        data: Optional[bytes] = anyio.run(lambda: raw)
        if data is None:
            return None
        import pickle

        return pickle.loads(data)  # type: ignore[arg-type]

    def set(self, key: str, value: T, ttl: int) -> None:
        if not self._enabled or not self._redis:
            return
        import pickle, anyio

        payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        anyio.run(lambda: self._redis.set(self._mk(key), payload, ex=ttl))

    def delete(self, key: str) -> None:
        if not self._enabled or not self._redis:
            return
        import anyio

        anyio.run(lambda: self._redis.delete(self._mk(key)))

    def clear(self) -> None:
        if not self._enabled or not self._redis:
            return
        import anyio

        async def _wipe() -> None:
            async for k in self._redis.scan_iter(f"{self._prefix}*"):
                await self._redis.delete(k)

        anyio.run(_wipe)

    def setex(self, key: str, time: int, value: T) -> None:
        """Set key with expiration time in seconds."""
        if not self._enabled or not self._redis:
            return
        import pickle, anyio
        
        payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        anyio.run(lambda: self._redis.setex(self._mk(key), time, payload))

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._enabled or not self._redis:
            return False
        import anyio
        
        return bool(anyio.run(lambda: self._redis.exists(self._mk(key))))

    def expire(self, key: str, time: int) -> bool:
        """Set expiration time for existing key."""
        if not self._enabled or not self._redis:
            return False
        import anyio
        
        return bool(anyio.run(lambda: self._redis.expire(self._mk(key), time)))

    def ping(self) -> bool:
        """Ping Redis server to test connectivity."""
        if not self._enabled or not self._redis:
            return False
        import anyio
        
        try:
            result = anyio.run(lambda: self._redis.ping())
            return bool(result)
        except Exception:
            return False


__all__: list[str] = ["RedisCacheBackend"]
