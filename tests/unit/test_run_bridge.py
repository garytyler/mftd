import asyncio

import pytest

from run_bridge import start_bridge_with_retry


class DummyBridge:
    def __init__(self, failures: list[Exception]):
        self.failures = failures
        self.start_calls = 0
        self.stop_calls = 0

    async def start(self) -> None:
        self.start_calls += 1
        if self.failures:
            exc = self.failures.pop(0)
            if exc is not None:
                raise exc

    async def stop(self) -> None:
        self.stop_calls += 1


def test_start_bridge_with_retry_waits_for_midi(monkeypatch):
    bridge = DummyBridge([RuntimeError("MIDI input is not available."), None])
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    asyncio.run(start_bridge_with_retry(bridge, retry_delay=0.01))

    assert bridge.start_calls == 2
    assert bridge.stop_calls == 1
    assert sleep_calls == [0.01]


def test_start_bridge_with_retry_propagates_other_errors(monkeypatch):
    bridge = DummyBridge([RuntimeError("boom"), None])

    async def fake_sleep(delay: float) -> None:  # pragma: no cover - no retry expected
        raise AssertionError("sleep should not be called")

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(start_bridge_with_retry(bridge, retry_delay=0.01))

    assert bridge.start_calls == 1
    assert bridge.stop_calls == 1
