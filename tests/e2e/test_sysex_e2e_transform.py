import time

from mftd import DeviceConfig
from mftd.api import MftApi
from mftd.constants import MidiChannel, SysexBool, SideSwitchAction


def test_set_device_config_twice_sysex_e2e():
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

    mft = MftApi()

    mft.set_device_config(config_1)
    time.sleep(1)
    rec_config_1 = mft.get_device_config()

    time.sleep(1)

    mft.set_device_config(config_2)
    time.sleep(1)
    rec_config_2 = mft.get_device_config()

    time.sleep(1)

    assert rec_config_1 != rec_config_2
