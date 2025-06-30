from mftd.constants import MidiChannel


def test_set_encoder_value(
    mft,
) -> None:
    encoder_index = 0
    encoder_value = 20
    encoder_config = mft.get_encoder_config(encoder_index)
    encoder_config.encoder_midi_channel = MidiChannel(
        encoder_config.encoder_midi_channel - 1
    )
    mft.set_encoder_value(
        encoder_index=encoder_config.encoder_midi_number,
        value=encoder_value,
        channel=encoder_config.encoder_midi_channel,
    )

    # Cannot validate in e2e
