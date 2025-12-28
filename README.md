# mftd

A thin, adaptable API for integrating [Midi Fighter Twister](https://www.midifighter.com/#Twister) midi controllers in Touch Designer projects.

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
