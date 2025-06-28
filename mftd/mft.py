from mftd.midi import create_midi_input, create_midi_output
from mftd.sysex.device import DeviceConfigOut, DeviceConfig
from mftd.sysex.encoder import EncoderConfig


class MidiFighterTwister:
    def __init__(self):
        self.midi_in = create_midi_input()
        self.midi_out = create_midi_output()

    def set_device_config(self, config: DeviceConfig):
        out_config = DeviceConfigOut.from_config(config)
        if self.midi_out:
            for sysex_msg in out_config.to_sysex():
                self.midi_out.send_message(sysex_msg)

    def get_device_config(self, device_config: DeviceConfig):
        pass

    def set_encoder_config(self, index, config: EncoderConfig):
        pass
