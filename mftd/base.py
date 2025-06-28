"""
sysex_models.py – minimal std-lib “Pydantic-lite” helpers and the
DeviceConfig models (internal / out / in) for a MIDI Fighter Twister-style
controller.  Requires Python ≥ 3.11.
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field as dc_field, fields
from enum import IntEnum
from typing import (
    Any,
    ClassVar,
    Mapping,
    Sequence,
    TypeVar,
    dataclass_transform,
    get_type_hints,
    cast,
    Protocol,
)

from mftd import constants
from mftd.constants import (
    MidiChannel,
    SysexBool,
    SideSwitchAction,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    ColorValue,
    DetentColorValue,
    EncoderIndicatorDisplayType,
)

Self = TypeVar("Self", bound="FromSysexProtocol")


class FromSysexProtocol(Protocol):
    """Protocol defining the structure required by FromSysexMixin."""

    _HEADER: ClassVar[Sequence[int]]
    _MAP: ClassVar[Mapping[int, str]]


# ──────────────────────────────────────────────────────────────────
# 1.  decorator  (PEP-681 – tells mypy this behaves like @dataclass)
# ──────────────────────────────────────────────────────────────────
@dataclass_transform(frozen_default=True)
def model(_cls=None, **dc_kwargs):
    """Turn a plain class into @dataclass(frozen=True, slots=True)."""

    def wrap(cls):
        return dataclass(frozen=True, slots=True, **dc_kwargs)(cls)

    return wrap(_cls) if _cls else wrap


# ──────────────────────────────────────────────────────────────────
# 2.  Mixins
# ──────────────────────────────────────────────────────────────────
class _ValidateMixin:
    """Runtime type checking + 0–127 guard for any int / IntEnum fields."""

    def __post_init__(self) -> None:
        hints = get_type_hints(self.__class__)
        for fld in fields(cast(Any, self)):
            val: Any = getattr(self, fld.name)
            exp = hints.get(fld.name, Any)

            # Static-type check
            if exp is not Any and not isinstance(val, exp):
                raise TypeError(f"{fld.name}={val!r} is not {exp}")

            # Range check for int / IntEnum
            as_int = int(val) if isinstance(val, IntEnum) else val
            if isinstance(as_int, int) and not 0 <= as_int <= 0x7F:
                raise ValueError(f"{fld.name}={as_int} is outside 0-127")


class ToSysexMixin:
    """Adds .to_sysex() that returns list[int] (SysEx packet)."""

    _HEADER: ClassVar[Sequence[int]]  # must start with 0xF0

    def _addr_val_pairs(self) -> list[int]:
        out: list[int] = []
        for fld in fields(cast(Any, self)):
            addr = fld.metadata.get("addr")
            if addr is None:
                continue
            val: int = int(getattr(self, fld.name))
            if not (0 <= addr <= 0x7F and 0 <= val <= 0x7F):
                raise ValueError(f"{fld.name}: addr/val must be 0-127")
            out.extend((addr, val))
        return out

    def to_sysex(self) -> list[list[int]]:
        """Full SysEx message ready for MidiOut.send_message()."""
        pairs: list[int] = self._addr_val_pairs()
        header = list(self._HEADER)
        result: list[list[int]] = []
        payload = header.copy()
        for i in range(0, len(pairs), 2):
            if len(payload) - len(header) + 2 > constants.PART_SIZE_BYTES:
                payload.append(0xF7)
                result.append(payload)
                payload = header.copy()
            payload.extend(pairs[i : i + 2])

        if len(payload) > len(header):
            payload.append(0xF7)
            result.append(payload)
        return result


class FromSysexMixin:
    """cls.from_sysex(pkt) → model instance."""

    _HEADER: ClassVar[Sequence[int]]  # **without** leading 0xF0
    _MAP: ClassVar[Mapping[int, str]]  # {addr → field_name}

    @classmethod
    def from_sysex(cls: type[Self], pkt: Sequence[int]) -> Self:
        if len(pkt) < 3 or pkt[0] != 0xF0 or pkt[-1] != 0xF7:
            raise ValueError("not a SysEx packet")
        if list(pkt[1 : 1 + len(cls._HEADER)]) != list(cls._HEADER):
            raise ValueError("header mismatch")

        body = pkt[1 + len(cls._HEADER) : -1]
        if len(body) % 2:
            raise ValueError("addr/val pairs must be even length")

        it = iter(body)
        kwargs: dict[str, int] = {
            cls._MAP[addr]: val for addr, val in zip(it, it) if addr in cls._MAP
        }
        missing = set(cls._MAP.values()) - kwargs.keys()
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")

        return cls(**kwargs)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────
# 3.  INTERNAL model – your business object
# ──────────────────────────────────────────────────────────────────
@model
class DeviceConfig(_ValidateMixin):
    system_midi_channel: MidiChannel = MidiChannel.SYSTEM
    super_knob_start: int = 63
    super_knob_end: int = 127
    rgb_led_brightness: int = 127
    indicator_global_brightness: int = 127
    bank_side_buttons: SysexBool = SysexBool.TRUE
    left_button_1_function: SideSwitchAction = SideSwitchAction.CC_HOLD
    left_button_2_function: SideSwitchAction = SideSwitchAction.PREV_BANK
    left_button_3_function: SideSwitchAction = SideSwitchAction.CC_HOLD
    right_button_1_function: SideSwitchAction = SideSwitchAction.CC_HOLD
    right_button_2_function: SideSwitchAction = SideSwitchAction.NEXT_BANK
    right_button_3_function: SideSwitchAction = SideSwitchAction.CC_HOLD


# ──────────────────────────────────────────────────────────────────
# 4.  OUT model – serialises to SysEx
# ──────────────────────────────────────────────────────────────────
@model
class DeviceConfigOut(DeviceConfig, ToSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommands.PUSH_CONF,
    )

    system_midi_channel: MidiChannel = dc_field(metadata={"addr": 0})
    bank_side_buttons: SysexBool = dc_field(metadata={"addr": 1})
    left_button_1_function: SideSwitchAction = dc_field(metadata={"addr": 2})
    left_button_2_function: SideSwitchAction = dc_field(metadata={"addr": 3})
    left_button_3_function: SideSwitchAction = dc_field(metadata={"addr": 4})
    right_button_1_function: SideSwitchAction = dc_field(metadata={"addr": 5})
    right_button_2_function: SideSwitchAction = dc_field(metadata={"addr": 6})
    right_button_3_function: SideSwitchAction = dc_field(metadata={"addr": 7})
    super_knob_start: int = dc_field(metadata={"addr": 8})
    super_knob_end: int = dc_field(metadata={"addr": 9})
    rgb_led_brightness: int = dc_field(metadata={"addr": 31})
    indicator_global_brightness: int = dc_field(metadata={"addr": 32})


# ──────────────────────────────────────────────────────────────────
# 5.  IN model – parses SysEx into DeviceConfig
# ──────────────────────────────────────────────────────────────────
@model
class DeviceConfigIn(DeviceConfig, FromSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (0x00, 0x01, 0x79, 0x02, 0x00)
    _MAP: ClassVar[Mapping[int, str]] = {
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


@model
class EncoderConfig(_ValidateMixin):
    detent: SysexBool = SysexBool.FALSE
    movement_type: EncoderMovementType = EncoderMovementType.DIRECT_HIGH_RESOLUTION
    switch_action_type: EncoderSwitchActionType = EncoderSwitchActionType.CC_HOLD
    switch_midi_channel: MidiChannel = MidiChannel.SWITCH_AND_COLOR
    switch_midi_number: int = 1
    switch_midi_type: int = 0
    encoder_midi_channel: MidiChannel = MidiChannel.ROTARY_ENCODER
    encoder_midi_number: int = 1
    encoder_midi_type: EncoderMidiMessageType = EncoderMidiMessageType.SEND_CC
    active_color: ColorValue = ColorValue.DEFAULT_ACTIVE
    inactive_color: ColorValue = ColorValue.DEFAULT_INACTIVE
    detent_color: DetentColorValue = DetentColorValue.PINK
    indicator_display_type: EncoderIndicatorDisplayType = (
        EncoderIndicatorDisplayType.BLENDED_BAR
    )
    is_super_knob: SysexBool = SysexBool.FALSE
    encoder_shift_midi_channel: MidiChannel = MidiChannel.SHIFT


@model
class EncoderConfigOut(EncoderConfig, ToSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommands.BULK_XFER,
        0x00,
    )
    detent: SysexBool = dc_field(metadata={"addr": 10})
    movement_type: EncoderMovementType = dc_field(metadata={"addr": 11})
    switch_action_type: EncoderSwitchActionType = dc_field(metadata={"addr": 12})
    switch_midi_channel: MidiChannel = dc_field(metadata={"addr": 13})
    switch_midi_number: int = dc_field(metadata={"addr": 14})
    switch_midi_type: int = dc_field(metadata={"addr": 15})
    encoder_midi_channel: MidiChannel = dc_field(metadata={"addr": 16})
    encoder_midi_number: int = dc_field(metadata={"addr": 17})
    encoder_midi_type: EncoderMidiMessageType = dc_field(metadata={"addr": 18})
    active_color: ColorValue = dc_field(metadata={"addr": 19})
    inactive_color: ColorValue = dc_field(metadata={"addr": 20})
    detent_color: DetentColorValue = dc_field(metadata={"addr": 21})
    indicator_display_type: EncoderIndicatorDisplayType = dc_field(
        metadata={"addr": 22}
    )
    is_super_knob: SysexBool = dc_field(metadata={"addr": 23})
    encoder_shift_midi_channel: MidiChannel = dc_field(metadata={"addr": 24})


# ─────────────────────────────────────────────────────────────
# EncoderConfig  ← SysEx (IN)
# ─────────────────────────────────────────────────────────────
@model
class EncoderConfigIn(EncoderConfig, FromSysexMixin):
    _HEADER: ClassVar[Sequence[int]] = (0x00, 0x01, 0x79, 0x03, 0x00)
    _MAP: ClassVar[Mapping[int, str]] = {
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
