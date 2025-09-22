from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from typing import Any, Iterable

from mftd.midi import create_midi_input, create_midi_output


def _is_control_change(status_byte: int) -> bool:
    return (status_byte & 0xF0) == 0xB0


class MidiToOscForwarder:
    """Forward MIDI Control Change messages to an OSC endpoint."""

    def __init__(
        self,
        *,
        osc_dst_host: str = "127.0.0.1",
        osc_dst_port: int = 9000,
        osc_dst_ports: Sequence[int] | None = None,
        osc_dst_addr: str = "/mftd/cc",
        midi_in: Any | None = None,
        osc_client: Any | None = None,
        osc_port_selector: Callable[[tuple[int, int, int]], int] | None = None,
        osc_client_factory: Callable[[str, int], Any] | None = None,
    ) -> None:
        self._osc_dst_host = osc_dst_host
        self._osc_dst_ports = self._normalise_ports(osc_dst_ports, osc_dst_port)
        self._osc_dst_port = self._osc_dst_ports[0]
        self._osc_dst_addr = osc_dst_addr
        self._midi_in = midi_in
        self._osc_port_selector = osc_port_selector
        self._osc_client_factory = osc_client_factory
        self._osc_clients: dict[int, Any] = {}
        if osc_client is not None:
            self._osc_clients[self._osc_dst_ports[0]] = osc_client
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False

    @staticmethod
    def _normalise_ports(
        osc_dst_ports: Sequence[int] | None, osc_dst_port: int
    ) -> tuple[int, ...]:
        ports: Iterable[int]
        if osc_dst_ports is None:
            ports = (osc_dst_port,)
        else:
            ports = osc_dst_ports

        deduped: list[int] = []
        for port in ports:
            int_port = int(port)
            if int_port not in deduped:
                deduped.append(int_port)

        if not deduped:
            raise ValueError("At least one OSC destination port must be provided")

        return tuple(deduped)

    @property
    def osc_dst_host(self):
        return self._osc_dst_host

    @property
    def osc_dst_port(self):
        return self._osc_dst_ports[0]

    @property
    def osc_dst_ports(self) -> tuple[int, ...]:
        return self._osc_dst_ports

    @property
    def osc_dst_addr(self):
        return self._osc_dst_addr

    async def start(self) -> None:
        if self._running:
            return

        if self._midi_in is None:
            self._midi_in = create_midi_input()
        if self._midi_in is None:
            raise RuntimeError("MIDI input is not available.")

        missing_ports = [
            port for port in self._osc_dst_ports if port not in self._osc_clients
        ]

        if missing_ports:
            if self._osc_client_factory is None:
                from pythonosc import udp_client

                def default_factory(host: str, port: int) -> Any:
                    return udp_client.SimpleUDPClient(host, port)

                factory = default_factory
            else:
                factory = self._osc_client_factory

            for port in missing_ports:
                self._osc_clients[port] = factory(self._osc_dst_host, port)

        self._loop = asyncio.get_running_loop()
        self._midi_in.set_callback(self._handle_midi_message)
        self._running = True

    async def stop(self) -> None:
        if not self._running:
            return

        if self._midi_in is not None:
            cancel_callback: Callable[[], None] | None = getattr(
                self._midi_in, "cancel_callback", None
            )
            if cancel_callback:
                cancel_callback()
            close_port: Callable[[], None] | None = getattr(
                self._midi_in, "close_port", None
            )
            if close_port:
                close_port()

        self._running = False

    def _handle_midi_message(
        self, event: tuple[Sequence[int], float] | None, _: Any
    ) -> None:
        if not event:
            return

        print("Received MIDI event:", event)
        message, _delta = event
        if not message:
            return

        print("Received MIDI message:", message)
        status = message[0]
        if not _is_control_change(status):
            return

        if len(message) < 3:
            return

        channel = status & 0x0F
        controller = int(message[1]) & 0x7F
        value = int(message[2]) & 0x7F

        if self._loop is None or not self._osc_clients:
            return

        payload = [channel, controller, value]
        target_port = self._resolve_destination_port((channel, controller, value))
        if target_port is None:
            return

        client = self._osc_clients.get(target_port)
        if client is None:
            print(
                "OSC port selector returned unknown port:",
                target_port,
                "available ports:",
                sorted(self._osc_clients.keys()),
            )
            return

        def _send() -> None:
            client.send_message(self._osc_dst_addr, payload)

        self._loop.call_soon_threadsafe(_send)

    def _resolve_destination_port(
        self, message: tuple[int, int, int]
    ) -> int | None:
        if len(self._osc_dst_ports) == 1:
            return self._osc_dst_ports[0]

        if self._osc_port_selector is None:
            return self._osc_dst_ports[0]

        try:
            selected_port = self._osc_port_selector(message)
        except Exception as exc:  # pragma: no cover - defensive logging
            print("OSC port selector raised an exception:", exc)
            return None

        if selected_port is None:
            return None

        try:
            return int(selected_port)
        except (TypeError, ValueError):
            print("OSC port selector returned an invalid port:", selected_port)
            return None


