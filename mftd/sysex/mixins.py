from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import IntEnum
from typing import (
    Any,
    ClassVar,
    Type,
    Sequence,
    Mapping,
    TypeVar,
    get_type_hints,
)

Self = TypeVar("Self", bound="FromSysexMixin")


class FromSysexMixin:
    """Mixin for classes that can be created from SysEx messages."""

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

    @classmethod
    def from_sysex(cls: Type[Self], pkt: Sequence[int]) -> Self:
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

        data_instance = cls._DATA_CLASS(**kwargs)
        return cls(data_instance)


class ToSysexMixin:
    """Mixin for classes that convert dataclasses to SysEx messages."""

    _HEADER: ClassVar[Sequence[int]]
    data: Any

    def _transform_sysex_out(self, field_name: str, value: Any) -> Any:
        """Hook to modify a single value for a SysEx message."""
        return value

    def to_sysex(self) -> tuple[Sequence[int], ...]:
        """Convert the stored dataclass to a sequence of SysEx messages."""
        if not is_dataclass(self.data):
            raise TypeError("data attribute must be a dataclass instance")

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

        sysex_msg = (*self._HEADER, *payload, 0xF7)
        return (sysex_msg,)
