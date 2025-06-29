from __future__ import annotations

from dataclasses import dataclass, fields
from enum import IntEnum
from typing import (
    Any,
    dataclass_transform,
    get_type_hints,
    cast,
)


def _validate_fields(instance: Any) -> None:
    """Runtime type checking + 0–127 guard for any int / IntEnum fields."""
    hints = get_type_hints(instance.__class__)
    for fld in fields(cast(Any, instance)):
        val: Any = getattr(instance, fld.name)
        exp = hints.get(fld.name, Any)

        # Static-type check
        if exp is not Any and not isinstance(val, exp):
            raise TypeError(f"{fld.name}={val!r} is not {exp}")

        # Range check for int / IntEnum
        as_int = int(val) if isinstance(val, IntEnum) else val
        if isinstance(as_int, int) and not 0 <= as_int <= 0x7F:
            raise ValueError(f"{fld.name}={as_int} is outside 0-127")


@dataclass_transform()
def model(_cls=None, **dc_kwargs):

    def wrap(cls):
        # Get existing __post_init__ if any
        original_post_init = getattr(cls, "__post_init__", None)

        def __post_init__(self):
            # Run our validation
            _validate_fields(self)
            # Call original __post_init__ if it exists
            if original_post_init:
                original_post_init(self)

        # Add the new __post_init__ to the class
        setattr(cls, "__post_init__", __post_init__)

        # Turn the class into a dataclass
        return dataclass(frozen=False, slots=True, **dc_kwargs)(cls)

    return wrap(_cls) if _cls else wrap
