# mftd

A thin, adaptable API for programatically configuring [Midi Fighter Twister](https://www.midifighter.com/#Twister) midi controllers, and integrating them in Touch Designer projects.

### Firmware support

**0.3.0 and later target the 2026 firmware** (build `2026-06-01` or newer — the
Midi Fighter Utility gates the same behaviour on `fw_version >= 0x20230c11`).

That release renumbered two enums *by insertion*, so running 0.3.0 against
older firmware fails silently rather than loudly — the stale value selects a
different, valid function:

| Value | Pre-2026 meaning | 2026 meaning |
| ----- | ---------------- | ------------ |
| `EncoderSwitchActionType` 6 | Shift Encoder (Hold) | Encoder Fine Adjust |
| `SideSwitchAction` 12 | Cycle Bank | Bank 2 |

Use 0.2.0 for pre-2026 firmware. 0.3.0 also adds device config addresses
33–38 (colour map, animation channels, sleep timer and animation, bank change
animations), which older firmware does not report — `get_device_config()`
raises on a response missing any declared address.

### Build

Generate inlined source using [`inline-importer`](https://inline-importer.readthedocs.io/en/latest/):

```shell
# Prepare destination
rm -f dist/mftd.py
mkdir -p dist

# Build
inline-python -p mftd -e mftd/__init__.py -o dist/mftd.py
```

### Touch Designer Usage

When running inside TouchDesigner the library uses a `midioutCHOP` named `midiOut` to communicate with the Midi Fighter Twister. The library will create this operator if it is missing.
