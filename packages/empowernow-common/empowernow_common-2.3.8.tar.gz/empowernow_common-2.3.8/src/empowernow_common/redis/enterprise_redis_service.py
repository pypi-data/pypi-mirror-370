"""
Enterprise Redis Service for empowernow_common.

Production-ready Redis service with connection pooling, circuit breakers,
health monitoring, and comprehensive error handling. Based on IdP redis_service.py
pattern but generalized for use across all empowernow services.
"""

import asyncio
import json
import logging
import os
import random
import time
import weakref
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Union

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Production-grade circuit breaker for Redis operations."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception

    failure_count: int = field(default=0, init=False)
    last_failure_time: float = field(default=0.0, init=False)
    state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.failure_count = 0
                else:
                    raise Exception("Circuit breaker is OPEN – short-circuiting call")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            return result
        except Exception as exc:
            is_expected = isinstance(exc, self.expected_exception)
            if is_expected:
                async with self._lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        self.state = CircuitState.OPEN
                        logger.error(
                            "Circuit breaker opened after %d failures (func=%s)",
                            self.failure_count,
                            func.__name__,
                            extra={"component": "redis", "circuit_state": "open"},
                        )
            raise


def retry_with_circuit_breaker(
    max_retries: int = 3,
    initial_backoff: float = 0.25,
    max_backoff: float = 2.0,
    backoff_factor: float = 2.0,
    circuit_breaker: Optional[CircuitBreaker] = None,
):
    """Decorator combining circuit-breaker and exponential backoff."""
    if circuit_breaker is None:
        circuit_breaker = CircuitBreaker()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            backoff = initial_backoff
            for attempt in range(max_retries):
                try:
                    return await circuit_breaker.call(func, *args, **kwargs)
                except Exception as exc:
                    if (
                        attempt == max_retries - 1
                        or circuit_breaker.state == CircuitState.OPEN
                    ):
                        raise
                    jitter = backoff * random.uniform(0, 0.1)
                    await asyncio.sleep(backoff + jitter)
                    backoff = min(backoff * backoff_factor, max_backoff)
        return wrapper
    return decorator


