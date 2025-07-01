import time

from mftd.constants import MidiChannel
from mftd.device import DeviceConfig


def test_set_encoder_value(
    mft,
) -> None:
    device_config = DeviceConfig()
    encoder_index = 0
    encoder_value = 30
    encoder_config = mft.get_encoder_config(encoder_index)
    # encoder_config.encoder_midi_channel = MidiChannel(
    #     encoder_config.encoder_midi_channel - 1
    # )
    # encoder_config.encoder_midi_channel = MidiChannel(
    #     encoder_config.encoder_midi_channel - 1
    # )

    mft.set_device_config(device_config)
    mft.set_encoder_value(
        encoder_index=encoder_config.encoder_midi_number,
        value=encoder_value,
        channel=encoder_config.encoder_midi_channel,
    )


def test_device_channel_index(
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

    print(device_config_1)
    print(device_config_2)


def test_encoder_channel_transform(
    mft,
) -> None:
    encoder_index = 3
    encoder_config_1 = mft.get_encoder_config(encoder_index)
    encoder_config_1.encoder_midi_channel = MidiChannel.ROTARY_ENCODER
    mft.set_encoder_config(encoder_index, encoder_config_1)
    encoder_config_2 = mft.get_encoder_config(encoder_index)
    assert (
        encoder_config_2.encoder_midi_channel == encoder_config_1.encoder_midi_channel
    )
    assert encoder_config_1.encoder_midi_channel == MidiChannel.ROTARY_ENCODER
