import asyncio

import pytest

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

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


async def _run_midi_to_osc_end_to_end() -> None:
    loop = asyncio.get_running_loop()
    messages_primary = asyncio.Queue()
    messages_secondary = asyncio.Queue()

    disp_primary = Dispatcher()
    disp_secondary = Dispatcher()

    def capture_primary(_address, *args):
        messages_primary.put_nowait((_address, list(args)))

    def capture_secondary(_address, *args):
        messages_secondary.put_nowait((_address, list(args)))

    disp_primary.map("/mftd/cc", capture_primary)
    disp_secondary.map("/mftd/cc", capture_secondary)

    server_primary = AsyncIOOSCUDPServer(("127.0.0.1", 0), disp_primary, loop)
    transport_primary, _ = await server_primary.create_serve_endpoint()
    port_primary = transport_primary.get_extra_info("sockname")[1]

    server_secondary = AsyncIOOSCUDPServer(("127.0.0.1", 0), disp_secondary, loop)
    transport_secondary, _ = await server_secondary.create_serve_endpoint()
    port_secondary = transport_secondary.get_extra_info("sockname")[1]

    midi_in = TriggerMidiIn()
    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_dst_ports=[port_primary, port_secondary],
        osc_port_selector=lambda msg: port_secondary,
    )

    await forwarder.start()

    midi_in.emit(([0xB3, 7, 120], 0.0))

    address, payload = await asyncio.wait_for(messages_secondary.get(), timeout=1)
    assert address == "/mftd/cc"
    assert payload == [3, 7, 120]

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(messages_primary.get(), timeout=0.1)

    await forwarder.stop()
    transport_primary.close()
    transport_secondary.close()


def test_midi_to_osc_end_to_end() -> None:
    asyncio.run(_run_midi_to_osc_end_to_end())
