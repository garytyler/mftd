"""Helper script to run the MIDI↔OSC bridge."""

from __future__ import annotations

import asyncio

from mftd import MidiChannel
from mftd.bridge import MidiOscBridge


class MessageRouter:
    basePort = 9000
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

    @classmethod
    def getPort(cls, message) -> int | None:
        channel, port, value = message
        if (
            channel
            in [
                MidiChannel.ROTARY_ENCODER,
                MidiChannel.SWITCH_AND_COLOR,
                MidiChannel.SHIFT,
            ]
            and port in cls.encoderIndexesToTargetNums
        ):
            return cls.basePort + cls.encoderIndexesToTargetNums[port]
        elif channel == MidiChannel.SYSTEM:
            return cls.basePort
        else:
            return None


async def main() -> None:
    bridge = MidiOscBridge(
        osc_dst_host="127.0.0.1",
        osc_dst_ports=[9000, 9001, 9002, 9003, 9004],
        osc_src_host="127.0.0.1",
        osc_src_port=9005,
        osc_port_selector=MessageRouter.getPort,
    )

    osc_ports_desc = ", ".join(str(port) for port in bridge.midi_to_osc.osc_dst_ports)
    print(
        "Starting bridge — MIDI CC → OSC on "
        f"{bridge.midi_to_osc.osc_dst_host}:{osc_ports_desc}, "
        "OSC CC → MIDI on "
        f"{bridge.osc_to_midi.osc_src_host}:{bridge.osc_to_midi.osc_src_port}."
    )

    try:
        await bridge.start()
    except OSError as exc:
        await bridge.stop()
        print(
            "Failed to start bridge due to unavailable port(s):",
            exc,
        )
        raise SystemExit(1) from exc
    except Exception as exc:
        await bridge.stop()
        print("Failed to start bridge:", exc)
        raise SystemExit(1) from exc

    print("Bridge running. Press Ctrl+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bridge…")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
