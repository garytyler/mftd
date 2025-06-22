# mftd

### Build

Generate inlined source using [`inline-importer`](https://inline-importer.readthedocs.io/en/latest/):

```shell
inline-python -p mftd -e mftd/__init__.py -o dist/mftd.py
```

### TouchDesigner Usage

When running inside TouchDesigner the library uses a `midiinCHOP` and a
`midieventDAT` to communicate with the Midi Fighter Twister. The helper
`create_midi_input()` will automatically create these operators under
`/project1` if they are missing:

```
mftMidiSystemIn  (midiinCHOP)
mftMidiEvent     (midieventDAT)
```

Ensure that the `mftMidiSystemIn` CHOP is configured to your device and both
operators have their **Active** parameter enabled. Incoming SysEx messages will
then appear in the `mftMidiEvent` table so calls like
`MftSysexApi.get_device_config()` can succeed.
