import sys
import types
import builtins

import pytest

from mftd.midi import create_midi_input, TdMidiInput


class DummyPar:
    def __init__(self):
        self.active = False


class DummyCell:
    def __init__(self, val):
        self.val = val


class MidiEventDAT:
    def __init__(self, name):
        self.name = name
        self.par = DummyPar()
        self.rows = []

    @property
    def numRows(self):
        return len(self.rows)

    def __getitem__(self, key):
        row, col = key
        if col == "bytes":
            return DummyCell(self.rows[row])
        raise KeyError

    def add_row(self, val):
        self.rows.append(val)


class MidiInCHOP:
    def __init__(self, name):
        self.name = name
        self.par = DummyPar()


class StubOP:
    def __init__(self, name):
        self.name = name
        self.children = {}

    def op(self, name):
        return self.children.get(name)

    def create(self, type_name, name):
        if type_name == "midieventDAT":
            child = MidiEventDAT(name)
        elif type_name == "midiinCHOP":
            child = MidiInCHOP(name)
        else:
            child = StubOP(name)
        self.children[name] = child
        return child


@pytest.fixture
def td_stub(monkeypatch):
    root = StubOP("project1")
    td_module = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "td", td_module)

    def op_fn(name):
        if name == "/project1":
            return root
        return root.op(name)

    monkeypatch.setattr(builtins, "op", op_fn, raising=False)
    yield root
    monkeypatch.setattr(builtins, "op", lambda x: None, raising=False)
    monkeypatch.delitem(sys.modules, "td", raising=False)


def test_td_midi_input_creation(monkeypatch, td_stub):
    monkeypatch.setattr("mftd.midi.is_rtmidi_available", lambda: False)
    midi_in = create_midi_input()
    assert isinstance(midi_in, TdMidiInput)
    assert "mftMidiSystemIn" in td_stub.children
    assert "mftMidiEvent" in td_stub.children
    assert td_stub.children["mftMidiSystemIn"].par.active
    assert td_stub.children["mftMidiEvent"].par.active


def test_td_midi_get_message(monkeypatch, td_stub):
    monkeypatch.setattr("mftd.midi.is_rtmidi_available", lambda: False)
    midi_in = create_midi_input()
    dat = midi_in.midi_event_dat
    dat.add_row("0xF0 0x01 0x02 0xF7")
    msg = midi_in.get_message()
    assert msg[0] == [0xF0, 0x01, 0x02, 0xF7]
