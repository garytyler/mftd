from __future__ import annotations

from dataclasses import field, dataclass
from enum import IntEnum

from mftd.constants import (
    MidiChannel,
    SysexBool,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    Color,
    DetentColor,
    EncoderIndicatorDisplayType,
)
from .base import BaseModel


@dataclass
class EncoderConfig(BaseModel):
    detent: SysexBool = field(
        default=SysexBool.FALSE,
        metadata={"addr": 10},
    )
    movement_type: EncoderMovementType = field(
        default=EncoderMovementType.DIRECT_HIGH_RESOLUTION,
        metadata={"addr": 11},
    )
    switch_action_type: EncoderSwitchActionType = field(
        default=EncoderSwitchActionType.CC_HOLD,
        metadata={"addr": 12},
    )
    switch_midi_channel: MidiChannel = field(
        default=MidiChannel.SWITCH_AND_COLOR,
        metadata={"addr": 13},
    )
    switch_midi_number: int = field(
        default=1,
        metadata={"addr": 14},
    )
    # Addr 15 carries a -1 transform, so the model value is one above the wire
    # value.  A default of 0 emitted -1, which is not a legal SysEx data byte
    # and made rtmidi reject the whole encoder push.  1 emits the 0 that 2026
    # devices actually report.  The Utility never reads or writes this address.
    switch_midi_type: int = field(
        default=1,
        metadata={"addr": 15},
    )
    encoder_midi_channel: MidiChannel = field(
        default=MidiChannel.ROTARY_ENCODER,
        metadata={"addr": 16},
    )
    encoder_midi_number: int = field(
        default=1,
        metadata={"addr": 17},
    )
    encoder_midi_type: EncoderMidiMessageType = field(
        default=EncoderMidiMessageType.SEND_CC,
        metadata={"addr": 18},
    )
    active_color: Color = field(
        default=Color.DEFAULT_ACTIVE,
        metadata={"addr": 19},
    )
    inactive_color: Color = field(
        default=Color.DEFAULT_INACTIVE,
        metadata={"addr": 20},
    )
    detent_color: DetentColor = field(
        default=DetentColor.DEFAULT,
        metadata={"addr": 21},
    )
    indicator_display_type: EncoderIndicatorDisplayType = field(
        default=EncoderIndicatorDisplayType.BLENDED_BAR,
        metadata={"addr": 22},
    )
    is_super_knob: SysexBool = field(
        default=SysexBool.FALSE,
        metadata={"addr": 23},
    )
    encoder_shift_midi_channel: MidiChannel = field(
        default=MidiChannel.SHIFT,
        metadata={"addr": 24},
    )

    @property
    def index(self):
        return self.encoder_midi_number

    # All three channel fields are 1-16 on the wire and 0-15 in this model.
    # encoder_shift_midi_channel was previously sent untransformed, which put
    # shift rotation one channel below where it was asked for — writing
    # MidiChannel.SHIFT (4) landed it on channel 4 of 16, i.e. zero-indexed 3.
    # The Utility declares addr 24 as a 1-16 value defaulting to 5, the same
    # form as addrs 13 and 16.
    _CHANNEL_FIELDS = frozenset(
        {"encoder_midi_channel", "switch_midi_channel", "encoder_shift_midi_channel"}
    )

    def transform_outgoing(self, name: str, value: int | IntEnum):
        if name in self._CHANNEL_FIELDS:
            return value + 1
        elif name == "switch_midi_type":  # Appears no longer used
            return value - 1
        else:
            return value

    @classmethod
    def transform_incoming(cls, name: str, value: int | IntEnum):
        if name in cls._CHANNEL_FIELDS:
            return value - 1
        elif name == "switch_midi_type":  # Appears no longer used
            return value + 1
        else:
            return value
