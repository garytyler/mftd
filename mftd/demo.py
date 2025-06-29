from mftd.constants import (
    SysexBool,
    MidiChannel,
    SideSwitchAction,
)
from mftd.sysex.device import DeviceConfig

config_1 = DeviceConfig()
config_1.system_midi_channel = MidiChannel.SWITCH_ANIMATION
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

# mft = MidiFighterTwister()
# mft.set_device_config(config_1)
# time.sleep(5)
# rec_config_1 = mft.get_device_config()
# print(rec_config_1)
# time.sleep(5)
# mft.set_device_config(config_2)
# time.sleep(5)
# rec_config_2 = mft.get_device_config()
# print(rec_config_2)
