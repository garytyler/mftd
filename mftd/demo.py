import time

from mftd import create_midi_output
from mftd.constants import (
    SysexBool,
    MidiChannel,
    SideSwitchAction,
)
from mftd.sysex.device import DeviceConfigOut

out_config_1 = DeviceConfigOut()
out_config_2 = DeviceConfigOut(
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

midi_out = create_midi_output()
if midi_out:
    for sysex_msg in out_config_1.to_sysex():
        midi_out.send_message(sysex_msg)
    time.sleep(5)
    in_config = out_config_1.to_sysex()
