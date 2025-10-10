# Performance improvement opportunities

This document summarises optimisation ideas for the current MIDI ⇄ OSC bridge
implementation. The goal is to improve message throughput and latency without
redesigning the program from scratch.

## Consider tighter event-loop integration
- The bridge currently mixes RtMidi callbacks with the asyncio loop by posting
  work with `call_soon_threadsafe`. Establishing the MIDI input on the asyncio
  thread (via `asyncio.to_thread` or a background task that drains a
  `queue.SimpleQueue`) would let the handler run directly on the loop and avoid
  cross-thread hops for each message, while preserving the existing public
  interface.【F:mftd/bridge.py†L97-L169】
- Likewise, using an `asyncio.DatagramTransport` for OSC output (instead of the
  python-osc client) would allow writing to sockets with `transport.sendto`
  directly from the loop without leaving the asyncio concurrency model. This can
  be done behind a thin adapter so callers still interact with the same
  high-level API.【F:mftd/bridge.py†L83-L169】

## Reduce per-message scheduling overhead
- `MidiToOscForwarder._handle_midi_message` currently schedules a separate
  `call_soon_threadsafe` for every OSC port, and also allocates a closure for
  each send (`_send`). Collapsing this into a single loop that is scheduled once
  per MIDI event (or even sending synchronously from the callback when it is
  already running on the event loop thread) would reduce the number of context
  switches and object allocations.【F:mftd/bridge.py†L151-L169】
- Switching from the nested function to a small helper method allows reuse of a
  pre-created `functools.partial` or direct `call_soon_threadsafe` of the method,
  eliminating repeated closure construction.【F:mftd/bridge.py†L151-L169】

## Avoid repeated OSC address work for static mappings
- `MessageRouter.getAddress` builds string keys, performs dictionary lookups and
  mutates the interpreter mapping on every message. Caching the resolved address
  per `(channel, index)` pair – or precomputing the static pieces at startup –
  would eliminate repeated string formatting, dictionary lookups, and per-call
  mutations.【F:run_bridge.py†L58-L72】
- The method also mutates the shared `mapping` dict (`mapping["index"] = …` and
  `mapping["loc2"] = …`), which may add unnecessary locking or copy-on-write if
  multiple callbacks touch it. Keeping an immutable template and copying only
  when something actually changes can be cheaper.【F:run_bridge.py†L65-L70】

## Streamline OSC client usage
- `SimpleUDPClient.send_message` encodes OSC messages on every call. Providing a
  custom `osc_client_factory` that reuses a pre-built message buffer or uses a
  lightweight socket wrapper would reduce per-message allocations and Python
  function calls while keeping the same API surface.【F:mftd/bridge.py†L83-L169】
- If OSC destinations rarely change, keep a local reference to the client
  objects inside `_handle_midi_message` (e.g. turn the dictionary into a tuple
  aligned with `osc_dst_ports`) to avoid dictionary lookups for every packet.
  This keeps the existing configuration API but removes a hash-table lookup per
  message.【F:mftd/bridge.py†L30-L169】

## Cut down on defensive work in the hot path
- `_resolve_destination_ports` rebuilds tuples on every message when multiple
  ports are chosen. Precomputing common selections (e.g. target index → tuple of
  destination ports) or returning slices of a cached structure avoids repeated
  tuple and list creation.【F:mftd/bridge.py†L171-L205】
- The current handler converts controller/value bytes with `int()` even though
  the values are already integers. Dropping the redundant conversions and bit
  masks (after validating upstream) reduces arithmetic and keeps the original
  semantics.【F:mftd/bridge.py†L133-L138】

## Reduce logging and startup probes in production runs
- `create_midi_input` prints the name of every port during discovery. Turning
  this into debug logging or gating it behind a flag removes a noticeable amount
  of I/O when starting the bridge repeatedly.【F:mftd/midi.py†L53-L75】
- Both `create_midi_input` and `create_midi_output` call `is_rtmidi_available`,
  which instantiates a temporary `MidiIn` every time. Caching the discovery
  result or attempting the import only once avoids repeated device creation when
  reconnecting.【F:mftd/midi.py†L48-L120】

These changes can be pursued independently and should keep the current bridge
structure intact while targeting the dominant costs observed in the hot paths.

## Test-only pythonosc stub
- The lightweight `pythonosc` stub that lives in the test fixture only affects
  the unit-test environment. It replaces network and encoding work with simple
  in-memory queues so that tests can run without the third-party dependency,
  but production code continues to import the real library. As a result, this
  change does not alter the bridge's runtime performance profile; it just
  shortens and simplifies the test setup.【F:tests/conftest.py†L1-L106】
