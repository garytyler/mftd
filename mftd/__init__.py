# mylib/__init__.py

from mftd.constants import (
    MidiChannel,
    EncoderControl,
    SystemMessage,
    Color,
    DetentColor,
    EncoderAnimation,
    EncoderIndicatorBrightness,
    EncoderRgbBrightness,
    EncoderControlType,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    EncoderIndicatorDisplayType,
    SysexCommand,
    SysexBool,
    SideSwitchAction,
    Encoders,
)
from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.mft import MidiFighterTwister
from mftd.midi import TdMidiOutput

__all__ = [
    "MidiChannel",
    "EncoderControl",
    "SystemMessage",
    "Color",
    "DetentColor",
    "EncoderAnimation",
    "EncoderIndicatorBrightness",
    "EncoderRgbBrightness",
    "EncoderControlType",
    "EncoderMovementType",
    "EncoderSwitchActionType",
    "EncoderMidiMessageType",
    "EncoderIndicatorDisplayType",
    "SysexCommand",
    "SysexBool",
    "SideSwitchAction",
    "Encoders",
    "DeviceConfig",
    "EncoderConfig",
    "MidiFighterTwister",
    "TdMidiOutput",
    "MidiToOscForwarder",
    "OscToMidiForwarder",
    "MidiOscBridge",
]


def __getattr__(name):  # optional safeguard (PEP 562)
    raise AttributeError(f"{name!r} is not a shared attribute.")
