from __future__ import annotations

from typing import cast
import time

from mftd import constants
from mftd.protocol import MidiInput, MidiOutput


class TdMidiInput(MidiInput):
    """MidiInput wrapper for TouchDesigner."""

    midi_event_dat_name = "mftMidiEvent"
    midi_event_dat_type = "midieventDAT"

    def __init__(self, chop=None) -> None:
        import td  # type: ignore

        self.parent_op = op("/project1")
        self.midi_event_dat = self.parent_op.op(self.midi_event_dat_name)
        if not self.midi_event_dat:
            self.midi_event_dat = self.parent_op.create(
                self.midi_event_dat_type, self.midi_event_dat_name
            )
        self.row = 0

    def get_port_count(self) -> int:  # pragma: no cover - TD only
        return 1

    def get_port_name(self, port: int) -> str:  # pragma: no cover - TD only
        try:
            return self.midi_event_dat.name
        except Exception as exc:
            print(f"Error accessing MIDI event DAT name: {exc}")

    def open_port(self, port: int) -> None:  # pragma: no cover - TD only
        self.row = 0

    def close_port(self) -> None:  # pragma: no cover - TD only
        pass

    def ignore_types(
        self, sysex: bool, timing: bool, active_sense: bool
    ) -> None:  # pragma: no cover - TD only
        pass

    def get_message(self):  # pragma: no cover - TD only
        if not self.midi_event_dat:
            return None
        if self.row >= self.midi_event_dat.numRows:
            return None
        try:
            cell = self.midi_event_dat[self.row, "bytes"]
        except Exception as exc:
            print(f"Error accessing event_dat cell: {exc}")
            return None
        data = []
        if cell and getattr(cell, "val", None):
            for item in str(cell.val).split():
                try:
                    data.append(int(item, 0))
                except ValueError:
                    pass
        self.row += 1
        return data, time.time()


class TdMidiOutput(MidiOutput):
    """MidiOutput wrapper for TouchDesigner."""

    midi_out_chop_name = "mftMidiSystemOut"
    midi_out_chop_type = "midioutCHOP"

    def __init__(self, chop=None) -> None:
        import td  # type: ignore

        self.parent_op = op("/project1")
        self.midi_out_chop = self.parent_op.op(self.midi_out_chop_name)
        if not self.midi_out_chop:
            self.midi_out_chop = self.parent_op.create(
                self.midi_out_chop_type, self.midi_out_chop_name
            )

        self.chop = self.parent_op.op(self.midi_out_chop_name)
        print(self.chop)

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
        import rtmidi

        midi_in = rtmidi.MidiIn()

        # Auto-connect to device
        for i in range(midi_in.get_port_count()):
            if constants.DEVICE_NAME in midi_in.get_port_name(i):
                midi_in.open_port(i)
                midi_in.ignore_types(False, True, True)  # Don't ignore sysex
                break

        return cast(MidiInput, midi_in)
    elif is_td_available():
        print("Using TouchDesigner MIDI input")
        return TdMidiInput()
    return None


def create_midi_output() -> MidiOutput | None:
    """Create a MidiOutput instance that auto-connects to Midi Fighter Twister."""
    if is_rtmidi_available():
        import rtmidi

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
    except (ImportError, RuntimeError):
        return False


def is_td_available() -> bool:
    """Check if running in Touch Designer environment."""
    try:  # type: ignore
        import td  # type: ignore

        return True
    except ImportError:
        return False
