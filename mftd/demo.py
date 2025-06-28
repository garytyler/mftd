"""
demo.py – end-to-end example for sysex_models.py
No third-party libraries required; MIDI I/O is just simulated here.
"""

from mftd import create_midi_output
from mftd.base import DeviceConfigOut
from mftd.constants import (
    SysexBool,
    MidiChannel,
    SideSwitchAction,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    ColorValue,
    DetentColorValue,
    EncoderIndicatorDisplayType,
)

# out_cfg = DeviceConfigOut()
out_cfg = DeviceConfigOut(
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
print("Outgoing dataclass  :", out_cfg)
print("Outgoing SysEx bytes :", out_cfg.to_sysex())

midi_out = create_midi_output()
if midi_out:
    for sysex_msg in out_cfg.to_sysex():
        midi_out.send_message(sysex_msg)
