import time
from copy import deepcopy

from mftd import constants


def test_get_set_global_config_e2e(
    mft_sysex_api, device_config, midi_out, midi_in
) -> None:
    old_config = device_config
    old_value = old_config[31]

    new_value = (old_value + 1) % 128
    new_config = deepcopy(old_config)
    new_config[31] = new_value

    mft_sysex_api.set_device_config(midi_out, new_config)
    time.sleep(0.5)

    result_config = mft_sysex_api.get_device_config(midi_out, midi_in)
    assert result_config[31] == new_value


def test_get_set_encoder_config_e2e(
    midi_out, midi_in, mft_sysex_api, encoder_config, encoder_index
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

    mft_sysex_api.set_encoder_config(midi_out, encoder_index, new_config)
    time.sleep(0.5)

    result_config = mft_sysex_api.get_encoder_config(midi_out, midi_in, encoder_index)
    assert result_config.active_color == new_color  # Check for the expected new color
    assert result_config.active_color != old_config.active_color  # Ensure it changed
