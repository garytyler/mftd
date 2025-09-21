from dataclasses import fields

import pytest

from mftd import constants
from mftd.constants import MidiChannel, SysexBool, SideSwitchAction
from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.mft import MidiFighterTwister


@pytest.fixture
def mft(rtmidi_stub):
    midi_out = rtmidi_stub.MidiOut()
    midi_in = rtmidi_stub.MidiIn()
    return MidiFighterTwister(midi_in=midi_in, midi_out=midi_out)


def test_set_device_config(mft):
    cfg = DeviceConfig()
    cfg.rgb_led_brightness = 88

    mft.set_device_config(cfg)

    merged = []
    for msg in mft.midi_output.messages:
        merged.extend(msg)

    assert merged[0] == 0xF0
    assert constants.SysexCommand.PUSH_CONF in merged
    assert 31 in merged and 88 in merged
    assert merged[-1] == 0xF7


def test_get_device_config(mft):
    response_values = []
    name_to_addr = {
        f.name: f.metadata["addr"] for f in fields(DeviceConfig) if "addr" in f.metadata
    }
    for key, val in {
        "system_midi_channel": int(MidiChannel.SYSTEM),
        "super_knob_start": 40,
        "super_knob_end": 90,
        "rgb_led_brightness": 99,
        "indicator_global_brightness": 82,
        "bank_side_buttons": int(SysexBool.FALSE),
        "left_button_1_function": int(SideSwitchAction.BANK1),
        "left_button_2_function": int(SideSwitchAction.BANK2),
        "left_button_3_function": int(SideSwitchAction.BANK3),
        "right_button_1_function": int(SideSwitchAction.BANK4),
        "right_button_2_function": int(SideSwitchAction.NOTE_HOLD),
        "right_button_3_function": int(SideSwitchAction.SHIFT_PAGE1),
    }.items():
        response_values.extend([name_to_addr[key], val])

    resp = [
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommand.PULL_CONF,
        0x00,
        *response_values,
        0xF7,
    ]
    mft.midi_input.messages.append((resp, 0))

    cfg = mft.get_device_config()
    assert cfg is not None
    assert cfg.rgb_led_brightness == 99
    out_msg = mft.midi_output.messages[-1]
    assert out_msg[4] == constants.SysexCommand.PULL_CONF


def test_set_encoder_config(mft):
    cfg = EncoderConfig()
    cfg.active_color = constants.Color.RED

    mft.set_encoder_config(0, cfg)

    msg = mft.midi_output.messages[0]
    assert msg[0] == 0xF0
    assert msg[4] == constants.SysexCommand.BULK_XFER
    assert constants.Color.RED in msg
    assert msg[-1] == 0xF7


def test_get_encoder_config(mft):
    name_to_addr = {
        f.name: f.metadata["addr"]
        for f in fields(EncoderConfig)
        if "addr" in f.metadata
    }
    encoder_midi_number_addr = name_to_addr["encoder_midi_number"]

    resp = [
        0xF0,
        constants.MIDI_MFR_ID_0,
        constants.MIDI_MFR_ID_1,
        constants.MIDI_MFR_ID_2,
        constants.SysexCommand.BULK_XFER,
        0x00,
        1,
        1,
        1,
        6,
        encoder_midi_number_addr,
        0,
        19,
        constants.Color.BLUE,
        21,
        constants.DetentColor.RED,
        0xF7,
    ]
    mft.midi_input.messages.append((resp, None))

    cfg = mft.get_encoder_config(0)
    assert cfg.active_color == constants.Color.BLUE
    assert cfg.detent_color == constants.DetentColor.RED


def test_set_encoder_value(mft):
    encoder_index = 10
    value = 64
    channel = 2

    mft.set_encoder_value(encoder_index, value, channel)

    expected_status = 0xB0 | (channel & 0x0F)
    expected = [expected_status, encoder_index, value]

    assert mft.midi_output.messages == [expected]


def test_set_encoder_value_without_midi_out(monkeypatch, rtmidi_stub):
    midi_in = rtmidi_stub.MidiIn()
    monkeypatch.setattr("mftd.mft.create_midi_output", lambda: None)

    mft = MidiFighterTwister(midi_in=midi_in, midi_out=None)

    with pytest.raises(RuntimeError, match="MIDI output is not available."):
        mft.set_encoder_value(encoder_index=0, value=0)


def test_set_encoder_animation(mft):
    encoder_index = 3
    value = constants.EncoderAnimation.RGB_BRIGHTNESS_MID
    channel = constants.MidiChannel.ANIMATIONS_AND_BRIGHTNESS

    mft.set_encoder_animation(encoder_index, value, channel)

    expected_status = 0xB0 | (channel & 0x0F)
    expected = [expected_status, encoder_index, int(value)]

    assert mft.midi_output.messages[-1] == expected


def test_set_indicator_brightness(mft):
    encoder_index = 4
    brightness = constants.EncoderIndicatorBrightness.QUARTER

    mft.set_encoder_indicator_brightness(encoder_index, brightness)

    expected_status = 0xB0 | (constants.MidiChannel.ANIMATIONS_AND_BRIGHTNESS & 0x0F)
    expected = [expected_status, encoder_index, int(brightness)]

    assert mft.midi_output.messages[-1] == expected


def test_set_rgb_brightness(mft):
    encoder_index = 7
    brightness = constants.EncoderRgbBrightness.MAX

    mft.set_encoder_rgb_brightness(encoder_index, brightness)

    expected_status = 0xB0 | (constants.MidiChannel.ANIMATIONS_AND_BRIGHTNESS & 0x0F)
    expected = [expected_status, encoder_index, int(brightness)]

    assert mft.midi_output.messages[-1] == expected
