# run_bridge.py
import asyncio
from mftd.bridge import MidiOscBridge


async def main() -> None:
    bridge = MidiOscBridge(osc_dst_port=9005, osc_src_port=9006)
    print(
        f"Bridge running — MIDI CC → OSC on {bridge.midi_to_osc.osc_dst_host}:{bridge.midi_to_osc.osc_src_port}, "
        f"OSC CC → MIDI on {bridge.osc_to_midi.osc_src_host}:{bridge.osc_to_midi.osc_src_port}.\nPress Ctrl+C to stop."
    )

    try:
        await bridge.start()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bridge…")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
