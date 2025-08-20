from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any, Self, overload


@dataclass(frozen=True)
class BaseValue[T]:
    """A frozen dataclass for holding constant values of any type."""

    value: T
    text: str
    default: T
    expected_type: type[T]


@dataclass(frozen=True)
class IntValue(BaseValue[int]):
    """A frozen dataclass for holding constant integer values."""

    default: int = 0
    expected_type: type[int] = int


@dataclass(frozen=True)
class StrValue(BaseValue[str]):
    """A frozen dataclass for holding constant string values."""

    default: str = ""
    expected_type: type[str] = str


class RichStrEnum(StrEnum):
    """Base class for StrEnums with rich metadata."""

    text: str
    default: str

    def __new__(cls, value: StrValue) -> Self:
        obj: Self = str.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text
        obj.default = value.default
        return obj

    @classmethod
    def keys(cls) -> list[str]:
        """Return a list of all enum member names."""
        return [item.name for item in cls]

    @overload
    @classmethod
    def get(cls, value: str | Self, default: Self) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | Self, default: None = None) -> None: ...

    @classmethod
    def get(cls, value: str | Self, default: Self | None = None) -> Self | None:
        """Try to get an enum member by its value or name."""
        if isinstance(value, cls):
            return value
        with suppress(ValueError):
            if isinstance(value, str):
                return cls.from_text(value)
        return default

    @classmethod
    def from_text(cls, text: str) -> Self:
        """Convert a string text to its corresponding enum member."""
        for item in cls:
            if item.text == text:
                return item
        raise ValueError(f"Text {text} not found in {cls.__name__}")

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Name {name} not found in {cls.__name__}") from e

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return self.value

    def str(self) -> str:
        """Return the string value of the enum."""
        return self.value


class RichIntEnum(IntEnum):
    """Base class for IntEnums with rich metadata."""

    text: str
    default: int

    def __new__(cls, value: IntValue) -> Self:
        obj: Self = int.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text
        obj.default = value.default
        return obj

    def __int__(self) -> int:
        """Return the integer value of the enum."""
        return self.value

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return f"{self.name} ({self.value}): {self.text}"

    @classmethod
    def keys(cls) -> list[str]:
        """Return a list of all enum member names."""
        return [item.name for item in cls]

    @overload
    @classmethod
    def get(cls, value: str | int | Self | Any, default: Self) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | int | Self | Any, default: str) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | int | Self | Any, default: int) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | int | Self | Any, default: None = None) -> None: ...

    @classmethod
    def get(cls, value: str | int | Self | Any, default: Self | str | int | None = None) -> Self | None:
        """Try to get an enum member by its value, name, or text."""
        if isinstance(value, cls):
            return value
        with suppress(ValueError):
            if isinstance(value, int):
                return cls.from_int(value)
            if isinstance(value, str):
                return cls.from_name(value)
            if isinstance(default, str):
                return cls.from_name(default)
            if isinstance(default, int):
                return cls.from_int(default)
            return default

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Name {name} not found in {cls.__name__}") from e

    @classmethod
    def from_int(cls, code: int) -> Self:
        """Convert an integer to its corresponding enum member."""
        for item in cls:
            if item.value == code:
                return item
        raise ValueError(f"Value {code} not found in {cls.__name__}")

    @classmethod
    def int_to_text(cls, code: int) -> str:
        """Convert an integer to its text representation."""
        try:
            return cls.from_int(code).text
        except ValueError:
            return "Unknown value"
