"""Network helpers (retry / back-off) shared by OAuth modules."""

from __future__ import annotations

import random
import asyncio
from typing import Type

import httpx


class RetryPolicy:
    """Simple exponential back-off with optional jitter.

    Parameters
    ----------
    attempts:
        Total number of attempts **including** the first call. `attempts=3`
        means *1 original try + up to 2 retries*.
    backoff_base:
        Initial back-off in seconds for the first retry.
    backoff_factor:
        Multiplier applied for each subsequent retry (`base * factor ** n`).
    jitter:
        Randomised ±fraction applied to the computed back-off, expressed as a
        proportion of the back-off (0.1 = ±10 %).
    retry_exceptions:
        Tuple of exception classes considered retry-able.  Defaults to
        `httpx.TransportError` and `asyncio.TimeoutError`.
    """

    def __init__(
        self,
        *,
        attempts: int = 3,
        backoff_base: float = 0.5,
        backoff_factor: float = 2.0,
        jitter: float = 0.1,
        retry_exceptions: tuple[Type[BaseException], ...] | None = None,
    ) -> None:
        if attempts < 1:
            raise ValueError("attempts must be ≥ 1")
        self.attempts = attempts
        self.backoff_base = backoff_base
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = (
            retry_exceptions
            if retry_exceptions is not None
            else (httpx.TransportError, asyncio.TimeoutError)
        )

    def backoff(self, attempt_index: int) -> float:
        """Return back-off (seconds) *before* the given retry attempt."""
        base = self.backoff_base * (self.backoff_factor**attempt_index)
        if self.jitter:
            delta = base * self.jitter
            base += random.uniform(-delta, delta)
        return base

    async def sleep(self, attempt_index: int) -> None:
        await asyncio.sleep(self.backoff(attempt_index))

    def is_retryable(self, exc: BaseException) -> bool:
        return isinstance(exc, self.retry_exceptions)


# Default policy (3 attempts: 0.5s, 1s)
DEFAULT_RETRY_POLICY = RetryPolicy()

__all__ = ["RetryPolicy", "DEFAULT_RETRY_POLICY"]
