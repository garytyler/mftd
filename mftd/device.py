from dataclasses import field, dataclass, fields

from .constants import (
    MidiChannel,
    SysexBool,
    SideSwitchAction,
)


@dataclass
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

    def __post_init__(self):
        """Ensure that all fields have the correct type."""
        for f in fields(self):
            value = getattr(self, f.name)
            if not isinstance(value, f.type):
                setattr(self, f.name, f.type(value))


def _populate_class_attributes(cls):
    addr_map = {}
    name_map = {}
    for f in fields(cls):
        if "addr" in f.metadata:
            addr = f.metadata["addr"]
            name = f.name
            addr_map[addr] = name
            name_map[name] = addr
    cls.ADDRESSES_TO_NAMES = addr_map
    cls.NAMES_TO_ADDRESSES = name_map
    cls.ADDRESSES = list(addr_map.keys())
    cls.NAMES = list(name_map.keys())


_populate_class_attributes(DeviceConfig)
