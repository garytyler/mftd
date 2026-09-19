from __future__ import annotations

from typing import Optional

from mftd.constants import (
    MidiChannel,
    EncoderRgbBrightness,
    EncoderIndicatorBrightness,
    EncoderAnimation,
)
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
    api = MftSysexApi

    def __init__(
        self,
        *,
        midi_in: Optional[MidiInput] = None,
        midi_out: Optional[MidiOutput] = None,
    ) -> None:
        self.midi_input = midi_in or create_midi_input()
        self.midi_output = midi_out or create_midi_output()

    def set_device_config(
        self,
        device_config: DeviceConfig,
    ) -> None:
        """Send the full device configuration to the MIDI device."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        self.api.set_device_config(
            midi_out=self.midi_output,
            data=device_config.to_out_dict(),
        )

    def set_encoder_config(
        self,
        encoder_index: int,
        encoder_config: EncoderConfig,
    ) -> None:
        """Send the full encoder configuration to the MIDI encoder."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        return self.api.set_encoder_config(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            data=encoder_config.to_out_dict(),
        )

    def get_device_config(
        self,
    ) -> DeviceConfig | None:
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
        resp = self.api.get_device_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
        )
        return DeviceConfig.from_in_dict(resp)

    def get_encoder_config(
        self,
        encoder_index: int,
    ) -> EncoderConfig:
        """Get the full encoder configuration from the MIDI encoder."""
        if not self.midi_output or not self.midi_input:
            if is_td_available():
                raise RuntimeError(
                    "get_device_config() is not supported in TouchDesigner."
                )
            elif not self.midi_output:
                raise RuntimeError("MIDI output is not available.")
            elif not self.midi_input:
                raise RuntimeError("MIDI input is not available.")
        resp = self.api.get_encoder_config(
            midi_out=self.midi_output,
            midi_in=self.midi_input,
            encoder_index=encoder_index,
        )
        return EncoderConfig.from_in_dict(resp)

    def set_encoder_value(
        self,
        encoder_index,
        value: int,
        channel: MidiChannel = MidiChannel.ROTARY_ENCODER,
    ):
        """Set an encoder value."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        return self.api.set_encoder_value(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            value=value,
            channel=channel,
        )

    def set_encoder_animation(
        self,
        encoder_index: int,
        value: EncoderAnimation,
        channel: MidiChannel = MidiChannel.ANIMATIONS_AND_BRIGHTNESS,
    ) -> None:
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        """Set an encoder animation or brightness value."""
        return self.api.set_encoder_animation_and_brightness(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            value=value,
            channel=channel,
        )

    def set_encoder_indicator_brightness(
        self,
        encoder_index: int,
        brightness: EncoderIndicatorBrightness,
        channel: MidiChannel = MidiChannel.ANIMATIONS_AND_BRIGHTNESS,
    ) -> None:
        """Set the indicator ring brightness for a single encoder."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        return self.api.set_encoder_animation_and_brightness(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            value=int(brightness),
            channel=channel,
        )

    def set_encoder_rgb_brightness(
        self,
        encoder_index: int,
        brightness: EncoderRgbBrightness,
        channel: MidiChannel = MidiChannel.ANIMATIONS_AND_BRIGHTNESS,
    ) -> None:
        """Set the RGB LED brightness for a single encoder."""
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")
        return self.api.set_encoder_animation_and_brightness(
            midi_out=self.midi_output,
            encoder_index=encoder_index,
            value=int(brightness),
            channel=channel,
        )

    def send_cc(
        self,
        cc: int,
        value: int,
        channel: int = 0,
    ) -> None:
        """
        Send a Control Change (CC) message to the device.

        Args:
            cc: CC number (0-127)
            value: CC value (0-127)
            channel: MIDI channel (0-15, default 0)
        """
        if not self.midi_output:
            raise RuntimeError("MIDI output is not available.")

        if not 0 <= channel <= 15:
            raise ValueError("channel must be in range 0-15")
        if not 0 <= cc <= 127:
            raise ValueError("cc must be in range 0-127")
        if not 0 <= value <= 127:
            raise ValueError("value must be in range 0-127")

        status = 0xB0 | (channel & 0x0F)
        message = [status, cc, value]
        self.midi_output.send_message(message)

    def close(self):
        midi_input = getattr(self, "midi_input", None)
        if midi_input:
            midi_input.close_port()
        midi_output = getattr(self, "midi_output", None)
        if midi_output:
            midi_output.close_port()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()  # Fallback cleanup
