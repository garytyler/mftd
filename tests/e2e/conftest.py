import time

import pytest

from mftd import MftSysexApi
from mftd.midi import (
    create_midi_input,
    create_midi_output,
)


@pytest.fixture
def midi_in():
    """Create a real MIDI input device."""
    midi_in = create_midi_input()
    if midi_in is None:
        pytest.skip("MIDI input not available")
    if "FakeMidiIn" in str(type(midi_in)):
        pytest.skip("Real MIDI device required for E2E tests")
    yield midi_in
    midi_in.close_port()


@pytest.fixture
def midi_out():
    """Create a real MIDI output device."""
    midi_out = create_midi_output()
    if midi_out is None:
        pytest.skip("MIDI output not available")
    if "FakeMidiOut" in str(type(midi_out)):
        pytest.skip("Real MIDI device required for E2E tests")
    yield midi_out
    midi_out.close_port()


@pytest.fixture(scope="session")
def device_config(midi_out, midi_in):
    device_config = MftSysexApi.get_device_config(midi_out, midi_in)
    yield device_config
    MftSysexApi.set_device_config(midi_out, device_config)
    time.sleep(0.5)
