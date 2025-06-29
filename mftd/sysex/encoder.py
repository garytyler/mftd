from dataclasses import field
from typing import (
    ClassVar,
    Sequence,
)

from mftd import constants
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
from mftd.sysex.base import model
from mftd.sysex.mixins import FromSysexMixin, ToSysexMixin


@model
class EncoderConfig:
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


class EncoderConfigOut(ToSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommands.BULK_XFER,
        0x00,
    )

    _DATA_CLASS: ClassVar[type] = EncoderConfig

    def __init__(self, config: EncoderConfig):
        self.data = config


class EncoderConfigIn(FromSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (0x00, 0x01, 0x79, 0x03, 0x00)

    _DATA_CLASS: ClassVar[type] = EncoderConfig

    def __init__(self, config: EncoderConfig):
        self.data = config

    def to_config(self) -> EncoderConfig:
        return self.data
