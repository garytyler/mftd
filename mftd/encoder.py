from collections.abc import MutableMapping
from dataclasses import dataclass

from mftd.constants import (
    SysexBool,
    EncoderIndicatorDisplayType,
    ColorValue,
    DetentColorValue,
    EncoderMidiMessageType,
    EncoderMovementType,
    EncoderSwitchActionType,
    MidiChannel,
)


@dataclass
class EncoderConfig(MutableMapping):
    """Configuration values for a single encoder."""

    ADDRESSES_TO_NAMES = {
        10: "detent",
        11: "movement_type",
        12: "switch_action_type",
        13: "switch_midi_channel",
        14: "switch_midi_number",
        15: "switch_midi_type",
        16: "encoder_midi_channel",
        17: "encoder_midi_number",
        18: "encoder_midi_type",
        19: "active_color",
        20: "inactive_color",
        21: "detent_color",
        22: "indicator_display_type",
        23: "is_super_knob",
        24: "encoder_shift_midi_channel",
    }
    NAMES_TO_ADDRESSES = {name: addr for (addr, name) in ADDRESSES_TO_NAMES.items()}

    def __init__(
        self,
        midi_number: int,
        *,
        detent: bool | SysexBool = SysexBool.FALSE,
        movement_type: EncoderMovementType = EncoderMovementType.DIRECT_HIGH_RESOLUTION,
        switch_action_type: EncoderSwitchActionType = EncoderSwitchActionType.CC_HOLD,
        switch_midi_channel: MidiChannel = MidiChannel.SWITCH_AND_COLOR,
        # switch_midi_number: int = 1, # Set with `midi_number`
        switch_midi_type: int = 0,
        encoder_midi_channel: MidiChannel = MidiChannel.ROTARY_ENCODER,
        # encoder_midi_number: int = 1, # Set with `midi_number`
        encoder_midi_type: EncoderMidiMessageType = EncoderMidiMessageType.SEND_CC,
        active_color: ColorValue = ColorValue.DEFAULT_ACTIVE,
        inactive_color: ColorValue = ColorValue.DEFAULT_INACTIVE,
        detent_color: DetentColorValue = DetentColorValue.PINK,
        indicator_display_type: EncoderIndicatorDisplayType = EncoderIndicatorDisplayType.BLENDED_BAR,
        is_super_knob: bool | SysexBool = SysexBool.FALSE,
        encoder_shift_midi_channel: MidiChannel = MidiChannel.SHIFT,
    ):
        self.midi_number = midi_number
        self.detent = detent
        self.movement_type = movement_type
        self.switch_action_type = switch_action_type
        self.switch_midi_channel = switch_midi_channel
        self.encoder_midi_channel = encoder_midi_channel
        self.switch_midi_number = midi_number  # Set with `midi_number`
        self.switch_midi_type = switch_midi_type
        self.encoder_midi_channel = encoder_midi_channel
        self.encoder_midi_number = midi_number  # Set with `midi_number`
        self.encoder_midi_type = encoder_midi_type
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.detent_color = detent_color
        self.indicator_display_type = indicator_display_type
        self.is_super_knob = is_super_knob
        self.encoder_shift_midi_channel = encoder_shift_midi_channel

    @property
    def midi_number(self):
        return self._midi_number

    @midi_number.setter
    def midi_number(self, value):
        self._midi_number = int(value)
        self._encoder_midi_number = self._switch_midi_number = self._midi_number

    @property
    def detent(self):
        return self._detent

    @detent.setter
    def detent(self, value):
        self._detent = SysexBool(value)

    @property
    def movement_type(self):
        return self._movement_type

    @movement_type.setter
    def movement_type(self, value):
        self._movement_type = EncoderMovementType(value)

    @property
    def switch_action_type(self):
        return self._switch_action_type

    @switch_action_type.setter
    def switch_action_type(self, value):
        self._switch_action_type = EncoderSwitchActionType(value)

    @property
    def switch_midi_channel(self):
        return self._switch_midi_channel

    @switch_midi_channel.setter
    def switch_midi_channel(self, value):
        self._switch_midi_channel = MidiChannel(value)

    @property
    def switch_midi_number(self):
        return self._switch_midi_number

    @switch_midi_number.setter
    def switch_midi_number(self, value):
        self._midi_number = int(value)

    @property
    def switch_midi_type(self):
        return self._switch_midi_type

    @switch_midi_type.setter
    def switch_midi_type(self, value):
        self._switch_midi_type = int(value)

    @property
    def encoder_midi_channel(self):
        return self._encoder_midi_channel

    @encoder_midi_channel.setter
    def encoder_midi_channel(self, value):
        self._encoder_midi_channel = MidiChannel(value)

    @property
    def encoder_midi_number(self):
        return self._encoder_midi_number

    @encoder_midi_number.setter
    def encoder_midi_number(self, value):
        self._midi_number = int(value)

    @property
    def encoder_midi_type(self):
        return self._encoder_midi_type

    @encoder_midi_type.setter
    def encoder_midi_type(self, value):
        self._encoder_midi_type = EncoderMidiMessageType(value)

    @property
    def active_color(self):
        return self._active_color

    @active_color.setter
    def active_color(self, value):
        self._active_color = ColorValue(value)

    @property
    def inactive_color(self):
        return self._inactive_color

    @inactive_color.setter
    def inactive_color(self, value):
        self._inactive_color = ColorValue(value)

    @property
    def detent_color(self):
        return self._detent_color

    @detent_color.setter
    def detent_color(self, value):
        self._detent_color = DetentColorValue(value)

    @property
    def indicator_display_type(self):
        return self._indicator_display_type

    @indicator_display_type.setter
    def indicator_display_type(self, value):
        self._indicator_display_type = EncoderIndicatorDisplayType(value)

    @property
    def is_super_knob(self):
        return self._is_super_knob

    @is_super_knob.setter
    def is_super_knob(self, value):
        self._is_super_knob = SysexBool(value)

    @property
    def encoder_shift_midi_channel(self):
        return self._encoder_shift_midi_channel

    @encoder_shift_midi_channel.setter
    def encoder_shift_midi_channel(self, value):
        self._encoder_shift_midi_channel = MidiChannel(value)

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
