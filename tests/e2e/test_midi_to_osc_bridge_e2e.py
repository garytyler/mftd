import asyncio

import pytest

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

    class CaptureProtocol(asyncio.DatagramProtocol):
        def __init__(self, target_queue: asyncio.Queue):
            self._queue = target_queue

        def datagram_received(self, data: bytes, _addr):
            self._queue.put_nowait(data)

    def decode_packet(packet: bytes) -> tuple[str, list[int]]:
        def read_padded_string(offset: int) -> tuple[str, int]:
            end = packet.index(0, offset)
            value = packet[offset:end].decode("utf-8")
            offset = (end + 4) & ~0x03
            return value, offset

        address, cursor = read_padded_string(0)
        type_tags, cursor = read_padded_string(cursor)
        values: list[int] = []
        for tag in type_tags[1:]:
            if tag == "i":
                values.append(int.from_bytes(packet[cursor:cursor + 4], "big", signed=True))
                cursor += 4
        return address, values

    transport_primary, _ = await loop.create_datagram_endpoint(
        lambda: CaptureProtocol(messages_primary), local_addr=("127.0.0.1", 0)
    )
    port_primary = transport_primary.get_extra_info("sockname")[1]

    transport_secondary, _ = await loop.create_datagram_endpoint(
        lambda: CaptureProtocol(messages_secondary), local_addr=("127.0.0.1", 0)
    )
    port_secondary = transport_secondary.get_extra_info("sockname")[1]

    midi_in = TriggerMidiIn()
    forwarder = MidiToOscForwarder(
        midi_in=midi_in,
        osc_dst_ports=[port_primary, port_secondary],
        osc_port_selector=lambda msg: port_secondary,
    )

    await forwarder.start()

    midi_in.emit(([0xB3, 7, 120], 0.0))

    packet = await asyncio.wait_for(messages_secondary.get(), timeout=1)
    address, payload = decode_packet(packet)
    assert address == "/mftd/cc"
    assert payload == [3, 7, 120]

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(messages_primary.get(), timeout=0.1)

    await forwarder.stop()
    transport_primary.close()
    transport_secondary.close()


def test_midi_to_osc_end_to_end() -> None:
    asyncio.run(_run_midi_to_osc_end_to_end())
