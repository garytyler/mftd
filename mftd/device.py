from __future__ import annotations

from dataclasses import field, dataclass
from enum import IntEnum

from .base import BaseModel
from .constants import (
    ColorMap,
    MidiChannel,
    SideSwitchAction,
    SleepAnimation,
    SleepTimer,
    SysexBool,
)


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
    # --- 2026 firmware additions (addrs 33-38) ---
    # Defaults below are the firmware's own, so a DeviceConfig() still
    # describes a factory device rather than imposing a house style.
    # Departs from the "defaults mirror the factory device" rule above, and
    # deliberately: Color's members are Expanded bytes, so a CLASSIC default
    # would make every named colour in the library select something else.
    color_map: ColorMap = field(
        default=ColorMap.EXPANDED,
        metadata={"addr": 33},
    )
    encoder_animation_channel: MidiChannel = field(
        default=MidiChannel.SWITCH_ANIMATION,
        metadata={"addr": 34},
    )
    button_animation_channel: MidiChannel = field(
        default=MidiChannel.ANIMATIONS_AND_BRIGHTNESS,
        metadata={"addr": 35},
    )
    sleep_timer: SleepTimer = field(
        default=SleepTimer.MIN_60,
        metadata={"addr": 36},
    )
    sleep_animation: SleepAnimation = field(
        default=SleepAnimation.RAINBOW_WAVE,
        metadata={"addr": 37},
    )
    bank_change_animations: SysexBool = field(
        default=SysexBool.TRUE,
        metadata={"addr": 38},
    )

    # Channel fields are 1-16 on the wire and 0-15 everywhere else, matching
    # how the Utility presents them.  A device reporting 6 on addr 34 is on
    # MidiChannel.SWITCH_ANIMATION (5).
    _CHANNEL_FIELDS = frozenset(
        {"system_midi_channel", "encoder_animation_channel", "button_animation_channel"}
    )

    def transform_outgoing(self, name: str, value: int | IntEnum):
        if name in self._CHANNEL_FIELDS:
            return value + 1
        else:
            return value

    @classmethod
    def transform_incoming(cls, name: str, value: int | IntEnum):
        if name in cls._CHANNEL_FIELDS:
            return value - 1
        else:
            return value
