from __future__ import annotations

from typing import Optional

from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.midi import (
    create_midi_input,
    create_midi_output,
    is_td_available,
)
from mftd.protocol import MidiInput, MidiOutput
from mftd.sysex import MftSysexApi


class MidiFighterTwister:
    def __init__(
        self,
        *,
        midi_in: Optional[MidiInput] = None,
        midi_out: Optional[MidiOutput] = None,
    ) -> None:
        self.midi_input = midi_in or create_midi_input()
        self.midi_output = midi_out or create_midi_output()

    def set_device_config(self, device_config: DeviceConfig) -> None:
        """Send the full device configuration to the MIDI device."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        MftSysexApi.set_device_config(
            midi_out=self.midi_output,
            config=device_config,
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

    def get_device_config(self) -> DeviceConfig | None:
        """Request and return the current device configuration."""
        if not self.midi_output or not self.midi_input:
            if is_td_available():
                raise RuntimeError(
                    "get_device_config() is not supported in TouchDesigner."
                )
            elif not self.midi_output:
                raise RuntimeError("MIDI output is not available.")
            elif not self.midi_input:
                raise RuntimeError("MIDI input is not available.")
        return MftSysexApi.get_device_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
        )

    def get_encoder_config(self, encoder_index) -> EncoderConfig:
        """Request and return the current encoder configuration."""
        if not self.midi_output or not self.midi_input:
            if is_td_available():
                raise RuntimeError(
                    "get_encoder_config() is not supported in TouchDesigner."
                )
            elif not self.midi_output:
                raise RuntimeError("MIDI output is not available.")
            elif not self.midi_input:
                raise RuntimeError("MIDI input is not available.")
        return MftSysexApi.get_encoder_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
            encoder_index=encoder_index,
        )

    def set_encoder_value(self, encoder_index, value: int):
        """Request and return the current encoder configuration."""
        if not self.midi_output or not self.midi_input:
            if is_td_available():
                raise RuntimeError(
                    "get_encoder_config() is not supported in TouchDesigner."
                )
            elif not self.midi_output:
                raise RuntimeError("MIDI output is not available.")
            elif not self.midi_input:
                raise RuntimeError("MIDI input is not available.")

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
