from __future__ import annotations

from typing import cast

from mftd import constants
from mftd.protocol import MidiInput, MidiOutput


class TdMidiOutput(MidiOutput):
    """MidiOutput wrapper for TouchDesigner."""

    midi_out_chop_name = "midiOut"
    midi_out_chop_type = "midioutCHOP"

    def __init__(self, midi_out_chop=None) -> None:
        if midi_out_chop:
            self.chop = midi_out_chop
        else:
            self.chop = me.parent().op(self.midi_out_chop_name)  # type: ignore[name-defined]  # noqa: F821

    def get_port_count(self) -> int:  # pragma: no cover - TD only
        return 1

    def get_port_name(self, port: int) -> str:  # pragma: no cover - TD only
        # if hasattr(self.chop, "name"):
        return self.chop.name

    def open_port(self, port: int) -> None:  # pragma: no cover - TD only
        pass

    def close_port(self) -> None:  # pragma: no cover - TD only
        pass

    def ignore_types(
        self, sysex: bool, timing: bool, active_sense: bool
    ) -> None:  # pragma: no cover - TD only
        pass

    def send_message(self, message):  # pragma: no cover - TD only
        try:
            self.chop.send(bytes(message))
        except Exception as exc:
            print("Failed to send message:", message)
            print(exc)
            pass


def create_midi_input() -> MidiInput | None:
    """Create a MidiInput instance that auto-connects to Midi Fighter Twister."""
    print("Creating MIDI input...")
    if is_rtmidi_available():
        import rtmidi  # type: ignore

        midi_in = rtmidi.MidiIn()

        # Auto-connect to device
        for i in range(midi_in.get_port_count()):
            if constants.DEVICE_NAME in midi_in.get_port_name(i):
                midi_in.open_port(i)
                midi_in.ignore_types(False)  # Don't ignore sysex
                break

        return cast(MidiInput, midi_in)
    elif is_td_available():
        return None
    return None


def create_midi_output() -> MidiOutput | None:
    """Create a MidiOutput instance that auto-connects to Midi Fighter Twister."""
    if is_rtmidi_available():
        import rtmidi  # type: ignore

        midi_out = rtmidi.MidiOut()

        # Auto-connect to device
        for i in range(midi_out.get_port_count()):
            if constants.DEVICE_NAME in midi_out.get_port_name(i):
                midi_out.open_port(i)
                break

        return cast(MidiOutput, midi_out)
    elif is_td_available():
        return TdMidiOutput()
    return None


def is_rtmidi_available() -> bool:
    """Check if rtmidi package is available."""
    try:  # type: ignore
        import rtmidi  # type: ignore

        # Test device creation to ensure rtmidi works
        rtmidi.MidiIn()
        return True
    except Exception:
        return False


def is_td_available() -> bool:
    """Check if running in Touch Designer environment."""
    try:  # type: ignore
        import td as _td  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False
