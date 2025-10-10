import asyncio
import contextlib
import sys
import types
from collections.abc import Iterable


class _Dispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, list] = {}

    def map(self, address: str, handler) -> None:
        self._handlers.setdefault(address, []).append(handler)

    def handlers_for(self, address: str) -> list:
        return self._handlers.get(address, [])


class _FakeTransport:
    def __init__(self, server: "_AsyncIOOSCUDPServer") -> None:
        self._server = server

    def get_extra_info(self, name: str):
        if name == "sockname":
            return (self._server.host, self._server.port)
        return None

    def close(self) -> None:
        self._server.close()


class _AsyncIOOSCUDPServer:
    _port_counter = 10000
    _servers: dict[int, "_AsyncIOOSCUDPServer"] = {}

    def __init__(self, address, dispatcher: _Dispatcher, loop: asyncio.AbstractEventLoop):
        self.host, requested_port = address
        if requested_port == 0:
            requested_port = self._next_port()
        self.port = requested_port
        self._dispatcher = dispatcher
        self._loop = loop
        self._queue: asyncio.Queue[tuple[str, list]] = asyncio.Queue()
        self._task: asyncio.Task | None = None
        self._closed = False

    @classmethod
    def _next_port(cls) -> int:
        cls._port_counter += 1
        return cls._port_counter

    async def create_serve_endpoint(self):
        if self.port in self._servers:
            raise OSError(f"Port {self.port} already in use")
        self._servers[self.port] = self
        self._task = self._loop.create_task(self._serve())
        return _FakeTransport(self), object()

    async def _serve(self) -> None:
        try:
            while True:
                address, args = await self._queue.get()
                for handler in list(self._dispatcher.handlers_for(address)):
                    handler(address, *args)
        except asyncio.CancelledError:
            pass

    def enqueue(self, address: str, args: Iterable) -> None:
        if self._closed:
            raise ConnectionError("OSC server is closed")
        self._queue.put_nowait((address, list(args)))

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.port in self._servers:
            del self._servers[self.port]
        if self._task is not None:
            self._task.cancel()

    async def wait_closed(self) -> None:
        if self._task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._task


class _SimpleUDPClient:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    def send_message(self, address: str, payload: Iterable) -> None:
        server = _AsyncIOOSCUDPServer._servers.get(self._port)
        if server is None:
            raise ConnectionRefusedError(f"No OSC server listening on {self._host}:{self._port}")
        server._loop.call_soon_threadsafe(server.enqueue, address, list(payload))


_pythonosc = types.ModuleType("pythonosc")
_dispatcher_mod = types.ModuleType("pythonosc.dispatcher")
_dispatcher_mod.Dispatcher = _Dispatcher

_osc_server_mod = types.ModuleType("pythonosc.osc_server")
_osc_server_mod.AsyncIOOSCUDPServer = _AsyncIOOSCUDPServer

_udp_client_mod = types.ModuleType("pythonosc.udp_client")
_udp_client_mod.SimpleUDPClient = _SimpleUDPClient

_pythonosc.dispatcher = _dispatcher_mod
_pythonosc.osc_server = _osc_server_mod
_pythonosc.udp_client = _udp_client_mod

sys.modules.setdefault("pythonosc", _pythonosc)
sys.modules.setdefault("pythonosc.dispatcher", _dispatcher_mod)
sys.modules.setdefault("pythonosc.osc_server", _osc_server_mod)
sys.modules.setdefault("pythonosc.udp_client", _udp_client_mod)
