import time

from mftd.constants import MidiChannel
from mftd.device import DeviceConfig


def test_device_channel_transform(
    mft,
) -> None:
    device_config_1 = DeviceConfig()
    device_config_1.system_midi_channel = MidiChannel.SYSTEM
    mft.set_device_config(device_config_1)
    time.sleep(1)
    device_config_2 = mft.get_device_config()
    time.sleep(1)
    assert device_config_2.system_midi_channel == device_config_1.system_midi_channel
    assert device_config_1.system_midi_channel == MidiChannel.SYSTEM
    assert device_config_2.system_midi_channel == MidiChannel.SYSTEM


def test_encoder_channel_transform(
    mft,
) -> None:
    device_config = DeviceConfig()
    encoder_index = 3
    encoder_config_1 = mft.get_encoder_config(encoder_index)
    encoder_config_1.encoder_midi_channel = MidiChannel.ROTARY_ENCODER
    mft.set_encoder_config(encoder_index, encoder_config_1)
    mft.set_device_config(device_config)  # Ensure device returns to operating state
    encoder_config_2 = mft.get_encoder_config(encoder_index)
    assert (
        encoder_config_2.encoder_midi_channel == encoder_config_1.encoder_midi_channel
    )
    assert encoder_config_1.encoder_midi_channel == MidiChannel.ROTARY_ENCODER
