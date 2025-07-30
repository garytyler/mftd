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
    AnimationValues,
    IndicatorBrightnessValues,
    RgbBrightnessValues,
)

with MidiFighterTwister() as mft:
    # Set encoder 1 indicator to maximum brightness
    mft.set_indicator_brightness(
        0,
        IndicatorBrightnessValues.MAX,
    )

    # Dim the RGB LED for encoder 1
    mft.set_rgb_brightness(
        0,
        RgbBrightnessValues.MID,
    )
```
