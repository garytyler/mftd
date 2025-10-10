"""Helper script to run the MIDI<->OSC bridge."""

from __future__ import annotations

import asyncio
import signal
import sys
from contextlib import suppress
from typing import Callable, Sequence

from mftd import (
    MidiChannel,
    MidiFighterTwister,
)
from mftd.bridge import MidiOscBridge
from run_config_init import MftConfigInitializer


class MessageRouter:
    basePort = 9000
    engineBasePort = 9010
    targetNumsToEncoderIndexes = {
        0: {10, 11, 14, 15},
        1: {0, 4, 8, 12},
        2: {1, 5, 9, 13},
        3: {2, 6},
        4: {3, 7},
    }
    encoderIndexesToTargetNums = {
        e: t for t, encoders in targetNumsToEncoderIndexes.items() for e in encoders
    }
    encoderChannels = [
        MidiChannel.ROTARY_ENCODER,
    ]

    encoderEngagementChannels = {
        MidiChannel.ROTARY_ENCODER,
        MidiChannel.SWITCH_AND_COLOR,
        MidiChannel.SHIFT,
    }

    @classmethod
    def getPort(cls, message) -> list[int] | int | None:
        channel, index, value = message
        if (
            channel in cls.encoderEngagementChannels
            and index in cls.encoderIndexesToTargetNums
        ):
            targetNum = cls.encoderIndexesToTargetNums[index]
            return [cls.basePort + targetNum, cls.engineBasePort + targetNum]
        elif channel == MidiChannel.SYSTEM:
            return [cls.basePort, cls.engineBasePort]
        return None

    @classmethod
    def getAddress(cls, message, address) -> str | None:
        return address


RETRYABLE_START_ERRORS: tuple[Callable[[Exception], bool], ...] = (
    lambda exc: isinstance(exc, RuntimeError)
    and "MIDI input is not available" in str(exc),
    lambda exc: isinstance(exc, RuntimeError)
    and "MIDI output is not available" in str(exc),
)


async def start_bridge_with_retry(
    bridge: MidiOscBridge, retry_delay: float = 2.0
) -> None:
    while True:
        try:
            await bridge.start()
        except Exception as exc:
            if any(check(exc) for check in RETRYABLE_START_ERRORS):
                print(
                    "MIDI device unavailable, retrying in",
                    f"{retry_delay:.1f}s...",
                    f"Error: {exc}",
                )
                await bridge.stop()
                await asyncio.sleep(retry_delay)
                continue
            await bridge.stop()
            raise
        else:
            break


READINESS_HOST = "127.0.0.1"
READINESS_PORT = 9090


class HttpReadinessProbe:
    _HTTP_READY_RESPONSE = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Length: 6\r\n"
        "Connection: close\r\n"
        "\r\n"
        "ready\n"
    ).encode("ascii")

    def __init__(self, host: str = READINESS_HOST, port: int = READINESS_PORT) -> None:
        self._host = host
        self._port = port
        self._server: asyncio.base_events.Server | None = None

    async def start(self) -> None:
        if self._server is not None:
            return

        self._server = await asyncio.start_server(
            self._handle_readiness_probe,
            host=self._host,
            port=self._port,
        )

    async def stop(self) -> None:
        if self._server is None:
            return

        self._server.close()
        with suppress(Exception):
            await self._server.wait_closed()
        self._server = None

    async def _handle_readiness_probe(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            try:
                await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=0.5)
            except (
                asyncio.IncompleteReadError,
                asyncio.LimitOverrunError,
                asyncio.TimeoutError,
            ):
                pass
            writer.write(self._HTTP_READY_RESPONSE)
            await writer.drain()
        finally:
            writer.close()
            with suppress(Exception):
                await writer.wait_closed()


async def run_bridge(argv: Sequence[str] | None = None):
    bridge = MidiOscBridge(
        osc_dst_host="127.0.0.1",
        osc_dst_ports=[9000, 9001, 9002, 9003, 9004] + [9010, 9011, 9012, 9013, 9014],
        osc_src_host="127.0.0.1",
        osc_src_port=9005,
        osc_address="/mftd/cc",
        osc_port_selector=MessageRouter.getPort,
        osc_addr_resolver=MessageRouter.getAddress,
    )

    osc_ports_desc = ", ".join(str(port) for port in bridge.midi_to_osc.osc_dst_ports)
    print(
        "Starting mftd bridge — MIDI CC → OSC on "
        f"{bridge.midi_to_osc.osc_dst_host}:{osc_ports_desc}, "
        "OSC CC → MIDI on "
        f"{bridge.osc_to_midi.osc_src_host}:{bridge.osc_to_midi.osc_src_port}."
    )

    readiness_probe = HttpReadinessProbe()
    stop_announced = False
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def request_shutdown() -> None:
        nonlocal stop_announced
        if stop_announced:
            return
        stop_announced = True
        print("\nStopping bridge…")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, request_shutdown)

    try:
        try:
            await start_bridge_with_retry(bridge)
        except asyncio.CancelledError:
            raise
        except OSError as exc:
            print(
                "Failed to start bridge due to unavailable port(s):",
                exc,
            )
            raise SystemExit(1) from exc
        except Exception as exc:
            print("Failed to start bridge:", exc)
            raise SystemExit(1) from exc

        try:
            await readiness_probe.start()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(
                "Failed to start readiness endpoint on",
                f"{READINESS_HOST}:{READINESS_PORT}",
                ":",
                exc,
            )
            raise SystemExit(1) from exc

        print("Bridge running. Press Ctrl+C to stop.")

        try:
            await stop_event.wait()
        except KeyboardInterrupt:
            request_shutdown()
        except asyncio.CancelledError:
            request_shutdown()
            raise
    except asyncio.CancelledError:
        request_shutdown()
        raise
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            with suppress(NotImplementedError):
                loop.remove_signal_handler(sig)
        await readiness_probe.stop()
        await bridge.stop()


def main(argv: Sequence[str] | None = None) -> None:
    with MidiFighterTwister() as mft:
        MftConfigInitializer(mft).configureDevice()

    try:
        asyncio.run(run_bridge(argv), debug=False)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(argv=sys.argv[1:])
