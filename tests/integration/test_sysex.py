from dataclasses import fields

from mftd import constants
from mftd.constants import SideSwitchAction, MidiChannel, SysexBool
from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.mft import MftSysexApi


def test_set_global_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    device_config = DeviceConfig()
    device_config.rgb_led_brightness = 88
    data = device_config.to_out_dict()

    api.set_device_config(out, data)

    assert out.messages
    # The configuration may be sent in multiple SysEx chunks
    merged = []
    for m in out.messages:
        merged.extend(m)
    assert merged[0] == 0xF0
    assert constants.SysexCommand.PUSH_CONF in merged
    assert 31 in merged and 88 in merged
    assert merged[-1] == 0xF7


def test_get_global_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    inp = rtmidi_stub.MidiIn()
    consts = constants

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

    # Format response exactly like the real device
    resp = [
        0xF0,
        consts.MIDI_MFR_ID_0,
        consts.MIDI_MFR_ID_1,
        consts.MIDI_MFR_ID_2,
        consts.SysexCommand.PULL_CONF,
        0x00,  # status byte
        *response_values,
        0xF7,  # EOX
    ]
    inp.messages.append((resp, 0))  # Use timestamp 0 instead of None

    resp = api.get_device_config(out, inp)
    cfg = DeviceConfig.from_in_dict(resp)

    assert cfg.rgb_led_brightness == 99
    out_msg = out.messages[-1]
    assert out_msg[4] == consts.SysexCommand.PULL_CONF


def test_set_encoder_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    cfg = EncoderConfig()
    cfg.active_color = constants.Color.RED

    out_data = cfg.to_out_dict()
    api.set_encoder_config(out, 0, out_data)

    assert out.messages[0][0] == 0xF0
    assert out.messages[0][4] == constants.SysexCommand.BULK_XFER
    assert constants.Color.RED in out.messages[0]
    assert out.messages[0][-1] == 0xF7


def test_get_encoder_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    inp = rtmidi_stub.MidiIn()
    consts = constants

    # Find the address for encoder_midi_number in EncoderConfig
    name_to_addr = {
        f.name: f.metadata["addr"]
        for f in fields(EncoderConfig)
        if "addr" in f.metadata
    }
    encoder_midi_number_addr = name_to_addr["encoder_midi_number"]

    resp = [
        0xF0,
        consts.MIDI_MFR_ID_0,
        consts.MIDI_MFR_ID_1,
        consts.MIDI_MFR_ID_2,
        consts.SysexCommand.BULK_XFER,
        0x00,
        1,  # sysex_tag
        1,  # part
        1,  # total
        6,  # size updated to include the new field
        encoder_midi_number_addr,  # Add address for encoder_midi_number
        0,  # Value for encoder_midi_number (using the test index)
        19,
        consts.Color.BLUE,
        21,
        consts.DetentColor.RED,
        0xF7,
    ]
    inp.messages.append((resp, None))

    in_data = api.get_encoder_config(out, inp, 0)
    cfg = EncoderConfig.from_in_dict(in_data)
    assert cfg.active_color == consts.Color.BLUE
    assert cfg.detent_color == consts.DetentColor.RED


def test_set_encoder_value_sends_correct_cc(rtmidi_stub):
    """
    Verify that `set_encoder_value` emits the expected three-byte MIDI
    Control-Change message.

    A minimal stub is used in place of a real MIDI-output port so that the
    test remains fast, deterministic and free from external dependencies.
    """

    # Given
    encoder_index = 10  # a valid encoder (0-63)
    value = 64  # an arbitrary value (0-127)
    channel = 2  # an arbitrary MIDI channel (0-15)
    midi_out = rtmidi_stub.MidiOut()

    # When
    MftSysexApi.set_encoder_value(midi_out, encoder_index, value, channel)

    # Then
    expected_status = 0xB0 | (channel & 0x0F)
    expected = [expected_status, encoder_index, value]

    assert midi_out.messages == [expected], (
        "The Control-Change message sent to the MIDI out-port does not match "
        "what the API is expected to emit."
    )


def test_set_encoder_animation_sends_correct_cc(rtmidi_stub):
    encoder_index = 5
    value = constants.EncoderAnimation.INDICATOR_BRIGHTNESS_MAX
    channel = constants.MidiChannel.ANIMATIONS_AND_BRIGHTNESS
    midi_out = rtmidi_stub.MidiOut()

    MftSysexApi.set_encoder_animation_and_brightness(
        midi_out, encoder_index, value, channel
    )

    expected_status = 0xB0 | (channel & 0x0F)
    expected = [expected_status, encoder_index, int(value)]

    assert midi_out.messages == [expected]
