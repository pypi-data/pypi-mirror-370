from itertools import count
from typing import Self

from bear_utils.graphics.font._utils import ascii_header

from ._typing_stuff import ObjectTypeError, type_param, validate_type
from .clipboard import (
    ClipboardManager,
    clear_clipboard,
    clear_clipboard_async,
    copy_to_clipboard,
    copy_to_clipboard_async,
    paste_from_clipboard,
    paste_from_clipboard_async,
)
from .platform_utils import (
    DARWIN,
    LINUX,
    OS,
    OTHER,
    WINDOWS,
    get_platform,
    is_linux,
    is_macos,
    is_windows,
)


class Counter:
    """A simple counter class that can be used to track state transitions."""

    def __init__(self, start: int = 0) -> None:
        """Initialize the counter with a starting value."""
        if start < 0:
            raise ValueError("Counter value cannot be negative.")
        self._counter: count[int] = count(start)
        self._count: int = next(self._counter)

    def increment(self) -> int:
        """Increment the counter and return the new value."""
        self._count = next(self._counter)
        return self._count

    def reset(self, value: int = 0) -> None:
        """Reset the counter to a specific value."""
        self._count = value
        self._counter = count(value)

    def get(self, increment_after: bool = False, increment_before: bool = False) -> int:
        """Get the current value of the counter.

        Args:
            increment_after (bool): If True, increment the counter after getting the value.
            increment_before (bool): If True, increment the counter before getting the value.
        """
        if increment_before:
            self.increment()
            return self._count
        if increment_after:
            current_value: int = self._count
            self.increment()
            return current_value
        return self._count

    def set(self, value: int) -> Self:
        """Set the counter to a specific value."""
        if value < 0:
            raise ValueError("Counter value cannot be negative.")
        if value < self._count:
            raise ValueError("Cannot set counter to a value less than the current counter value.")
        self._counter = count(value)
        self._count = next(self._counter)
        return self

    def __eq__(self, other: object) -> bool:
        """Check equality with another integer."""
        return self._count == other

    def __lt__(self, other: int) -> bool:
        """Check if the counter is less than another integer."""
        return self._count < other

    def __le__(self, other: int) -> bool:
        """Check if the counter is less than or equal to another integer."""
        return self._count <= other

    def __gt__(self, other: int) -> bool:
        """Check if the counter is greater than another integer."""
        return self._count > other

    def __ge__(self, other: int) -> bool:
        """Check if the counter is greater than or equal to another integer."""
        return self._count >= other

    def __hash__(self) -> int:
        """Return the hash of the current counter value."""
        return hash(self._count)


__all__ = [
    "DARWIN",
    "LINUX",
    "OS",
    "OTHER",
    "WINDOWS",
    "ClipboardManager",
    "Counter",
    "ObjectTypeError",
    "ascii_header",
    "clear_clipboard",
    "clear_clipboard_async",
    "copy_to_clipboard",
    "copy_to_clipboard_async",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "paste_from_clipboard",
    "paste_from_clipboard_async",
    "type_param",
    "validate_type",
]
