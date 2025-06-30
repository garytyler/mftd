from mftd.device import DeviceConfig, DeviceConfigOut, DeviceConfigIn


def test_model_out_transform():
    config_in = DeviceConfigIn()
    print(config_in)
    config = DeviceConfig.from_incoming(config_in)
    print(config)
    config_out = DeviceConfigOut.from_config(config)
    print(config_out)
