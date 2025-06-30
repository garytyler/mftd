from __future__ import annotations

from dataclasses import fields, replace
from typing import Any, Callable, ClassVar, Mapping, get_type_hints


class BaseModel:
    """Common dataclass utilities for configuration models."""

    # Mapping of field name to callable used when constructing an instance from
    # device data.
    _inbound_transforms: ClassVar[Mapping[str, Callable[[Any], Any]]] = {}

    # Mapping of field name to callable used when preparing an instance for
    # transmission to the device.
    _outbound_transforms: ClassVar[Mapping[str, Callable[[Any], Any]]] = {}

    def __post_init__(self) -> None:  # pragma: no cover - executed implicitly
        """Ensure that all fields have the correct type."""
        hints = get_type_hints(self.__class__)
        for f in fields(self):
            value = getattr(self, f.name)
            field_type = hints.get(f.name, f.type)
            try:
                if hasattr(field_type, "__origin__"):
                    continue
                if isinstance(field_type, type) and not isinstance(value, field_type):
                    setattr(self, f.name, field_type(value))
            except TypeError:
                continue

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        """Ensure that fields have the correct type when set via attribute."""
        field_obj = next((f for f in fields(self) if f.name == name), None)
        if field_obj is not None:
            hints = get_type_hints(self.__class__)
            field_type = hints.get(field_obj.name, field_obj.type)
            try:
                if hasattr(field_type, "__origin__"):
                    pass
                elif isinstance(field_type, type) and not isinstance(value, field_type):
                    value = field_type(value)
            except TypeError:
                pass
        super().__setattr__(name, value)

    def to_device(self) -> "BaseModel":
        """Return a new instance with outbound transforms applied."""
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        for name, transform in self._outbound_transforms.items():
            if name in data:
                data[name] = transform(data[name])
        return replace(self, **data)

    @classmethod
    def from_device(cls, data: Mapping[str, Any]) -> "BaseModel":
        """Create an instance from raw device values."""
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                value = data[f.name]
                transform = cls._inbound_transforms.get(f.name)
                if transform:
                    value = transform(value)
                kwargs[f.name] = value
        return cls(**kwargs)
