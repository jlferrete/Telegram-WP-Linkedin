from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

import httpx

T = TypeVar("T")


@dataclass(frozen=True)
class RetryConfig:
    attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 4.0
    jitter_factor: float = 0.2


def is_retryable_exception(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError, httpx.WriteError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


def retry_call(
    fn: Callable[[], T],
    *,
    config: RetryConfig,
    should_retry: Callable[[Exception], bool],
    on_retry: Callable[[int, Exception, float], None] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> T:
    if config.attempts < 1:
        raise ValueError("Retry attempts must be >= 1")

    attempt = 1
    while True:
        try:
            return fn()
        except Exception as exc:
            if attempt >= config.attempts or not should_retry(exc):
                raise

            exponential = config.base_delay_seconds * (2 ** (attempt - 1))
            bounded = min(exponential, config.max_delay_seconds)
            jitter = bounded * config.jitter_factor * random.random()
            delay = bounded + jitter

            if on_retry is not None:
                on_retry(attempt, exc, delay)

            sleep_fn(delay)
            attempt += 1
