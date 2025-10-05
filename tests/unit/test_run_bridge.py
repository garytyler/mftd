import asyncio
import socket

import pytest

import run_bridge
from run_bridge import main, start_bridge_with_retry


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


def _get_unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_main_exposes_readiness_probe(monkeypatch):
    async def exercise() -> None:
        start_event = asyncio.Event()
        stop_event = asyncio.Event()

        async def fake_start(self) -> None:  # type: ignore[override]
            start_event.set()

        async def fake_stop(self) -> None:  # type: ignore[override]
            stop_event.set()

        monkeypatch.setattr(run_bridge.MidiOscBridge, "start", fake_start)
        monkeypatch.setattr(run_bridge.MidiOscBridge, "stop", fake_stop)

        port = _get_unused_port()

        with pytest.raises(OSError):
            await asyncio.open_connection("127.0.0.1", port)

        main_task = asyncio.create_task(main(["--ready-tcp-port", str(port)]))

        await asyncio.wait_for(start_event.wait(), timeout=1)

        for _ in range(100):
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
            except OSError:
                await asyncio.sleep(0.01)
                continue
            try:
                data = await reader.readline()
            finally:
                writer.close()
                await writer.wait_closed()
            assert data == b"ready\n"
            break
        else:  # pragma: no cover - defensive
            pytest.fail("Readiness server did not accept connections")

        main_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await main_task

        await asyncio.wait_for(stop_event.wait(), timeout=1)

        for _ in range(10):
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
            except OSError:
                break
            else:
                writer.close()
                await writer.wait_closed()
                await asyncio.sleep(0.01)
        else:  # pragma: no cover - defensive
            pytest.fail("Readiness server still accepting connections after shutdown")

    asyncio.run(exercise())
