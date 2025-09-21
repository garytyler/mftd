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
    def __init__(self):
        self.sent = []

    def send_message(self, address, payload):
        self.sent.append((address, payload))


@pytest.mark.asyncio
async def test_midi_to_osc_forwards_control_change():
    midi_in = FakeMidiIn()
    osc_client = FakeOscClient()
    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_client=osc_client,
        osc_address="/test/cc",
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
async def test_midi_to_osc_fans_out_to_configured_clients():
    midi_in = FakeMidiIn()
    primary_client = FakeOscClient()
    extra_client = FakeOscClient()

    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_client=primary_client,
        osc_address="/test/cc",
        fanout={10: [extra_client]},
    )

    await forwarder.start()

    midi_in.callback(([0xB0, 10, 99], 0.0), None)
    await asyncio.sleep(0)

    expected = [("/test/cc", [0, 10, 99])]
    assert primary_client.sent == expected
    assert extra_client.sent == expected

    await forwarder.stop()
