import time

import pytest

from mftd import MftSysexApi, constants
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


@pytest.fixture
def mft_sysex_api(midi_in, midi_out):
    """Setup MIDI ports and restore device state after testing."""
    from mftd.sysex import MftSysexApi

    in_port = None
    out_port = None

    # Find input port
    for i in range(midi_in.get_port_count()):
        if constants.DEVICE_NAME in midi_in.get_port_name(i):
            in_port = i
            break

    # Find output port
    for i in range(midi_out.get_port_count()):
        if constants.DEVICE_NAME in midi_out.get_port_name(i):
            out_port = i
            break

    if in_port is None or out_port is None:
        pytest.skip("Midi Fighter Twister device not found")

    # Store initial state
    start_global_config = MftSysexApi.get_device_config(midi_out, midi_in)

    yield MftSysexApi

    # Restore state
    MftSysexApi.set_device_config(midi_out, start_global_config)


@pytest.fixture
def encoder_index():
    """Fixture to provide a default encoder index."""
    yield 2


@pytest.fixture
def encoder_config(midi_out, midi_in, encoder_index):
    encoder_config = MftSysexApi.get_encoder_config(midi_out, midi_in, encoder_index)
    yield encoder_config
    MftSysexApi.set_encoder_config(midi_out, encoder_index, encoder_config)
    time.sleep(0.5)


@pytest.fixture
def device_config(midi_out, midi_in):
    device_config = MftSysexApi.get_device_config(midi_out, midi_in)
    yield device_config
    MftSysexApi.set_device_config(midi_out, device_config)
    time.sleep(0.5)
