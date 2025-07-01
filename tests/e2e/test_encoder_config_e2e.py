import time
from copy import deepcopy

import pytest

from mftd import constants


@pytest.fixture
def encoder_index():
    """Fixture to provide a default encoder index."""
    yield 2


@pytest.fixture
def encoder_config(mft, encoder_index):
    encoder_config = mft.get_encoder_config(encoder_index)
    yield encoder_config
    mft.set_encoder_config(encoder_index, encoder_config)
    time.sleep(0.5)


def test_get_set_encoder_config_e2e(mft, encoder_config, encoder_index) -> None:
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

    mft.set_encoder_config(encoder_index, new_config)
    time.sleep(0.5)

    result_config = mft.get_encoder_config(encoder_index)
    assert result_config is not None
    assert result_config.active_color == new_color  # Check for the expected new color
    assert result_config.active_color != old_config.active_color  # Ensure it changed
