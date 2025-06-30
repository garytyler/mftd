from __future__ import annotations

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
            field_type = f.type
            try:
                if hasattr(field_type, "__origin__"):
                    continue
                if isinstance(field_type, type) and not isinstance(value, field_type):
                    setattr(self, f.name, field_type(value))
            except TypeError:
                continue

    def __setattr__(self, name, value):
        """Ensure that fields have the correct type when set using dot notation."""
        # Get the field if it exists
        field_obj = next((f for f in fields(self) if f.name == name), None)

        if field_obj is not None:
            field_type = field_obj.type
            try:
                # Skip generic types
                if hasattr(field_type, "__origin__"):
                    pass
                # Convert value to correct type if necessary
                elif isinstance(field_type, type) and not isinstance(value, field_type):
                    value = field_type(value)
            except TypeError:
                pass

        # Call the default __setattr__ with potentially converted value
        super().__setattr__(name, value)
