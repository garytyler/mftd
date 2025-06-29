from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import IntEnum
from collections.abc import Sequence
from typing import (
    Any,
    ClassVar,
    Type,
    Mapping,
    TypeVar,
    get_type_hints,
)

Self = TypeVar("Self", bound="FromSysexMixin")


class FromSysexMixin:
    """Base class for objects created from SysEx messages."""

    _HEADER: ClassVar[Sequence[int]]
    _DATA_CLASS: ClassVar[type]
    _MAP: ClassVar[Mapping[int, str]]

    def __init_subclass__(cls, **kwargs):
        """Create the address map for the provided dataclass."""
        super().__init_subclass__(**kwargs)

        data_cls = getattr(cls, "_DATA_CLASS", None)
        if data_cls is None or not is_dataclass(data_cls):
            raise TypeError(f"{cls.__name__} must define a dataclass in _DATA_CLASS")

        cls._MAP = {
            f.metadata["addr"]: f.name
            for f in fields(data_cls)
            if "addr" in f.metadata
        }

    @classmethod
    def _transform_sysex_in(cls: Type[Self], field_name: str, value: Any) -> Any:
        """Hook to sysex a single value from a SysEx message."""
        return value

    def __init__(self, pkt: Sequence[int]):
        cls = self.__class__

        if len(pkt) < 3 or pkt[0] != 0xF0 or pkt[-1] != 0xF7:
            raise ValueError("not a SysEx packet")
        if list(pkt[1 : 1 + len(cls._HEADER)]) != list(cls._HEADER):
            raise ValueError("header mismatch")

        body = pkt[1 + len(cls._HEADER) : -1]
        if len(body) % 2:
            raise ValueError("addr/val pairs must be even length")

        it = iter(body)
        kwargs: dict[str, Any] = {}
        for addr, val in zip(it, it):
            if addr in cls._MAP:
                field_name = cls._MAP[addr]
                transformed_val = cls._transform_sysex_in(field_name, val)
                kwargs[field_name] = transformed_val

        missing = set(cls._MAP.values()) - kwargs.keys()
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")

        hints = get_type_hints(cls._DATA_CLASS)
        for name, value in kwargs.items():
            if name in hints:
                field_type = hints[name]
                try:
                    if issubclass(field_type, IntEnum):
                        kwargs[name] = field_type(value)
                except TypeError:
                    pass

        self.data = cls._DATA_CLASS(**kwargs)

    @classmethod
    def from_sysex(cls: Type[Self], pkt: Sequence[int]) -> Self:
        return cls(pkt)


class ToSysexMixin(Sequence[int]):
    """Base class for objects representing outgoing SysEx commands."""

    _HEADER: ClassVar[Sequence[int]]
    data: Any
    _msg: tuple[int, ...]

    def _transform_sysex_out(self, field_name: str, value: Any) -> Any:
        """Hook to modify a single value for a SysEx message."""
        return value

    def __init__(self, data: Any):
        if not is_dataclass(data):
            raise TypeError("data attribute must be a dataclass instance")
        self.data = data

        payload = []
        for f in fields(self.data):
            if "addr" in f.metadata:
                addr = f.metadata["addr"]
                name = f.name
                value = getattr(self.data, name)

                value = self._transform_sysex_out(name, value)

                if isinstance(value, IntEnum):
                    value = value.value

                payload.append(addr)
                payload.append(int(value))

        self._msg = (*self._HEADER, *payload, 0xF7)

    def __len__(self) -> int:  # type: ignore[override]
        return len(self._msg)

    def __getitem__(self, index: int) -> int:  # type: ignore[override]
        return self._msg[index]

    def __iter__(self):  # type: ignore[override]
        return iter(self._msg)

    def to_sysex(self) -> tuple[Sequence[int], ...]:
        """Return the generated SysEx message."""
        return (self._msg,)
