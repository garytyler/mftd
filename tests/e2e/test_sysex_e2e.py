import time
from copy import deepcopy

from mftd import constants, MftSysexApi


def test_get_set_global_config_e2e(device_config, midi_out, midi_in) -> None:
    old_config = device_config
    old_value = old_config.rgb_led_brightness

    new_value = (old_value + 1) % 128
    new_config = deepcopy(old_config)
    new_config.rgb_led_brightness = new_value

    MftSysexApi.set_device_config(midi_out, new_config)
    time.sleep(0.5)

    result_config = MftSysexApi.get_device_config(midi_out, midi_in)
    assert result_config is not None
    assert result_config.rgb_led_brightness == new_value


def test_get_set_encoder_config_e2e(
    midi_out, midi_in, encoder_config, encoder_index
) -> None:
    old_config = encoder_config

    # Ensure we pick a different color value
    if old_config.active_color == constants.ColorValue.RED:
        new_color = constants.ColorValue.BLUE
    elif old_config.active_color == constants.ColorValue.BLUE:
        new_color = constants.ColorValue.GREEN  # or another color
    else:
        new_color = constants.ColorValue.RED

    new_config = deepcopy(old_config)
    new_config.active_color = new_color

    MftSysexApi.set_encoder_config(midi_out, encoder_index, new_config)
    time.sleep(0.5)

    result_config = MftSysexApi.get_encoder_config(midi_out, midi_in, encoder_index)
    assert result_config is not None
    assert result_config.active_color == new_color  # Check for the expected new color
    assert result_config.active_color != old_config.active_color  # Ensure it changed
