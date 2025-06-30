from mftd.constants import MidiChannel
from mftd.sysex import MftSysexApi


def test_get_encoder_value(midi_out, midi_in) -> None:
    # print(MftSysexApi.get_device_config(midi_out, midi_in))
    # encoder_configs = [
    #     MftSysexApi.get_encoder_config(midi_out, midi_in, n) for n in range(0, 16)
    # ]
    # for encoder_config in encoder_configs:
    #     print(encoder_config)
    pass


def test_set_encoder_value(midi_out, midi_in) -> None:
    encoder_index = 0
    encoder_value = 10
    encoder_config = MftSysexApi.get_encoder_config(midi_out, midi_in, encoder_index)
    encoder_config.encoder_midi_channel = MidiChannel(
        encoder_config.encoder_midi_channel - 1
    )
    MftSysexApi.set_encoder_value(
        midi_out,
        encoder_config.encoder_midi_number,
        encoder_value,
        encoder_config.encoder_midi_channel,
    )
