from __future__ import annotations

import sys
import types

from mftd import constants, midi
from mftd.protocol import MidiInput, MidiOutput


class MissingMidiIn(MidiInput):
    def __init__(self) -> None:
        self.opened = False

    def get_port_count(self) -> int:
        return 1

    def get_port_name(self, index: int) -> str:
        assert index == 0
        return "Some Other Controller"

    def open_port(self, port: int) -> None:
        self.opened = True

    def close_port(self) -> None:
        self.opened = False

    def ignore_types(self, sysex: bool, timing: bool, active_sense: bool) -> None:
        pass

    def get_message(self):
        return None


class MissingMidiOut(MidiOutput):
    def __init__(self) -> None:
        self.opened = False
        self.messages: list[list[int]] = []

    def get_port_count(self) -> int:
        return 1

    def get_port_name(self, index: int) -> str:
        assert index == 0
        return "Some Other Controller"

    def open_port(self, port: int) -> None:
        self.opened = True

    def close_port(self) -> None:
        self.opened = False

    def ignore_types(self, sysex: bool, timing: bool, active_sense: bool) -> None:
        pass

    def send_message(self, message):
        self.messages.append(list(message))


def test_create_midi_helpers_return_none_when_device_missing(monkeypatch):
    stub = types.SimpleNamespace(MidiIn=MissingMidiIn, MidiOut=MissingMidiOut)
    monkeypatch.setitem(sys.modules, "rtmidi", stub)

    midi_in = midi.create_midi_input()
    midi_out = midi.create_midi_output()

    assert midi_in is None
    assert midi_out is None

    # Guard to ensure the test is meaningful if the device constant changes.
    assert constants.DEVICE_NAME not in MissingMidiIn().get_port_name(0)
