from dataclasses import fields

from mftd import MftSysexApi, constants, EncoderConfig, DeviceConfig
from mftd.constants import SideSwitchAction, MidiChannel, SysexBool


def test_set_global_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    cfg = DeviceConfig()
    cfg.rgb_led_brightness = 88

    api.set_device_config(out, cfg)

    assert out.messages
    # The configuration may be sent in multiple SysEx chunks
    merged = []
    for m in out.messages:
        merged.extend(m)
    assert merged[0] == 0xF0
    assert constants.SysexCommands.PUSH_CONF in merged
    assert 31 in merged and 88 in merged
    assert merged[-1] == 0xF7


def test_get_global_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    inp = rtmidi_stub.MidiIn()
    consts = constants

    response_values = []
    name_to_addr = {
        f.name: f.metadata["addr"]
        for f in fields(DeviceConfig)
        if "addr" in f.metadata
    }
    for key, val in {
        "system_midi_channel": int(MidiChannel.ROTARY_ENCODER),
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
        consts.SysexCommands.PULL_CONF,
        0x00,  # status byte
        *response_values,
        0xF7,  # EOX
    ]
    inp.messages.append((resp, 0))  # Use timestamp 0 instead of None

    cfg = api.get_device_config(out, inp)

    assert cfg.rgb_led_brightness == 99
    out_msg = out.messages[-1]
    assert out_msg[4] == consts.SysexCommands.PULL_CONF


def test_set_encoder_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    cfg = EncoderConfig(0)
    cfg.active_color = constants.ColorValue.RED

    api.set_encoder_config(out, 0, cfg)

    assert out.messages[0][0] == 0xF0
    assert out.messages[0][4] == constants.SysexCommands.BULK_XFER
    assert constants.ColorValue.RED in out.messages[0]
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
        consts.SysexCommands.BULK_XFER,
        0x00,
        1,  # sysex_tag
        1,  # part
        1,  # total
        6,  # size updated to include the new field
        encoder_midi_number_addr,  # Add address for encoder_midi_number
        0,  # Value for encoder_midi_number (using the test index)
        19,
        consts.ColorValue.BLUE,
        21,
        consts.DetentColorValue.RED,
        0xF7,
    ]
    inp.messages.append((resp, None))

    cfg = api.get_encoder_config(out, inp, 0)

    assert cfg.active_color == consts.ColorValue.BLUE
    assert cfg.detent_color == consts.DetentColorValue.RED
