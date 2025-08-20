from __future__ import annotations

from typing import Literal, Self


class StateTransitionError(Exception):
    """Custom exception for state transition errors."""


MAGIC_FLAG: Literal[2147483648] = 0x80000000
"""A flag to indicate that an integer has been processed by the Auto class."""


def mark_as_auto(number: int) -> int:
    """Mark integer as processed by adding magic flag."""
    return number + MAGIC_FLAG


def is_auto(number: int) -> bool:
    """Check if integer has been processed."""
    return number >= MAGIC_FLAG


def get_original(number: int) -> int:
    """Get original value (works for both processed and unprocessed)."""
    return number - MAGIC_FLAG if is_auto(number) else number


class Auto(int):
    """A class that uses the fact it is subclassing int as a way to smuggle in extra values."""

    def __new__(cls, value: int = 0) -> Self:
        """Create a new Auto instance with a processed value."""
        return super().__new__(cls, mark_as_auto(value))

    def __int__(self) -> int:
        """Return the original integer value."""
        return get_original(self)

    def __str__(self) -> str:
        return str(get_original(self))

    def __repr__(self) -> str:
        return str(get_original(self))

    def __hash__(self) -> int:
        """Return the hash of the original integer value."""
        return hash(get_original(self))

    def __eq__(self, other: object) -> bool:
        """Check equality with another object."""
        if isinstance(other, Auto):
            return get_original(self) == get_original(other)
        if isinstance(other, int):
            return get_original(self) == get_original(other)
        return False
