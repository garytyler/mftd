import pytest

from mftd.bridge import OscToMidiForwarder


class FakeMidiOut:
    def __init__(self):
        self.sent = []
        self.closed = False

    def send_message(self, message):
        self.sent.append(message)

    def close_port(self):
        self.closed = True


@pytest.mark.asyncio
async def test_osc_to_midi_translates_cc_messages():
    midi_out = FakeMidiOut()
    forwarder = OscToMidiForwarder(midi_out=midi_out)

    await forwarder.start()

    forwarder.handle_osc_message("/mftd/cc", 1, 74, 32)

    assert midi_out.sent == [[0xB1, 74, 32]]

    await forwarder.stop()
    assert midi_out.closed
