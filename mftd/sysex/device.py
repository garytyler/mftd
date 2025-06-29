from dataclasses import field, asdict
from typing import ClassVar, Sequence
from typing import cast, Any

from mftd import constants
from mftd.constants import SysexBool, SideSwitchAction, MidiChannel, SysexCommands
from mftd.sysex.base import model
from mftd.sysex.mixins import FromSysexMixin, ToSysexMixin


@model
class DeviceConfig:
    system_midi_channel: MidiChannel = field(
        default=MidiChannel.SYSTEM,
        metadata={"addr": 0},
    )
    bank_side_buttons: SysexBool = field(
        default=SysexBool.TRUE,
        metadata={"addr": 1},
    )
    left_button_1_function: SideSwitchAction = field(
        default=SideSwitchAction.CC_HOLD,
        metadata={"addr": 2},
    )
    left_button_2_function: SideSwitchAction = field(
        default=SideSwitchAction.PREV_BANK,
        metadata={"addr": 3},
    )
    left_button_3_function: SideSwitchAction = field(
        default=SideSwitchAction.CC_HOLD,
        metadata={"addr": 4},
    )
    right_button_1_function: SideSwitchAction = field(
        default=SideSwitchAction.CC_HOLD,
        metadata={"addr": 5},
    )
    right_button_2_function: SideSwitchAction = field(
        default=SideSwitchAction.NEXT_BANK,
        metadata={"addr": 6},
    )
    right_button_3_function: SideSwitchAction = field(
        default=SideSwitchAction.CC_HOLD,
        metadata={"addr": 7},
    )
    super_knob_start: int = field(
        default=63,
        metadata={"addr": 8},
    )
    super_knob_end: int = field(
        default=127,
        metadata={"addr": 9},
    )
    rgb_led_brightness: int = field(
        default=127,
        metadata={"addr": 31},
    )
    indicator_global_brightness: int = field(
        default=127,
        metadata={"addr": 32},
    )


class DeviceConfigOut(DeviceConfig, ToSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommands.PUSH_CONF,
    )

    def _transform_sysex_out(self, field_name: str, value: Any) -> Any:
        if field_name == "system_midi_channel":
            return value + 1
        return value

    @classmethod
    def from_config(cls, config: DeviceConfig) -> "DeviceConfigOut":
        """Creates a DeviceConfigOut instance from a DeviceConfig."""
        # Cast to Any to bypass type checking for asdict
        return cls(**asdict(cast(Any, config)))


class DeviceConfigIn(DeviceConfig, FromSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        SysexCommands.PULL_CONF,
        0x01,
    )

    def to_config(self) -> "DeviceConfig":
        """Transforms a DeviceConfigIn instance to a DeviceConfig."""
        # Cast to Any to bypass type checking for asdict
        return DeviceConfig(**asdict(cast(Any, self)))
