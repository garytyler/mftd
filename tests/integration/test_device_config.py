from mftd import DeviceConfig
from mftd.constants import MidiChannel, SysexBool


def test_device_config_defaults():
    cfg = DeviceConfig()
    assert cfg.system_midi_channel == MidiChannel.SYSTEM
    assert cfg.bank_side_buttons == SysexBool.TRUE
