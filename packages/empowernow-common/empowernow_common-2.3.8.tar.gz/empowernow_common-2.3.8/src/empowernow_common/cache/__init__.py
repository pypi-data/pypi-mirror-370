"""Cache backend interfaces and implementations.

This module provides a lightweight async cache abstraction used by
security helpers (e.g. DPoP replay detection, Shared-Signals JTI replay
checks).

Two implementations are shipped out-of-the-box:
* ``InMemoryCacheBackend`` – process-local, best effort (tests / dev).
* ``RedisCacheBackend``    – production-ready, based on ``redis.asyncio``.

Both back-ends expose the same three coroutines:
* ``get(key)``      – return value or ``None``.
* ``set(key,value,ttl)`` – store value for *ttl* seconds.
* ``exists(key)``   – boolean existence check.

All values are stored **as JSON strings** for portability.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

__all__ = [
    "CacheBackend",
    "InMemoryCacheBackend",
    "RedisCacheBackend",
]


class CacheBackend(ABC):
    """Minimal async cache contract."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Return previously stored value or ``None`` if missing/expired."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Store *value* for *ttl* seconds (best-effort)."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return *True* if *key* exists and has not expired."""


class InMemoryCacheBackend(CacheBackend):
    """Non-thread-safe in-process cache – suitable for tests/dev only."""

    def __init__(self) -> None:
        # key -> (expires_at, json value)
        self._store: Dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, raw = item
        if expires_at < time.time():
            # expired – cleanup lazily
            self._store.pop(key, None)
            return None
        try:
            return json.loads(raw)
        except Exception:
            return raw  # fallback (already basic type)

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        expires_at = time.time() + max(ttl, 1)
        self._store[key] = (expires_at, json.dumps(value))

    async def exists(self, key: str) -> bool:
        item = self._store.get(key)
        if not item:
            return False
        expires_at, _ = item
        if expires_at < time.time():
            self._store.pop(key, None)
            return False
        return True


class RedisCacheBackend(CacheBackend):
    """Redis implementation suitable for multi-process / multi-host deployment.

    Uses ``redis.asyncio`` which is part of the official *redis* package ≥4.2.
    """

    def __init__(
        self,
        redis_client: "Redis",
        json_serializer: bool = True,
    ) -> None:
        # Lazy import to avoid mandatory redis dependency for users of InMemory backend
        from redis.asyncio import Redis  # type: ignore

        if not isinstance(redis_client, Redis):  # pragma: no cover – defensive
            raise TypeError("redis_client must be redis.asyncio.Redis instance")
        self._redis = redis_client
        self._json = json_serializer

    async def get(self, key: str) -> Optional[Any]:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        if self._json:
            try:
                return json.loads(raw)
            except Exception:
                return raw.decode() if isinstance(raw, (bytes, bytearray)) else raw
        return raw

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        data = json.dumps(value) if self._json else value
        await self._redis.set(key, data, ex=max(ttl, 1))

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(key) == 1
