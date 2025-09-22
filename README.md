# mftd

### Build

Generate inlined source using [`inline-importer`](https://inline-importer.readthedocs.io/en/latest/):

```shell
rm dist/mftd.py; inline-python -p mftd -e mftd/__init__.py -o dist/mftd.py
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

### MIDI ↔ OSC Bridge

The `MidiToOscForwarder` and `MidiOscBridge` helpers make it easy to forward
incoming MIDI Control Change events to OSC receivers. Multiple OSC destination
ports can be configured by passing a sequence to `osc_dst_ports` along with an
optional `osc_port_selector` callback. The selector receives the decoded
`(channel, controller, value)` tuple and chooses the destination port for each
message, enabling per-controller routing across OSC services.

Use `run_bridge.py` to run the bidirectional bridge from the command line. The
script accepts repeated `--osc-dst-port` options to target multiple receivers
and will keep retrying when the Midi Fighter Twister is not yet connected,
making it suitable for running alongside live performance setups.

Ensure that the `mftMidiSystemIn` CHOP is configured to your device and both
operators have their **Active** parameter enabled. Incoming SysEx messages will
then appear in the `mftMidiEvent` table so calls like
`MftSysexApi.get_device_config()` can succeed.

### Animation Example

The controller supports simple indicator and RGB animations via Control Change
messages on MIDI channel 2. Animation values and brightness levels are exposed
through the `AnimationValues`, `IndicatorBrightnessValues` and
`RgbBrightnessValues` enums. Use `set_encoder_animation()` to trigger an
animation or the convenience helpers `set_indicator_brightness()` and
`set_rgb_brightness()` for per-encoder brightness control.

```python
from mftd import (
    MidiFighterTwister,
    EncoderAnimation,
    EncoderIndicatorBrightness,
    EncoderRgbBrightness,
)

with MidiFighterTwister() as mft:
    # Set encoder 1 indicator to maximum brightness
    mft.set_encoder_indicator_brightness(
        0,
        EncoderIndicatorBrightness.MAX,
    )

    # Dim the RGB LED for encoder 1
    mft.set_encoder_rgb_brightness(
        0,
        EncoderRgbBrightness.MID,
    )
```
