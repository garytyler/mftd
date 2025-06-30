from __future__ import annotations

from dataclasses import fields, replace
from typing import Any, Callable, ClassVar, Mapping, Self, get_type_hints


class BaseModel:
    """Common dataclass utilities for configuration models."""

    # Mapping of field name to callable used when constructing an instance from
    # device data.
    _inbound_transforms: ClassVar[Mapping[str, Callable[[Any], Any]]] = {}

    # Mapping of field name to callable used when preparing an instance for
    # transmission to the device.
    _outbound_transforms: ClassVar[Mapping[str, Callable[[Any], Any]]] = {}

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
            super().__setattr__(f.name, self._coerce(getattr(self, f.name), field_type))

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Coerce attribute ``value`` to its declared type if possible."""
        field_obj = next((f for f in fields(self) if f.name == name), None)
        if field_obj is not None:
            hints = get_type_hints(type(self))
            field_type = hints.get(field_obj.name, field_obj.type)
            value = self._coerce(value, field_type)
        super().__setattr__(name, value)

    def to_device(self) -> Self:
        """Return a new instance with outbound transforms applied."""
        data = {}
        for f in fields(self):
            val = getattr(self, f.name)
            transform = self._outbound_transforms.get(f.name)
            if transform:
                val = transform(val)
            data[f.name] = val
        return replace(self, **data)

    @classmethod
    def from_device(cls, data: Mapping[str, Any]) -> Self:
        """Create an instance from raw device values."""
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                val = data[f.name]
                transform = cls._inbound_transforms.get(f.name)
                if transform:
                    val = transform(val)
                kwargs[f.name] = val
        return cls(**kwargs)
