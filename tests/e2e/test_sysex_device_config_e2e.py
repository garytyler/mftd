import time

import pytest

from mftd.constants import MidiChannel, SysexBool, SideSwitchAction
from mftd.device import DeviceConfig
from mftd.sysex import MftSysexApi


@pytest.fixture
def old_config(midi_out):
    config_1 = DeviceConfig()
    MftSysexApi.set_device_config(midi_out, config_1)
    time.sleep(0.5)
    yield config_1


@pytest.fixture
def new_config(midi_out, old_config):
    new_config = DeviceConfig(
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
    MftSysexApi.set_device_config(midi_out, new_config)
    time.sleep(0.5)
    yield new_config


def test_device_config_updates(old_config, new_config):
    assert old_config != new_config


def test_updated_device_config_values(
    midi_out, midi_in, old_config, new_config
) -> None:
    result_config = MftSysexApi.get_device_config(midi_out, midi_in)
    assert result_config is not None
    assert result_config.bank_side_buttons == new_config.bank_side_buttons
    assert result_config.left_button_1_function == new_config.left_button_1_function
    assert result_config.left_button_2_function == new_config.left_button_2_function
    assert result_config.left_button_3_function == new_config.left_button_3_function
    assert result_config.right_button_1_function == new_config.right_button_1_function
    assert result_config.right_button_2_function == new_config.right_button_2_function
    assert result_config.right_button_3_function == new_config.right_button_3_function
    assert result_config.super_knob_start == new_config.super_knob_start
    assert result_config.super_knob_end == new_config.super_knob_end
    assert result_config.rgb_led_brightness == new_config.rgb_led_brightness
    assert (
        result_config.indicator_global_brightness
        == new_config.indicator_global_brightness
    )
    assert result_config.system_midi_channel == new_config.system_midi_channel
