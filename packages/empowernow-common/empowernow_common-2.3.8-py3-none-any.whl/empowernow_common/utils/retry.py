"""Retry helpers built on :class:`empowernow_common.oauth.network.RetryPolicy`.

Two usage styles are supported:

1.  Functional helper::

        result = await with_retry(my_async_call,  arg1, arg2,
                                 retry_policy=RetryPolicy(attempts=5))

2.  Decorator::

        @retryable()
        async def fragile_io(...):
            ...

        # Custom policy
        @retryable(RetryPolicy(attempts=5, backoff_base=1.0))
        async def other():
            ...
"""

from __future__ import annotations

import functools
from typing import Any, Awaitable, Callable, TypeVar

from ..oauth.network import RetryPolicy, DEFAULT_RETRY_POLICY

T = TypeVar("T")

__all__ = ["with_retry", "retryable"]


async def with_retry(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    **kwargs: Any,
) -> T:
    """Run *func* with retry semantics from *retry_policy*."""

    for attempt in range(retry_policy.attempts):
        try:
            return await func(*args, **kwargs)
        except retry_policy.retry_exceptions as exc:
            if attempt >= retry_policy.attempts - 1:
                raise
            await retry_policy.sleep(attempt)

    # theoretically unreachable
    raise RuntimeError("retry logic exhausted without raising")


def retryable(policy: RetryPolicy = DEFAULT_RETRY_POLICY):
    """Decorator version of :pyfunc:`with_retry`."""

    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:  # type: ignore[override]
            return await with_retry(fn, *args, retry_policy=policy, **kwargs)

        return wrapper

    return decorator
