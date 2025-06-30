from dataclasses import asdict

from mftd.device import DeviceConfig, DeviceConfigOut


def test_model_out_transform():
    config = DeviceConfig()

    config_out = DeviceConfigOut(**asdict(config))
