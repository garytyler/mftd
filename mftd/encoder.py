from __future__ import annotations

from dataclasses import field, dataclass

from mftd.constants import (
    MidiChannel,
    SysexBool,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    ColorValue,
    DetentColorValue,
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
    switch_midi_type: int = field(
        default=0,
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
    active_color: ColorValue = field(
        default=ColorValue.DEFAULT_ACTIVE,
        metadata={"addr": 19},
    )
    inactive_color: ColorValue = field(
        default=ColorValue.DEFAULT_INACTIVE,
        metadata={"addr": 20},
    )
    detent_color: DetentColorValue = field(
        default=DetentColorValue.PINK,
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
