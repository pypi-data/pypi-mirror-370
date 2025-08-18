import pytest
import asyncio
from core_infinity_stones.core.utils import retry


def test_sync_retry_success_after_failures() -> None:
    attempts = {"count": 0}

    @retry(max_attempts=3, delay_in_seconds=0)
    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("Fail")
        return "Success"

    assert flaky() == "Success"
    assert attempts["count"] == 3


def test_sync_retry_raises_after_max_attempts() -> None:
    attempts = {"count": 0}

    @retry(max_attempts=2, delay_in_seconds=0)
    def always_fails() -> None:
        attempts["count"] += 1
        raise RuntimeError("Always fails")

    with pytest.raises(RuntimeError, match="Always fails"):
        always_fails()

    assert attempts["count"] == 2


async def test_async_retry_success_after_failures() -> None:
    attempts = {"count": 0}

    @retry(max_attempts=4, delay_in_seconds=0)
    async def async_flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 4:
            raise Exception("Temporary failure")
        return "OK"

    result = await async_flaky()
    assert result == "OK"
    assert attempts["count"] == 4


test_sync_retry_raises_after_max_attempts()
test_sync_retry_success_after_failures()
asyncio.run(test_async_retry_success_after_failures())