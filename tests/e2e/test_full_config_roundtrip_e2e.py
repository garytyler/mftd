import time
from copy import deepcopy

import pytest

from mftd import constants


@pytest.fixture
def test_encoder_index():
    yield 1


def test_device_config_roundtrip_all_fields(mft):
    original_config = mft.get_device_config()

    new_config = deepcopy(original_config)
    new_config.system_midi_channel = constants.MidiChannel.SHIFT
    new_config.bank_side_buttons = constants.SysexBool.FALSE
    new_config.left_button_1_function = constants.SideSwitchAction.CC_TOGGLE
    new_config.left_button_2_function = constants.SideSwitchAction.CYCLE_BANK
    new_config.left_button_3_function = constants.SideSwitchAction.BANK2
    new_config.right_button_1_function = constants.SideSwitchAction.BANK3
    new_config.right_button_2_function = constants.SideSwitchAction.BANK4
    new_config.right_button_3_function = constants.SideSwitchAction.SHIFT_PAGE1
    new_config.super_knob_start = 60
    new_config.super_knob_end = 120
    new_config.rgb_led_brightness = 60
    new_config.indicator_global_brightness = 110
    mft.set_device_config(new_config)
    time.sleep(0.5)

    result = mft.get_device_config()
    assert result == new_config

    mft.set_device_config(original_config)
    time.sleep(0.5)


def test_encoder_config_roundtrip_all_fields(mft, test_encoder_index):
    original_config = mft.get_encoder_config(test_encoder_index)

    new_config = deepcopy(original_config)
    new_config.detent = constants.SysexBool.TRUE
    new_config.movement_type = constants.EncoderMovementType.RESPONSIVE
    new_config.switch_action_type = constants.EncoderSwitchActionType.CC_TOGGLE
    new_config.switch_midi_channel = constants.MidiChannel.SYSTEM
    new_config.switch_midi_number = original_config.switch_midi_number + 1
    new_config.switch_midi_type = 1
    new_config.encoder_midi_channel = constants.MidiChannel.SYSTEM
    new_config.encoder_midi_number = original_config.encoder_midi_number + 1
    new_config.encoder_midi_type = constants.EncoderMidiMessageType.SEND_NOTE
    new_config.active_color = constants.Color.BLUE
    new_config.inactive_color = constants.Color.GREEN
    new_config.detent_color = constants.DetentColor.BLUE
    new_config.indicator_display_type = constants.EncoderIndicatorDisplayType.DOT
    new_config.is_super_knob = constants.SysexBool.TRUE
    new_config.encoder_shift_midi_channel = constants.MidiChannel.SYSTEM

    mft.set_encoder_config(test_encoder_index, new_config)
    time.sleep(0.5)

    result = mft.get_encoder_config(test_encoder_index)
    assert result == new_config

    mft.set_encoder_config(test_encoder_index, original_config)
    time.sleep(0.5)
