from __future__ import annotations

from typing import cast

from mftd import MftSysexApi, DeviceConfig, EncoderConfig, constants
from mftd.protocol import MidiInput, MidiOutput


class MftApi:
    def __init__(
        self, midi_in: MidiInput | None = None, midi_out: MidiOutput | None = None
    ) -> None:
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

    def get_device_config(self) -> DeviceConfig:
        """Request and return the current device configuration."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        if not self.midi_input:
            raise RuntimeError("MIDI input is not available.")
        return MftSysexApi.get_device_config(
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
        import td

        return cast(MidiInput, td.midiinCHOP)
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
        import td

        return cast(MidiOutput, td.midioutCHOP)
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
