from dataclasses import asdict

from mftd.device import DeviceConfig, DeviceConfigOut, DeviceConfigIn


def test_model_out_transform():
    config_in = DeviceConfigIn()
    config = DeviceConfig.from_incoming(config_in)
    config_out = DeviceConfigOut.from_config(config)
    assert asdict(config_in) == asdict(config) == asdict(config_out)
