from mftd.constants import MidiChannel, SysexBool, SideSwitchAction
from mftd.mft import MidiFighterTwister
from mftd.sysex.device import DeviceConfig


def test_sysex_e2e():
    config_1 = DeviceConfig()
    config_2 = DeviceConfig(
        system_midi_channel=MidiChannel.SHIFT,
        bank_side_buttons=SysexBool.FALSE,
        left_button_1_function=SideSwitchAction.CC_TOGGLE,
        left_button_2_function=SideSwitchAction.CC_TOGGLE,
        left_button_3_function=SideSwitchAction.CC_TOGGLE,
        right_button_1_function=SideSwitchAction.CC_TOGGLE,
        right_button_2_function=SideSwitchAction.CC_TOGGLE,
        right_button_3_function=SideSwitchAction.CC_TOGGLE,
        super_knob_start=63,
        super_knob_end=127,
        rgb_led_brightness=60,
        indicator_global_brightness=127,
    )

    mft = MidiFighterTwister()
    mft.set_device_config(config_1)
    rec_config_1 = mft.get_device_config()
    mft.set_device_config(config_2)
    rec_config_2 = mft.get_device_config()
    assert rec_config_1 != rec_config_2
