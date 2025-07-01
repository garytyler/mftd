from __future__ import annotations

from dataclasses import dataclass, fields
from enum import IntEnum
from typing import Any, get_type_hints, TypeVar, Self, Dict

T = TypeVar("T", bound="BaseModel")
O = TypeVar("O", bound="BaseModelOut")
I = TypeVar("I", bound="BaseModelIn")


@dataclass
class BaseModel:
    """Common dataclass utilities for configuration models."""

    @staticmethod
    def _coerce(value: Any, field_type: Any) -> Any:
        """Return ``value`` converted to ``field_type`` when possible."""
        try:
            origin = getattr(field_type, "__origin__", None)
            if origin is not None:
                return value
            if isinstance(field_type, type) and not isinstance(value, field_type):
                return field_type(value)
        except TypeError:
            pass
        return value

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Coerce attribute ``value`` to its declared type if possible."""
        field_obj = getattr(self, "__dataclass_fields__").get(name)
        if field_obj is not None:
            hints = get_type_hints(type(self))
            field_type = hints.get(field_obj.name, field_obj.type)
            value = self._coerce(value, field_type)
        super().__setattr__(name, value)

    @classmethod
    def transform_incoming(cls, name: str, value: int | IntEnum) -> int | IntEnum:
        return value

    @classmethod
    def from_in_dict(cls, data) -> Self:
        kwargs = {}
        for field in fields(cls):
            try:
                field_addr = field.metadata["addr"]
            except KeyError:
                continue
            try:
                value = data[field_addr]
            except KeyError:
                value = field.default
            else:
                value = cls.transform_incoming(field.name, value)
            kwargs[field.name] = value
        return cls(**kwargs)

    # noinspection PyMethodMayBeStatic
    def transform_outgoing(self, name: str, value: int | IntEnum) -> int | IntEnum:
        return value

    def to_out_dict(self) -> Dict[str, int]:
        result = {}
        for field in fields(self):
            field_addr = field.metadata.get("addr")
            if field_addr is None:
                continue
            value = getattr(self, field.name)
            result[field_addr] = self.transform_outgoing(field.name, int(value))
        return result


# @dataclass
# class BaseModelIn(_BaseModel):
#     pass
#
#
# @dataclass
# class BaseModelOut(_BaseModel):
#     pass
#
#
# @dataclass
# class BaseModel(_BaseModel, Generic[O]):
#     pass
#
#     @dataclass
#     def from_addr_dict(cls, data) -> Self:
#         return cls(**data)
#
#     def to_addr_dict(self):
#         result = {}
#         for field in fields(self):
#             field_addr = field.metadata.get("addr")
#             if field_addr is None:
#                 continue
#             value = getattr(self, field.name)
#             result[field_addr] = value
#         return result
