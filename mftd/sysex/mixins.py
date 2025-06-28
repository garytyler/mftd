from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import IntEnum
from typing import Any, ClassVar, Type, Sequence, Mapping, TypeVar

Self = TypeVar("Self", bound="FromSysexMixin")


class FromSysexMixin:
    """A mixin for dataclasses that can be created from SysEx messages."""

    _HEADER: ClassVar[Sequence[int]]
    _MAP: ClassVar[Mapping[int, str]]

    def __init_subclass__(cls, **kwargs):
        """
        Creates the address-to-field-name map (_MAP)
        for any subclass by finding the first non-mixin, dataclass parent.
        """
        super().__init_subclass__(**kwargs)
        for base in cls.__mro__:
            if is_dataclass(base) and not issubclass(base, FromSysexMixin):
                cls._MAP = {
                    f.metadata["addr"]: f.name
                    for f in fields(base)
                    if "addr" in f.metadata
                }
                break
        else:
            raise TypeError(f"{cls} does not inherit from a non-mixin dataclass")

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
        kwargs: dict[str, int] = {}
        for addr, val in zip(it, it):
            if addr in cls._MAP:
                field_name = cls._MAP[addr]
                transformed_val = cls._transform_sysex_in(field_name, val)
                kwargs[field_name] = transformed_val

        missing = set(cls._MAP.values()) - kwargs.keys()
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")

        return cls(**kwargs)


class ToSysexMixin:
    """A mixin for dataclasses that can be converted to SysEx messages."""

    _HEADER: ClassVar[Sequence[int]]

    def _transform_sysex_out(self, field_name: str, value: Any) -> Any:
        """Hook to sysex a single value for a SysEx message."""
        return value

    def to_sysex(self) -> tuple[Sequence[int], ...]:
        """
        Converts the dataclass to a sequence of SysEx messages.
        This base implementation creates a single message.
        """
        for base in self.__class__.__mro__:
            if is_dataclass(base) and fields(base):
                data_cls = base
                break
        else:
            raise TypeError(f"Not a data class with fields: {self.__class__}")

        payload = []
        for f in fields(data_cls):
            if "addr" in f.metadata:
                addr = f.metadata["addr"]
                name = f.name
                value = getattr(self, name)

                value = self._transform_sysex_out(name, value)

                if isinstance(value, IntEnum):
                    value = value.value

                payload.append(addr)
                payload.append(int(value))
        sysex_msg = (*self._HEADER, *payload, 0xF7)
        return (sysex_msg,)