def handle_redis_errors(default_value=None):
    """Decorator that handles Redis errors gracefully."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(
                    "Redis operation failed, using fallback: %s",
                    str(e),
                    extra={"operation": func.__name__, "using_fallback": True},
                )
                return default_value
            except Exception as e:
                logger.error(
                    "Unexpected Redis error: %s",
                    str(e),
                    extra={"operation": func.__name__, "error_type": type(e).__name__},
                )
                return default_value
        return wrapper
    return decorator


class EnterpriseRedisService:
    """
    Enterprise-grade Redis service with connection pooling and circuit breakers.
    
    Features:
    - Per-event-loop connection pooling
    - Circuit breaker protection
    - Exponential backoff retry logic  
    - Health monitoring and metrics
    - Graceful error handling
    - FIPS-compliant operation
    """

    # Per-event-loop connection management
    _pools: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, redis.ConnectionPool]" = (
        weakref.WeakKeyDictionary()
    )
    _clients: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, redis.Redis]" = (
        weakref.WeakKeyDictionary()
    )
    _locks: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock]" = (
        weakref.WeakKeyDictionary()
    )
    _init_lock: Optional[asyncio.Lock] = None

    # Global circuit breaker
    _circuit_breaker = CircuitBreaker()

    def __init__(self, redis_url: str, max_connections: int = 20, key_prefix: str = ""):
        """
        Initialize enterprise Redis service.
        
        Args:
            redis_url: Redis connection URL
            max_connections: Maximum connections in pool
            key_prefix: Optional key prefix for namespacing
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not available - install with: pip install redis")
        
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.key_prefix = key_prefix

    async def get_redis(self, force_reconnect: bool = False) -> redis.Redis:
        """Get or create Redis client with per-loop pooling."""
        loop = asyncio.get_running_loop()

        # Initialize per-loop lock
        init_lock = self._init_lock
        if init_lock is None:
            init_lock = asyncio.Lock()
            self._init_lock = init_lock

        async with init_lock:
            lock = self._locks.get(loop)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[loop] = lock

        async with lock:
            if loop not in self._pools or loop not in self._clients or force_reconnect:
                if force_reconnect and (loop in self._pools or loop in self._clients):
                    logger.info("Forcing Redis reconnection for current event loop")
                    try:
                        if loop in self._clients:
                            await self._clients[loop].close()
                        if loop in self._pools:
                            await self._pools[loop].disconnect()
                    except Exception as e:
                        logger.warning("Error closing existing Redis connection: %s", str(e))

                    self._pools.pop(loop, None)
                    self._clients.pop(loop, None)

                logger.info("Connecting to Redis at %s", self.redis_url)

                try:
                    self._pools[loop] = redis.ConnectionPool.from_url(
                        self.redis_url,
                        max_connections=self.max_connections,
                        decode_responses=True,
                        health_check_interval=5,
                        socket_connect_timeout=float(os.environ.get("REDIS_SOCKET_CONNECT_TIMEOUT", "5")),
                        socket_keepalive=True,
                        retry_on_timeout=True,
                    )

                    self._clients[loop] = redis.Redis(connection_pool=self._pools[loop])

                    # Test connection
                    ping_timeout = float(os.environ.get("REDIS_PING_TIMEOUT", "6"))
                    ping_task = self._clients[loop].ping()
                    ping_success = await asyncio.wait_for(ping_task, timeout=ping_timeout)

                    if ping_success:
                        logger.info("Connected to Redis at %s", self.redis_url)
                    else:
                        raise Exception("Redis connection check failed")

                except Exception as e:
                    logger.error("Failed to connect to Redis: %s", str(e))
                    if loop in self._clients:
                        try:
                            await self._clients[loop].close()
                        except Exception:
                            pass
                        self._clients.pop(loop, None)

                    if loop in self._pools:
                        try:
                            await self._pools[loop].disconnect()
                        except Exception:
                            pass
                        self._pools.pop(loop, None)
                    raise

        return self._clients[loop]

    def _make_key(self, key: str) -> str:
        """Create prefixed Redis key."""
        return f"{self.key_prefix}{key}" if self.key_prefix else key

    @retry_with_circuit_breaker()
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with JSON parsing."""
        try:
            redis_client = await self.get_redis()
            value = await redis_client.get(self._make_key(key))

            if value is None:
                return None

            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value  # Return raw value if not JSON
        except Exception as e:
            logger.error(
                "Redis get error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "get",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return None

    @retry_with_circuit_breaker()
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL."""
        try:
            redis_client = await self.get_redis()

            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)

            # Set with or without TTL
            if ttl:
                result = await redis_client.setex(self._make_key(key), ttl, serialized_value)
            else:
                result = await redis_client.set(self._make_key(key), serialized_value)
                
            return bool(result)
        except Exception as e:
            logger.error(
                "Redis set error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "set",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    @retry_with_circuit_breaker()
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            redis_client = await self.get_redis()
            result = await redis_client.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(
                "Redis delete error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "delete",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    @retry_with_circuit_breaker()
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            redis_client = await self.get_redis()
            result = await redis_client.exists(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(
                "Redis exists error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "exists",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    @retry_with_circuit_breaker()
    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Set key with expiration time."""
        try:
            redis_client = await self.get_redis()
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
                
            result = await redis_client.setex(self._make_key(key), ttl, serialized_value)
            return bool(result)
        except Exception as e:
            logger.error(
                "Redis setex error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "setex",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    @retry_with_circuit_breaker()
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for existing key."""
        try:
            redis_client = await self.get_redis()
            result = await redis_client.expire(self._make_key(key), ttl)
            return bool(result)
        except Exception as e:
            logger.error(
                "Redis expire error: %s",
                str(e),
                extra={
                    "component": "redis",
                    "operation": "expire",
                    "key": key,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return False

    async def ping(self) -> bool:
        """Ping Redis server."""
        try:
            redis_client = await self.get_redis()
            result = await redis_client.ping()
            return bool(result)
        except Exception as e:
            logger.error("Redis ping error: %s", str(e))
            return False

    async def health_check(self, timeout: float = 1.0) -> Dict[str, Any]:
        """Comprehensive health check."""
        result = {
            "status": "unhealthy",
            "latency_ms": 0,
            "last_checked": datetime.now(UTC).isoformat(),
            "circuit_state": self._circuit_breaker.state.value,
            "error": None,
        }

        try:
            redis_client = await asyncio.wait_for(self.get_redis(), timeout=timeout)
            
            start_time = time.perf_counter()
            await redis_client.ping()
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            result.update({
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "error": None
            })

        except asyncio.TimeoutError:
            result.update({
                "error": "Connection timed out",
                "error_type": "TimeoutError"
            })
        except Exception as e:
            result.update({
                "error": str(e),
                "error_type": type(e).__name__
            })

        return result

    @classmethod
    async def close_all(cls):
        """Close all Redis connections."""
        for loop, client in list(cls._clients.items()):
            try:
                await client.close()
            finally:
                cls._clients.pop(loop, None)

        for loop, pool in list(cls._pools.items()):
            try:
                await pool.disconnect()
            finally:
                cls._pools.pop(loop, None)

        logger.info("Closed all Redis clients & pools")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        loop = asyncio.get_running_loop()
        pool = self._pools.get(loop)
        if pool is None:
            return {"status": "no_pool"}

        try:
            return {
                "max_connections": pool.max_connections,
                "created_connections": len(pool._created_connections),
                "available_connections": len(pool._available_connections),
                "in_use_connections": len(pool._in_use_connections),
                "status": "healthy" if pool._available_connections else "exhausted",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


def create_redis_service(
    redis_url: Optional[str] = None, 
    max_connections: int = 20,
    key_prefix: str = ""
) -> EnterpriseRedisService:
    """
    Factory function to create Redis service with environment configuration.
    
    Args:
        redis_url: Redis URL (defaults to REDIS_URL env var)
        max_connections: Max connections in pool
        key_prefix: Key prefix for namespacing
        
    Returns:
        Configured EnterpriseRedisService
    """
    if redis_url is None:
        redis_url = (
            os.environ.get("REDIS__URL") or
            os.environ.get("REDIS_URL") or
            os.environ.get("REDIS_CONNECTION_URL")
        )
    
    if not redis_url:
        raise ValueError(
            "Redis URL not configured. Set REDIS_URL environment variable or pass redis_url parameter."
        )
    
    return EnterpriseRedisService(
        redis_url=redis_url,
        max_connections=max_connections, 
        key_prefix=key_prefix
    )