import asyncio

import pytest
from pythonosc import udp_client

from mftd.bridge import OscToMidiForwarder


class RecordingMidiOut:
    def __init__(self):
        self.messages = asyncio.Queue()

    def send_message(self, message):
        self.messages.put_nowait(message)

    def close_port(self):
        pass


@pytest.mark.asyncio
async def test_osc_to_midi_end_to_end():
    midi_out = RecordingMidiOut()
    forwarder = OscToMidiForwarder(midi_out=midi_out, listen_port=0)

    await forwarder.start()
    port = forwarder.listening_port
    assert port is not None

    client = udp_client.SimpleUDPClient("127.0.0.1", port)
    client.send_message("/mftd/cc", [4, 22, 45])

    message = await asyncio.wait_for(midi_out.messages.get(), timeout=1)
    assert message == [0xB4, 22, 45]

    await forwarder.stop()
