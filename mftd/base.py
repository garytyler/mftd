from __future__ import annotations

from dataclasses import dataclass, fields, asdict
from typing import Any, get_type_hints, TypeVar, Self

T = TypeVar("T", bound="BaseModel")
O = TypeVar("O", bound="BaseModelOut")
I = TypeVar("I", bound="BaseModelIn")


@dataclass
class _BaseModel:
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

    def __post_init__(self) -> None:  # pragma: no cover - executed implicitly
        """Ensure dataclass fields are the correct type."""
        hints = get_type_hints(type(self))
        for f in fields(self):
            field_type = hints.get(f.name, f.type)
            value = getattr(self, f.name)
            super().__setattr__(f.name, self._coerce(value, field_type))

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Coerce attribute ``value`` to its declared type if possible."""
        field_obj = getattr(self, "__dataclass_fields__").get(name)
        if field_obj is not None:
            hints = get_type_hints(type(self))
            field_type = hints.get(field_obj.name, field_obj.type)
            value = self._coerce(value, field_type)
        super().__setattr__(name, value)


@dataclass
class BaseModelIn(_BaseModel):

    def __post_init__(self) -> None:  # pragma: no cover - executed implicitly
        pass


@dataclass
class BaseModelOut(_BaseModel):

    def __post_init__(self) -> None:  # pragma: no cover - executed implicitly
        pass

    @classmethod
    def from_config(cls, config: T) -> Self:
        return cls(**asdict(config))


@dataclass
class BaseModel(_BaseModel):

    @classmethod
    def from_incoming(cls, incoming: I) -> Self:
        return cls(**asdict(incoming))
