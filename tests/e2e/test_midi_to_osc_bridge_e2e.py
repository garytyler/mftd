import asyncio

import pytest
from pythonosc import dispatcher, osc_server

from mftd.bridge import MidiToOscForwarder


class TriggerMidiIn:
    def __init__(self):
        self.callback = None

    def set_callback(self, callback, data=None):
        self.callback = callback

    def cancel_callback(self):
        self.callback = None

    def close_port(self):
        pass

    def emit(self, message):
        if self.callback:
            self.callback(message, None)


@pytest.mark.asyncio
async def test_midi_to_osc_end_to_end():
    loop = asyncio.get_running_loop()
    messages = asyncio.Queue()

    disp = dispatcher.Dispatcher()

    def capture(address, *args):
        messages.put_nowait((address, list(args)))

    disp.map("/mftd/cc", capture)
    server = osc_server.AsyncIOOSCUDPServer(("127.0.0.1", 0), disp, loop)
    transport, _ = await server.create_serve_endpoint()
    port = transport.get_extra_info("sockname")[1]

    midi_in = TriggerMidiIn()
    forwarder = MidiToOscForwarder(midi_in=midi_in, osc_port=port)

    await forwarder.start()

    midi_in.emit(([0xB3, 7, 120], 0.0))

    address, payload = await asyncio.wait_for(messages.get(), timeout=1)
    assert address == "/mftd/cc"
    assert payload == [3, 7, 120]

    await forwarder.stop()
    transport.close()
