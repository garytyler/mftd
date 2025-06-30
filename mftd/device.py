from __future__ import annotations

from dataclasses import field, dataclass

from .base import BaseModel, BaseModelOut, BaseModelIn
from .constants import MidiChannel, SysexBool, SideSwitchAction


@dataclass
class DeviceConfig(BaseModel):
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


@dataclass
class DeviceConfigOut(DeviceConfig, BaseModelOut):
    pass


@dataclass
class DeviceConfigIn(DeviceConfig, BaseModelIn):
    pass
