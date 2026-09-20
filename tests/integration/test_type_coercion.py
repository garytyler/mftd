from mftd.device import DeviceConfig
from mftd.constants import MidiChannel, SysexBool, SideSwitchAction


def test_device_config_type_coercion_on_init():
    cfg = DeviceConfig(
        system_midi_channel=4,
        bank_side_buttons=0,
        left_button_1_function=8,
        super_knob_start="50",
    )

    assert isinstance(cfg.system_midi_channel, MidiChannel)
    assert cfg.system_midi_channel == MidiChannel.SHIFT
    assert isinstance(cfg.bank_side_buttons, SysexBool)
    assert cfg.bank_side_buttons == SysexBool.FALSE
    assert isinstance(cfg.left_button_1_function, SideSwitchAction)
    # 8 is NEXT_BANK under the 2026 numbering; it was BANK1 before.
    assert cfg.left_button_1_function == SideSwitchAction.NEXT_BANK
    assert isinstance(cfg.super_knob_start, int)
    assert cfg.super_knob_start == 50


def test_device_config_type_coercion_on_setattr():
    cfg = DeviceConfig()
    cfg.rgb_led_brightness = "85"
    cfg.right_button_2_function = 9

    assert isinstance(cfg.rgb_led_brightness, int)
    assert cfg.rgb_led_brightness == 85
    assert isinstance(cfg.right_button_2_function, SideSwitchAction)
    # 9 is PREV_BANK under the 2026 numbering; it was BANK2 before.
    assert cfg.right_button_2_function == SideSwitchAction.PREV_BANK
