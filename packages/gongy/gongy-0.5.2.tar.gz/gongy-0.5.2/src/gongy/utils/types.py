"""Custom types."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "Milliseconds",
    "ms_to_timedelta",
    "timedelta_to_ms",
)

from datetime import timedelta
from typing import Annotated

from pydantic import BeforeValidator, SerializerFunctionWrapHandler
from pydantic.functional_serializers import WrapSerializer


def ms_to_timedelta(v: int) -> timedelta:
    """Convert milliseconds to timedelta."""
    return timedelta(milliseconds=v)


def timedelta_to_ms(td: timedelta) -> int:
    """Convert timedelta to milliseconds."""
    return int(td.total_seconds() * 1000)


def wrap_milliseconds(td: timedelta, nxt: SerializerFunctionWrapHandler) -> int:
    """Serialize Milliseconds."""
    out: int = nxt(timedelta_to_ms(td))
    return out


Milliseconds = Annotated[
    timedelta,
    BeforeValidator(ms_to_timedelta),
    WrapSerializer(wrap_milliseconds),
]
