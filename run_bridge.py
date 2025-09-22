"""Helper script to run the MIDI↔OSC bridge."""

from __future__ import annotations

import argparse
import asyncio

from mftd.bridge import MidiOscBridge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--osc-dst-host",
        default="127.0.0.1",
        help="OSC destination host (default: %(default)s)",
    )
    parser.add_argument(
        "--osc-dst-port",
        dest="osc_dst_ports",
        type=int,
        action="append",
        default=[9005],
        help=(
            "OSC destination port. Repeat the option to forward to multiple "
            "ports (default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--osc-src-host",
        default="127.0.0.1",
        help="OSC source host to listen on (default: %(default)s)",
    )
    parser.add_argument(
        "--osc-src-port",
        type=int,
        default=9006,
        help="OSC source port to listen on (default: %(default)s)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    osc_dst_ports = args.osc_dst_ports or [9005]

    bridge = MidiOscBridge(
        osc_dst_host=args.osc_dst_host,
        osc_dst_port=osc_dst_ports[0],
        osc_dst_ports=osc_dst_ports,
        osc_src_host=args.osc_src_host,
        osc_src_port=args.osc_src_port,
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
