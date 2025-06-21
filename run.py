from mftd import DeviceConfig, EncoderConfig
from mftd.midi import MftApi


def run() -> None:
    """Demo usage of the mftd library."""
    api = MftApi()

    api.set_device_config(DeviceConfig())

    encoder_config = EncoderConfig()

    api.set_encoder_config(encoder_config.encoder_midi_number, encoder_config)

    device_config = api.get_device_config()
    print(device_config)
    encoder_config = api.get_encoder_config(1)
    print(encoder_config)


if __name__ == "__main__":
    run()
