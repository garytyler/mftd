"""Lock the 2026 firmware's SysEx spec against silent drift.

Every value here was taken from the Midi Fighter Utility's device plugin
(``Resources/plugins/device.mf_twister.js``, the branches gated on
``fw_version >= 0x20230c11``) and confirmed against hardware.

These matter more than most constants: the 2026 firmware *renumbered* two
enums by insertion rather than appending to them, so stale values do not fail
loudly — they select a different, valid function.  ``SHIFT_HOLD`` at its old 6
now means "Encoder Fine Adjust", and ``CYCLE_BANK`` at its old 12 now means
"Bank 2".
"""

from dataclasses import fields

import pytest

from mftd.constants import (
    ColorMap,
    EncoderSwitchActionType,
    MidiChannel,
    SideSwitchAction,
    SleepAnimation,
    SleepTimer,
    SysexBool,
    SysexCommand,
)
from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.sysex import MftSysexApi

# Address -> wire value, exactly as a 2026 device reports a factory config.
FIRMWARE_2026_DEVICE_ADDRS = {33, 34, 35, 36, 37, 38}

# The factory value each address holds, read from the Utility plugin's
# CONFIG.addEnum/addBool calls (device.mf_twister.js:306-309), where the
# argument after the option list is the default index.
FIRMWARE_2026_DEFAULTS = {
    33: ColorMap.CLASSIC,
    36: SleepTimer.MIN_60,
    37: SleepAnimation.RAINBOW_WAVE,
    38: SysexBool.TRUE,
}


@pytest.mark.parametrize(
    "member, value",
    [
        (EncoderSwitchActionType.CC_HOLD, 0),
        (EncoderSwitchActionType.CC_TOGGLE, 1),
        (EncoderSwitchActionType.NOTE_HOLD, 2),
        (EncoderSwitchActionType.NOTE_TOGGLE, 3),
        (EncoderSwitchActionType.ENC_RESET_VALUE, 4),
        (EncoderSwitchActionType.ENC_RESET_VALUE_MAX, 5),
        (EncoderSwitchActionType.ENC_FINE_ADJUST, 6),
        (EncoderSwitchActionType.SHIFT_HOLD, 7),
        (EncoderSwitchActionType.SHIFT_TOGGLE, 8),
    ],
)
def test_encoder_switch_action_numbering(member, value):
    assert int(member) == value


@pytest.mark.parametrize(
    "member, value",
    [
        (SideSwitchAction.SHIFT_PAGE2, 0x05),
        (SideSwitchAction.SHIFT_PAGE1_TOGGLE, 0x06),
        (SideSwitchAction.SHIFT_PAGE2_TOGGLE, 0x07),
        (SideSwitchAction.NEXT_BANK, 0x08),
        (SideSwitchAction.PREV_BANK, 0x09),
        (SideSwitchAction.BANK_SELECT, 0x0A),
        (SideSwitchAction.BANK1, 0x0B),
        (SideSwitchAction.BANK8, 0x12),
        (SideSwitchAction.CYCLE_BANK, 0x13),
    ],
)
def test_side_switch_action_numbering(member, value):
    assert int(member) == value


def test_pre_2026_values_now_mean_something_else():
    """The renumbering is a silent hazard; state it as an assertion."""
    assert EncoderSwitchActionType(6) is EncoderSwitchActionType.ENC_FINE_ADJUST
    assert SideSwitchAction(12) is SideSwitchAction.BANK2


def test_device_config_declares_the_2026_addresses():
    addrs = {f.metadata["addr"] for f in fields(DeviceConfig) if "addr" in f.metadata}
    assert FIRMWARE_2026_DEVICE_ADDRS <= addrs


def test_device_defaults_match_firmware_defaults():
    """A bare DeviceConfig should describe a factory device, not a house style.

    addr 33 is the one exception and is covered separately below.
    """
    config = DeviceConfig()
    assert config.sleep_timer is FIRMWARE_2026_DEFAULTS[36]
    assert config.sleep_animation is FIRMWARE_2026_DEFAULTS[37]
    assert config.bank_change_animations is FIRMWARE_2026_DEFAULTS[38]


def test_color_map_default_diverges_from_firmware_on_purpose():
    """addr 33 is where the library knowingly departs from the factory value.

    Color's members are Expanded bytes, so a CLASSIC default would make every
    named colour in the library select a different colour with no error.  Both
    halves are pinned separately: the firmware's own value stays on record, so
    withdrawing the divergence -- or discovering the factory value is not what
    the Utility plugin claims -- fails here rather than drifting quietly.
    """
    assert FIRMWARE_2026_DEFAULTS[33] is ColorMap.CLASSIC
    assert DeviceConfig().color_map is ColorMap.EXPANDED


@pytest.mark.parametrize(
    "addr, wire, expected",
    [
        # Observed on a 2026 device: addr 34 reads 6, addr 35 reads 3.
        (34, 6, MidiChannel.SWITCH_ANIMATION),
        (35, 3, MidiChannel.ANIMATIONS_AND_BRIGHTNESS),
        (0, 4, MidiChannel.SYSTEM),
    ],
)
def test_device_channel_fields_are_one_indexed_on_the_wire(addr, wire, expected):
    config = DeviceConfig.from_in_dict({addr: wire})
    name = {
        f.metadata["addr"]: f.name for f in fields(DeviceConfig) if "addr" in f.metadata
    }[addr]
    assert getattr(config, name) == expected
    assert config.to_out_dict()[addr] == wire


def test_encoder_shift_channel_is_one_indexed_on_the_wire():
    """Addr 24 was previously sent untransformed, landing shift a channel low."""
    config = EncoderConfig()
    assert config.encoder_shift_midi_channel is MidiChannel.SHIFT
    assert config.to_out_dict()[24] == int(MidiChannel.SHIFT) + 1
    assert EncoderConfig.from_in_dict({24: 5}).encoder_shift_midi_channel == (
        MidiChannel.SHIFT
    )


@pytest.mark.parametrize("model", [DeviceConfig, EncoderConfig])
def test_default_configs_emit_legal_sysex_bytes(model):
    """Anything outside 0-127 cannot be sent, and rtmidi rejects the message."""
    out_of_range = {a: v for a, v in model().to_out_dict().items() if not 0 <= v <= 127}
    assert not out_of_range


@pytest.mark.parametrize("model", [DeviceConfig, EncoderConfig])
def test_wire_round_trip_is_lossless(model):
    """Reading a device and writing it straight back must be a no-op."""
    wire = model().to_out_dict()
    assert model.from_in_dict(wire).to_out_dict() == wire


def test_device_config_is_never_split_across_messages():
    """PUSH_CONF has no part/total, and the firmware zeroes omitted addresses.

    A split push therefore wipes whatever was in the earlier message.  Adding
    the 2026 addresses took the payload past the old chunking threshold, which
    blacked out every encoder on a live rig.
    """

    class _Recorder:
        def __init__(self):
            self.messages = []

        def send_message(self, data):
            self.messages.append(list(data))

    out = _Recorder()
    config = DeviceConfig()
    MftSysexApi.set_device_config(out, config.to_out_dict())

    assert len(out.messages) == 1, "device config must be a single SysEx message"

    message = out.messages[0]
    assert message[0] == 0xF0 and message[-1] == 0xF7
    assert message[4] == SysexCommand.PUSH_CONF

    sent_addrs = set(message[5:-1:2])
    declared = {
        f.metadata["addr"] for f in fields(DeviceConfig) if "addr" in f.metadata
    }
    assert sent_addrs == declared
