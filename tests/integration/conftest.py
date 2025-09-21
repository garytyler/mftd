import sys
import types

import pytest

from mftd.protocol import MidiOutput, MidiInput


class FakeMidiIn(MidiInput):
    def __init__(self):
        self.messages = []
        self.opened = False
        self.callback = None

    def get_port_count(self):
        return 1

    def get_port_name(self, index):
        return "Midi Fighter Twister"

    def open_port(self, index):
        self.opened = True

    def ignore_types(self, *args):
        pass

    def get_message(self):
        if self.messages:
            return self.messages.pop(0)
        return None

    def close_port(self):
        self.opened = False

    def set_callback(self, callback, data=None):
        self.callback = callback

    def cancel_callback(self):
        self.callback = None


class FakeMidiOut(MidiOutput):
    def __init__(self):
        self.messages = []
        self.opened = False
        self.callback = None

    def get_port_count(self):
        return 1

    def get_port_name(self, index):
        return "Midi Fighter Twister"

    def open_port(self, index):
        self.opened = True

    def send_message(self, msg):
        self.messages.append(msg)

    def close_port(self):
        self.opened = False

    def set_callback(self, callback, data=None):
        self.callback = callback

    def cancel_callback(self):
        self.callback = None


@pytest.fixture(autouse=True)
def rtmidi_stub(monkeypatch):
    stub = types.SimpleNamespace(MidiIn=FakeMidiIn, MidiOut=FakeMidiOut)
    monkeypatch.setitem(sys.modules, "rtmidi", stub)
    yield stub
