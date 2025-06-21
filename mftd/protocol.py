from __future__ import annotations

from typing import Protocol, Sequence


class MidiPort(Protocol):
    """Device management operations."""

    def get_port_count(self) -> int:
        """Return the number of available MIDI ports."""
        pass

    def get_port_name(self, port: int) -> str:
        """Return the name of the MIDI port."""
        pass

    def open_port(self, port: int) -> None:
        """Open a MIDI port for input or output."""
        pass

    def close_port(self) -> None:
        """Close the currently open MIDI port."""
        pass

    def ignore_types(self, sysex: bool, timing: bool, active_sense: bool) -> None:
        """Ignore specific types of MIDI messages."""
        pass

    def __del__(self):
        self.close_port()  # Fallback cleanup


class MidiInput(MidiPort, Protocol):
    """Core MIDI input operations."""

    def get_message(self) -> tuple[Sequence[int], float] | None:
        """Retrieve a MIDI message from the input port."""
        pass


class MidiOutput(MidiPort, Protocol):
    """Core MIDI output operations."""

    def send_message(self, message: Sequence[int]) -> None:
        """Send a MIDI message to the output port."""
        pass