class OscToMidiForwarder:
    """Forward OSC messages to the Midi Fighter Twister."""

    def __init__(
        self,
        *,
        osc_src_host: str = "127.0.0.1",
        osc_src_port: int = 9001,
        osc_src_addr: str = "/mftd/cc",
        midi_out: Any | None = None,
    ) -> None:
        self._osc_listen_host = osc_src_host
        self._osc_listen_port = osc_src_port
        self._osc_listen_addr = osc_src_addr
        self._midi_out = midi_out
        self._loop: asyncio.AbstractEventLoop | None = None
        self._server = None
        self._transport = None
        self._protocol = None
        self._running = False

    @property
    def osc_src_host(self):
        return self._osc_listen_host

    @property
    def osc_src_port(self):
        return self._osc_listen_port

    @property
    def osc_src_addr(self):
        return self._osc_listen_addr

    async def start(self) -> None:
        if self._running:
            return

        if self._midi_out is None:
            self._midi_out = create_midi_output()
        if self._midi_out is None:
            raise RuntimeError("MIDI output is not available.")

        from pythonosc import dispatcher, osc_server

        self._loop = asyncio.get_running_loop()
        disp = dispatcher.Dispatcher()
        disp.map(self._osc_listen_addr, self.handle_osc_message)

        self._server = osc_server.AsyncIOOSCUDPServer(
            (self._osc_listen_host, self._osc_listen_port), disp, self._loop
        )
        self._transport, self._protocol = await self._server.create_serve_endpoint()
        self._running = True

    async def stop(self) -> None:
        if not self._running:
            return

        if self._transport is not None:
            self._transport.close()
            self._transport = None

        self._server = None

        if self._midi_out is not None:
            close_port: Callable[[], None] | None = getattr(
                self._midi_out, "close_port", None
            )
            if close_port:
                close_port()

        self._running = False

    def handle_osc_message(self, address: str, *args: Any) -> None:
        if self._midi_out is None:
            return

        if address != self._osc_listen_addr:
            return

        if len(args) < 3:
            return

        channel = int(args[0]) & 0x0F
        controller = int(args[1]) & 0x7F
        value = int(args[2]) & 0x7F

        status = 0xB0 | channel
        self._midi_out.send_message([status, controller, value])

    @property
    def listening_port(self) -> int | None:
        if self._transport is None:
            return None
        sockname = self._transport.get_extra_info("sockname")
        if not sockname:
            return None
        return int(sockname[1])


class MidiOscBridge:
    """Bidirectional bridge between MIDI and OSC for the Twister."""

    def __init__(
        self,
        *,
        midi_in: Any | None = None,
        midi_out: Any | None = None,
        osc_dst_host: str = "127.0.0.1",
        osc_dst_port: int = 9000,
        osc_dst_ports: Sequence[int] | None = None,
        osc_src_host: str = "127.0.0.1",
        osc_src_port: int = 9001,
        osc_address: str = "/mftd/cc",
        osc_port_selector: Callable[[tuple[int, int, int]], int] | None = None,
        osc_client_factory: Callable[[str, int], Any] | None = None,
    ) -> None:
        self.midi_to_osc = MidiToOscForwarder(
            osc_dst_host=osc_dst_host,
            osc_dst_port=osc_dst_port,
            osc_dst_ports=osc_dst_ports,
            osc_dst_addr=osc_address,
            midi_in=midi_in,
            osc_port_selector=osc_port_selector,
            osc_client_factory=osc_client_factory,
        )
        self.osc_to_midi = OscToMidiForwarder(
            osc_src_host=osc_src_host,
            osc_src_port=osc_src_port,
            osc_src_addr=osc_address,
            midi_out=midi_out,
        )

    async def start(self) -> None:
        await asyncio.gather(
            self.midi_to_osc.start(),
            self.osc_to_midi.start(),
        )

    async def stop(self) -> None:
        await asyncio.gather(
            self.midi_to_osc.stop(),
            self.osc_to_midi.stop(),
        )
