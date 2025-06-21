from mftd import MftSysexApi, constants, EncoderConfig, DeviceConfig
from mftd.constants import SideSwitchAction, MidiChannel, SysexBool


def test_set_global_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    cfg = DeviceConfig()
    cfg[31] = 88

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
        response_values.extend([DeviceConfig.NAMES_TO_ADDRESSES[key], val])

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

    assert cfg[31] == 99
    out_msg = out.messages[-1]
    assert out_msg[4] == consts.SysexCommands.PULL_CONF


def test_set_encoder_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    cfg = EncoderConfig()
    cfg.active_color = constants.ColorValue.RED

    api.set_encoder_config(out, 0, cfg)

    msg = out.messages[-1]
    assert msg[0] == 0xF0
    assert msg[4] == constants.SysexCommands.BULK_XFER
    assert constants.ColorValue.RED in msg
    assert msg[-1] == 0xF7


def test_get_encoder_config(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()
    inp = rtmidi_stub.MidiIn()
    consts = constants

    resp = [
        0xF0,
        consts.MIDI_MFR_ID_0,
        consts.MIDI_MFR_ID_1,
        consts.MIDI_MFR_ID_2,
        consts.SysexCommands.BULK_XFER,
        0x00,
        1,
        1,
        1,
        4,
        19,
        consts.ColorValue.BLUE,
        21,
        consts.DetentColorValues.RED,
        0xF7,
    ]
    inp.messages.append((resp, None))

    cfg = api.get_encoder_config(out, inp, 0)

    assert cfg.active_color == consts.ColorValue.BLUE
    assert cfg.detent_color == consts.DetentColorValues.RED


def test_set_encoder_value(rtmidi_stub):
    api = MftSysexApi
    out = rtmidi_stub.MidiOut()

    api.set_encoder_value(out, 2, 64)

    assert out.messages[-1] == [
        0xB0 + constants.MidiChannel.ROTARY_ENCODER,
        2,
        64,
    ]
