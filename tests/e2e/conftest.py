import pytest

from mftd.device import DeviceConfig
from mftd.encoder import EncoderConfig
from mftd.mft import MftSysexApi, MidiFighterTwister
from mftd.midi import (
    create_midi_input,
    create_midi_output,
)


@pytest.fixture(scope="session")
def midi_in():
    """Create a real MIDI input device."""
    midi_in = create_midi_input()
    if midi_in is None:
        pytest.skip("MIDI input not available")
    if "FakeMidiIn" in str(type(midi_in)):
        pytest.skip("Real MIDI device required for E2E tests")
    yield midi_in
    midi_in.close_port()


@pytest.fixture(scope="session")
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
def api():
    yield MftSysexApi


@pytest.fixture(scope="session")
def mft(midi_out, midi_in):
    yield MidiFighterTwister(midi_out=midi_out, midi_in=midi_in)


@pytest.fixture(scope="session", autouse=True)
def device_config(midi_out, midi_in, mft, api):
    device_config_in_data = api.get_device_config(midi_out, midi_in)
    if not device_config_in_data:
        RuntimeError("Failed to get device config")
    device_config = DeviceConfig.from_in_dict(device_config_in_data)

    yield device_config

    out_data = device_config.to_out_dict()
    api.set_device_config(midi_out, out_data)


@pytest.fixture(scope="session", autouse=True)
def _encoder_configs(device_config, midi_out, midi_in, mft, api):
    encoder_configs = []
    for n in range(0, 16):
        in_data = api.get_encoder_config(midi_out, midi_in, n)
        config = EncoderConfig.from_in_dict(in_data)
        encoder_configs.append((n, config))

    yield

    for n, config in encoder_configs:
        out_data = config.to_out_dict()
        api.set_encoder_config(midi_out, n, out_data)
