from __future__ import annotations

import httpx
import pytest
from app.infra.retry import RetryConfig, is_retryable_exception, retry_call


def test_retry_call_retries_until_success() -> None:
    calls = {"count": 0}
    retries: list[tuple[int, float]] = []
    sleeps: list[float] = []

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            request = httpx.Request("GET", "https://example.com")
            response = httpx.Response(status_code=503, request=request)
            raise httpx.HTTPStatusError("temporary", request=request, response=response)
        return "ok"

    result = retry_call(
        flaky,
        config=RetryConfig(
            attempts=3,
            base_delay_seconds=0.0,
            max_delay_seconds=0.0,
            jitter_factor=0.0,
        ),
        should_retry=is_retryable_exception,
        on_retry=lambda attempt, _exc, delay: retries.append((attempt, delay)),
        sleep_fn=lambda delay: sleeps.append(delay),
    )

    assert result == "ok"
    assert calls["count"] == 3
    assert retries == [(1, 0.0), (2, 0.0)]
    assert sleeps == [0.0, 0.0]


def test_retry_call_does_not_retry_non_retryable_error() -> None:
    calls = {"count": 0}

    def not_retryable() -> None:
        calls["count"] += 1
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(status_code=400, request=request)
        raise httpx.HTTPStatusError("bad request", request=request, response=response)

    with pytest.raises(httpx.HTTPStatusError):
        retry_call(
            not_retryable,
            config=RetryConfig(attempts=3),
            should_retry=is_retryable_exception,
            sleep_fn=lambda _delay: None,
        )

    assert calls["count"] == 1


def test_retry_call_raises_when_attempts_invalid() -> None:
    with pytest.raises(ValueError, match="attempts"):
        retry_call(
            lambda: "ok",
            config=RetryConfig(attempts=0),
            should_retry=is_retryable_exception,
        )


def test_gga_smoke_exception_is_raised() -> None:
    with pytest.raises(RuntimeError, match="smoke"):
        raise RuntimeError("smoke")
