from collections.abc import MutableMapping

from .constants import (
    MidiChannel,
    SysexBool,
    SideSwitchAction,
)


class DeviceConfig(MutableMapping):
    """Global configuration values for a Midi Fighter Twister."""

    ADDRESSES_TO_NAMES = {
        0: "system_midi_channel",
        1: "bank_side_buttons",
        2: "left_button_1_function",
        3: "left_button_2_function",
        4: "left_button_3_function",
        5: "right_button_1_function",
        6: "right_button_2_function",
        7: "right_button_3_function",
        8: "super_knob_start",
        9: "super_knob_end",
        31: "rgb_led_brightness",
        32: "indicator_global_brightness",
    }
    NAMES_TO_ADDRESSES = {name: addr for (addr, name) in ADDRESSES_TO_NAMES.items()}
    ADDRESSES = ADDRESSES_TO_NAMES.keys()
    NAMES = ADDRESSES_TO_NAMES.values()

    def __init__(
        self,
        *,
        system_midi_channel: MidiChannel = MidiChannel.SYSTEM,
        super_knob_start: int = 63,
        super_knob_end: int = 127,
        rgb_led_brightness: int = 127,
        indicator_global_brightness: int = 127,
        bank_side_buttons: SysexBool = SysexBool.TRUE,
        left_button_1_function: SideSwitchAction = SideSwitchAction.CC_HOLD,
        left_button_2_function: SideSwitchAction = SideSwitchAction.PREV_BANK,
        left_button_3_function: SideSwitchAction = SideSwitchAction.CC_HOLD,
        right_button_1_function: SideSwitchAction = SideSwitchAction.CC_HOLD,
        right_button_2_function: SideSwitchAction = SideSwitchAction.NEXT_BANK,
        right_button_3_function: SideSwitchAction = SideSwitchAction.CC_HOLD,
    ):
        self.system_midi_channel = system_midi_channel
        self.super_knob_start = super_knob_start
        self.super_knob_end = super_knob_end
        self.rgb_led_brightness = rgb_led_brightness
        self.indicator_global_brightness = indicator_global_brightness
        self.bank_side_buttons = bank_side_buttons
        self.left_button_1_function = left_button_1_function
        self.left_button_2_function = left_button_2_function
        self.left_button_3_function = left_button_3_function
        self.right_button_1_function = right_button_1_function
        self.right_button_2_function = right_button_2_function
        self.right_button_3_function = right_button_3_function

    @property
    def system_midi_channel(self):
        return self._system_midi_channel

    @system_midi_channel.setter
    def system_midi_channel(self, value):
        self._system_midi_channel = MidiChannel(value)

    @property
    def super_knob_start(self):
        return self._super_knob_start

    @super_knob_start.setter
    def super_knob_start(self, value):
        self._super_knob_start = int(value)

    @property
    def super_knob_end(self):
        return self._super_knob_end

    @super_knob_end.setter
    def super_knob_end(self, value):
        self._super_knob_end = int(value)

    @property
    def rgb_led_brightness(self):
        return self._rgb_led_brightness

    @rgb_led_brightness.setter
    def rgb_led_brightness(self, value):
        self._rgb_led_brightness = int(value)

    @property
    def indicator_global_brightness(self):
        return self._indicator_global_brightness

    @indicator_global_brightness.setter
    def indicator_global_brightness(self, value):
        self._indicator_global_brightness = int(value)

    @property
    def bank_side_buttons(self):
        return self._bank_side_buttons

    @bank_side_buttons.setter
    def bank_side_buttons(self, value):
        self._bank_side_buttons = SysexBool(value)

    @property
    def left_button_1_function(self):
        return self._left_button_1_function

    @left_button_1_function.setter
    def left_button_1_function(self, value):
        self._left_button_1_function = SideSwitchAction(value)

    @property
    def left_button_2_function(self):
        return self._left_button_2_function

    @left_button_2_function.setter
    def left_button_2_function(self, value):
        self._left_button_2_function = SideSwitchAction(value)

    @property
    def left_button_3_function(self):
        return self._left_button_3_function

    @left_button_3_function.setter
    def left_button_3_function(self, value):
        self._left_button_3_function = SideSwitchAction(value)

    @property
    def right_button_1_function(self):
        return self._right_button_1_function

    @right_button_1_function.setter
    def right_button_1_function(self, value):
        self._right_button_1_function = SideSwitchAction(value)

    @property
    def right_button_2_function(self):
        return self._right_button_2_function

    @right_button_2_function.setter
    def right_button_2_function(self, value):
        self._right_button_2_function = SideSwitchAction(value)

    @property
    def right_button_3_function(self):
        return self._right_button_3_function

    @right_button_3_function.setter
    def right_button_3_function(self, value):
        self._right_button_3_function = SideSwitchAction(value)

    def __getitem__(self, key: int | str):
        if isinstance(key, int):
            name = self.ADDRESSES_TO_NAMES[key]
        elif key in self.NAMES_TO_ADDRESSES:
            name = key
        else:
            raise KeyError(f"Invalid config property: {key}")
        return getattr(self, name)

    def __setitem__(self, key: int | str, value: int):
        if isinstance(key, int):
            name = self.ADDRESSES_TO_NAMES[key]
        elif key in self.NAMES_TO_ADDRESSES:
            name = key
        else:
            raise KeyError(f"Invalid config property: {key}")
        setattr(self, name, value)

    def __delitem__(self, key):
        raise NotImplementedError("Cannot delete config items")

    def __iter__(self):
        return iter(self.ADDRESSES_TO_NAMES)

    def __len__(self):
        return len(self.ADDRESSES_TO_NAMES)

    def __repr__(self):
        return str(dict(self))

    def __str__(self) -> str:
        lines = [f"{self.__class__.__name__}("]
        for addr, value in dict(self).items():
            name = self.ADDRESSES_TO_NAMES[addr]
            lines.append(f"{name}={repr(value)},")
        return "\n\t".join(lines) + "\n)"
