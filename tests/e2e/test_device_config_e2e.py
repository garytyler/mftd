import pytest

from mftd.constants import MidiChannel, SysexBool, SideSwitchAction
from mftd.device import DeviceConfig


@pytest.fixture
def config_1():
    yield DeviceConfig()


@pytest.fixture
def config_2():
    yield DeviceConfig(
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


def test_updated_device_config_values(mft, config_1, config_2) -> None:
    mft.set_device_config(config_1)
    config_1_recvd = mft.get_device_config()
    assert config_1_recvd is not None
    assert config_1_recvd == config_1

    mft.set_device_config(config_2)
    config_2_recvd = mft.get_device_config()
    assert config_2_recvd is not None
    assert config_2_recvd == config_2
