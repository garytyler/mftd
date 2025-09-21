import asyncio

import pytest

from mftd.bridge import MidiToOscForwarder


class FakeMidiIn:
    def __init__(self):
        self.callback = None
        self.cancelled = False
        self.closed = False

    def set_callback(self, callback, data=None):
        self.callback = callback

    def cancel_callback(self):
        self.callback = None
        self.cancelled = True

    def close_port(self):
        self.closed = True


class FakeOscClient:
    def __init__(self, host: str | None = None, port: int | None = None):
        self.sent = []
        self.host = host
        self.port = port

    def send_message(self, address, payload):
        self.sent.append((address, payload))


@pytest.mark.asyncio
async def test_midi_to_osc_forwards_control_change():
    midi_in = FakeMidiIn()
    osc_client = FakeOscClient()
    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_client=osc_client,
        osc_dst_addr="/test/cc",
    )

    await forwarder.start()
    assert midi_in.callback is not None

    midi_in.callback(([0xB2, 10, 64], 0.0), None)
    await asyncio.sleep(0)

    assert osc_client.sent == [("/test/cc", [2, 10, 64])]

    await forwarder.stop()
    assert midi_in.callback is None
    assert midi_in.closed


@pytest.mark.asyncio
async def test_midi_to_osc_routes_to_selected_port():
    midi_in = FakeMidiIn()
    created_clients: dict[int, FakeOscClient] = {}

    def client_factory(host, port):
        client = FakeOscClient(host, port)
        created_clients[port] = client
        return client

    selected: list[tuple[int, int, int]] = []

    def selector(message: tuple[int, int, int]) -> int:
        selected.append(message)
        return 9011

    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_dst_ports=[9010, 9011],
        osc_port_selector=selector,
        osc_client_factory=client_factory,
    )

    await forwarder.start()
    assert set(created_clients) == {9010, 9011}

    midi_in.callback(([0xB5, 22, 7], 0.0), None)
    await asyncio.sleep(0)

    assert selected == [(5, 22, 7)]
    assert created_clients[9011].sent == [("/mftd/cc", [5, 22, 7])]
    assert created_clients[9010].sent == []

    await forwarder.stop()
