from __future__ import annotations

import asyncio
import errno
import functools
import inspect
import struct
from collections.abc import Callable, Sequence
from typing import Any

from mftd.midi import create_midi_input, create_midi_output


def _is_control_change(status_byte: int) -> bool:
    return (status_byte & 0xF0) == 0xB0


def _pad_osc_string(value: str) -> bytes:
    data = value.encode("utf-8") + b"\x00"
    padding = (4 - (len(data) % 4)) % 4
    if padding:
        data += b"\x00" * padding
    return data


def _encode_osc_argument(argument: Any) -> tuple[str, bytes]:
    if isinstance(argument, bool):
        return ("T" if argument else "F"), b""
    if isinstance(argument, int) and not isinstance(argument, bool):
        return "i", struct.pack(">i", int(argument))
    if isinstance(argument, float):
        return "f", struct.pack(">f", float(argument))
    if isinstance(argument, str):
        return "s", _pad_osc_string(argument)
    raise TypeError(f"Unsupported OSC argument type: {type(argument)!r}")


def _encode_osc_message(address: str, payload: Sequence[Any]) -> bytes:
    if not address.startswith("/"):
        raise ValueError("OSC address must start with '/'")

    chunks = [_pad_osc_string(address)]
    type_tags = [","]
    arg_chunks: list[bytes] = []

    for argument in payload:
        tag, encoded = _encode_osc_argument(argument)
        type_tags.append(tag)
        if encoded:
            arg_chunks.append(encoded)

    chunks.append(_pad_osc_string("".join(type_tags)))
    chunks.extend(arg_chunks)
    return b"".join(chunks)


