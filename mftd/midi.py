from __future__ import annotations

from typing import cast
import time

from mftd import MftSysexApi, DeviceConfig, EncoderConfig, constants
from mftd.protocol import MidiInput, MidiOutput


class TdMidiInput(MidiInput):
    """MidiInput wrapper for TouchDesigner."""

    def __init__(self, chop=None, event_dat=None) -> None:
        import td  # type: ignore

        self.chop = chop if chop else td.midiinCHOP
        self.event_dat = event_dat if event_dat else getattr(td, "midieventDAT", None)
        self.row = 0

    def get_port_count(self) -> int:  # pragma: no cover - TD only
        return 1

    def get_port_name(self, port: int) -> str:  # pragma: no cover - TD only
        if hasattr(self.chop, "name"):
            return self.chop.name
        return "midiinCHOP"

    def open_port(self, port: int) -> None:  # pragma: no cover - TD only
        self.row = 0

    def close_port(self) -> None:  # pragma: no cover - TD only
        pass

    def ignore_types(
        self, sysex: bool, timing: bool, active_sense: bool
    ) -> None:  # pragma: no cover - TD only
        pass

    def get_message(self):  # pragma: no cover - TD only
        if not self.event_dat:
            return None
        if self.row >= self.event_dat.numRows:
            return None
        try:
            cell = self.event_dat[self.row, "bytes"]
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


class MftApi:
    def __init__(
        self, midi_in: MidiInput | None = None, midi_out: MidiOutput | None = None
    ) -> None:
        print("MftApi initialized")
        self.midi_input = midi_in if midi_in else create_midi_input()
        self.midi_output = midi_out if midi_out else create_midi_output()

    def set_device_config(self, device_config: DeviceConfig) -> None:
        """Send the full device configuration to the MIDI device."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        MftSysexApi.set_device_config(
            midi_out=self.midi_output,
            config=device_config,
        )

    def get_device_config(self) -> DeviceConfig | None:
        """Request and return the current device configuration."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        if not self.midi_input:
            raise RuntimeError("MIDI input is not available.")
        MftSysexApi.get_device_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
        )

    def set_encoder_config(
        self, encoder_index: int, encoder_config: EncoderConfig
    ) -> None:
        """Send the full encoder configuration to the MIDI encoder."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        MftSysexApi.set_encoder_config(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            config=encoder_config,
        )

    def get_encoder_config(self, encoder_index) -> EncoderConfig:
        """Request and return the current encoder configuration."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        if not self.midi_input:
            raise RuntimeError("MIDI input is not available.")
        return MftSysexApi.get_encoder_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
            encoder_index=encoder_index,
        )

    def close(self):
        if hasattr(self, "midi_input"):
            self.midi_input.close_port()
        if hasattr(self, "midi_output"):
            self.midi_output.close_port()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()  # Fallback cleanup


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
