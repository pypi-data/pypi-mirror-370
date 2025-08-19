"""Custom types."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "Milliseconds",
    "ms_to_timedelta",
)

from datetime import timedelta
from typing import Annotated

from pydantic import BeforeValidator


def ms_to_timedelta(v: int) -> timedelta:
    """Convert milliseconds to timedelta."""
    return timedelta(milliseconds=v)


Milliseconds = Annotated[
    timedelta,
    BeforeValidator(ms_to_timedelta),
]