class _OscDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(
        self,
        host: str,
        port: int,
        on_error: Callable[[str, int, Exception | None], None] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._on_error = on_error

    def error_received(self, exc: Exception) -> None:  # pragma: no cover - logging only
        if self._on_error is not None:
            self._on_error(self._host, self._port, exc)


class _OscDatagramClient:
    def __init__(self, transport: asyncio.DatagramTransport) -> None:
        self._transport = transport

    def send_message(self, address: str, payload: Sequence[Any]) -> None:
        packet = _encode_osc_message(address, payload)
        self._transport.sendto(packet)

    def send_packet(self, packet: bytes) -> None:
        self._transport.sendto(packet)

    def close(self) -> None:
        self._transport.close()


class MidiToOscForwarder:
    """Forward MIDI Control Change messages to an OSC endpoint."""

    def __init__(
        self,
        *,
        osc_dst_host: str = "127.0.0.1",
        osc_dst_ports: Sequence[int] = (9000,),
        osc_dst_addr: str = "/mftd/cc",
        midi_in: Any | None = None,
        osc_client: Any | None = None,
        osc_port_selector: Callable[[tuple[int, int, int]], int | list[int]]
        | None = None,
        osc_addr_resolver: Callable[[tuple[int, int, int], str], str] | None = None,
        osc_client_factory: Callable[[str, int], Any] | None = None,
    ) -> None:
        self._osc_dst_host = osc_dst_host
        self._osc_dst_ports = self._normalise_ports(osc_dst_ports)
        self._osc_dst_addr = osc_dst_addr
        self._midi_in = midi_in
        self._osc_port_selector = osc_port_selector
        self._osc_address_selector = osc_addr_resolver
        self._osc_client_factory = osc_client_factory
        self._osc_clients: dict[int, Any] = {}
        if osc_client is not None:
            self._osc_clients[self._osc_dst_ports[0]] = osc_client
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False
        self._midi_queue: asyncio.Queue[
            tuple[Sequence[int], float] | None
        ] | None = None
        self._queue_put: Callable[[tuple[Sequence[int], float] | None], None] | None = None
        self._schedule_queue_put: Callable[[tuple[Sequence[int], float] | None], None] | None = None
        self._drain_task: asyncio.Task[None] | None = None
        self._osc_error_reasons: dict[int, str] = {}

    @staticmethod
    def _normalise_ports(osc_dst_ports: Sequence[int]) -> tuple[int, ...]:
        deduped: list[int] = []
        for port in osc_dst_ports:
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

        self._loop = asyncio.get_running_loop()
        await self._ensure_osc_clients()

        self._running = True
        self._midi_queue = asyncio.Queue()
        self._queue_put = self._midi_queue.put_nowait
        self._schedule_queue_put = functools.partial(
            self._loop.call_soon_threadsafe, self._queue_put
        )
        self._drain_task = self._loop.create_task(self._drain_midi_events())
        self._midi_in.set_callback(self._enqueue_midi_event)

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

        if self._drain_task is not None:
            self._running = False
            if self._queue_put is not None:
                self._queue_put(None)
            await self._drain_task
            self._drain_task = None

        if self._midi_queue is not None:
            self._midi_queue = None
        self._queue_put = None
        self._schedule_queue_put = None

        for client in list(self._osc_clients.values()):
            closer: Callable[[], None] | None = getattr(client, "close", None)
            if closer is not None:
                closer()
        self._osc_clients.clear()
        self._osc_error_reasons.clear()
        self._loop = None
        self._running = False

    async def _ensure_osc_clients(self) -> None:
        assert self._loop is not None

        missing_ports = [
            port for port in self._osc_dst_ports if port not in self._osc_clients
        ]

        if not missing_ports:
            return

        for port in missing_ports:
            client = await self._create_osc_client(port)
            self._osc_clients[port] = client

    async def _create_osc_client(self, port: int) -> Any:
        assert self._loop is not None

        if self._osc_client_factory is not None:
            client = self._osc_client_factory(self._osc_dst_host, port)
            if inspect.isawaitable(client):
                return await client  # type: ignore[return-value]
            return client

        transport, _protocol = await self._loop.create_datagram_endpoint(
            lambda: _OscDatagramProtocol(
                self._osc_dst_host, port, self._handle_osc_send_error
            ),
            remote_addr=(self._osc_dst_host, port),
        )
        return _OscDatagramClient(transport)

    def _describe_osc_error(self, exc: Exception | None) -> str:
        if exc is None:
            return "The operating system reported an unspecified UDP send error."

        if isinstance(exc, OSError):
            if exc.errno in {errno.ECONNREFUSED, 61, 10061}:
                return (
                    "No OSC server is listening on the destination port; "
                    "the host rejected the datagram."
                )
            return str(exc)

        return str(exc)

    def _handle_osc_send_error(
        self, host: str, port: int, exc: Exception | None
    ) -> None:  # pragma: no cover - defensive logging
        reason = self._describe_osc_error(exc)
        previous = self._osc_error_reasons.get(port)
        if previous == reason:
            return
        self._osc_error_reasons[port] = reason
        print(
            f"OSC send error to {host}:{port}: {reason}"
        )

    async def _drain_midi_events(self) -> None:
        assert self._midi_queue is not None
        while self._running:
            try:
                event = await self._midi_queue.get()
            except asyncio.CancelledError:
                break

            if event is None:
                break

            self._process_midi_event(event)

    def _enqueue_midi_event(
        self, event: tuple[Sequence[int], float] | None, _: Any
    ) -> None:
        if not event:
            return

        if self._loop is not None:
            try:
                running_loop = asyncio.get_running_loop()
            except RuntimeError:
                running_loop = None
            if running_loop is self._loop:
                self._process_midi_event(event)
                return

        if self._schedule_queue_put is not None:
            self._schedule_queue_put(event)
            return

        if self._queue_put is not None:
            self._queue_put(event)

    def _process_midi_event(self, event: tuple[Sequence[int], float]) -> None:
        message, _delta = event
        if not message:
            return

        status = message[0]
        if not _is_control_change(status):
            return

        if len(message) < 3:
            return

        channel = status & 0x0F
        controller = int(message[1]) & 0x7F
        value = int(message[2]) & 0x7F

        if not self._osc_clients:
            return

        payload = [channel, controller, value]
        message = (channel, controller, value)
        target_ports = self._resolve_destination_ports(message)
        if not target_ports:
            return

        target_address = self._resolve_destination_address(message, self._osc_dst_addr)

        encoded_packet: bytes | None = None
        for target_port in target_ports:
            client = self._osc_clients.get(target_port)
            if client is None:
                print(
                    "OSC port selector returned unknown port:",
                    target_port,
                    "available ports:",
                    sorted(self._osc_clients.keys()),
                )
                continue

            try:
                encoded_packet = self._send_osc_message(
                    client, target_address, payload, encoded_packet
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                print("Failed to send OSC message:", payload)
                print(exc)

    def _send_osc_message(
        self,
        client: Any,
        address: str,
        payload: Sequence[Any],
        encoded_packet: bytes | None,
    ) -> bytes | None:
        if hasattr(client, "send_packet"):
            if encoded_packet is None:
                encoded_packet = _encode_osc_message(address, payload)
            client.send_packet(encoded_packet)
            return encoded_packet

        send_message = getattr(client, "send_message", None)
        if send_message is None:
            raise AttributeError("OSC client does not provide send_message")
        send_message(address, payload)
        return encoded_packet

    def _resolve_destination_ports(
        self, message: tuple[int, int, int]
    ) -> tuple[int, ...]:
        if len(self._osc_dst_ports) == 1:
            return self._osc_dst_ports

        if self._osc_port_selector is None:
            return (self._osc_dst_ports[0],)

        try:
            selected_port = self._osc_port_selector(message)
        except Exception as exc:  # pragma: no cover - defensive logging
            print("OSC port selector raised an exception:", exc)
            return ()

        if selected_port is None:
            return ()

        # Handle both single port (int) and multiple ports (Sequence)
        if isinstance(selected_port, int):
            return (selected_port,)

        # Handle sequence of ports
        try:
            ports = []
            for port in selected_port:
                try:
                    ports.append(int(port))
                except (TypeError, ValueError):
                    print("OSC port selector returned an invalid port:", port)
            return tuple(ports)
        except TypeError:
            # selected_port is not iterable
            print("OSC port selector returned an invalid port:", selected_port)
            return ()

    def _resolve_destination_address(
        self, message: tuple[int, int, int], base_address: str
    ) -> str:
        if self._osc_address_selector is None:
            return base_address

        try:
            selected_address = self._osc_address_selector(message, base_address)
        except Exception as exc:  # pragma: no cover - defensive logging
            print("OSC address resolver raised an exception:", exc)
            return base_address

        if selected_address is None:
            return base_address

        try:
            return str(selected_address)
        except Exception:  # pragma: no cover - defensive logging
            print(
                "OSC address resolver returned an invalid address:",
                selected_address,
            )
            return base_address


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

        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import AsyncIOOSCUDPServer

        self._loop = asyncio.get_running_loop()
        disp = Dispatcher()
        disp.map(self._osc_listen_addr, self.handle_osc_message)

        self._server = AsyncIOOSCUDPServer(
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
        try:
            self._midi_out.send_message([status, controller, value])
        except Exception as exc:  # pragma: no cover - defensive logging
            print("Failed to send MIDI message:", [status, controller, value])
            print(exc)

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
        osc_dst_ports: Sequence[int] = (9000,),
        osc_src_host: str = "127.0.0.1",
        osc_src_port: int = 9001,
        osc_address: str = "/mftd/cc",
        osc_port_selector: Callable[[tuple[int, int, int]], int | list[int]]
        | None = None,
        osc_addr_resolver: Callable[[tuple[int, int, int], str], str] | None = None,
        osc_client_factory: Callable[[str, int], Any] | None = None,
    ) -> None:
        self.midi_to_osc = MidiToOscForwarder(
            osc_dst_host=osc_dst_host,
            osc_dst_ports=osc_dst_ports,
            osc_dst_addr=osc_address,
            midi_in=midi_in,
            osc_port_selector=osc_port_selector,
            osc_addr_resolver=osc_addr_resolver,
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
