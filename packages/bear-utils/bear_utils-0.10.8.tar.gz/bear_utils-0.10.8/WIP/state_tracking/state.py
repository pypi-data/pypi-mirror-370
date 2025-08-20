"""A class representing a state in a state machine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from bear_utils.extras.state_tracking._common import Auto, get_original

if TYPE_CHECKING:
    from collections.abc import Callable


def auto(wrap: Callable, **kwargs) -> int:
    """A decorator to mark a value as auto-incrementing."""
    auto = Auto(0)
    return wrap(default=auto, **kwargs)


@dataclass
class State:
    """A class representing a state in a state machine."""

    name: str = Field(description="The string representation of the state.")
    initial: bool = Field(default=False, description="Whether this state is the initial state of the state machine.")
    final: bool = Field(default=False, description="Whether this state is a final state of the state machine.")
    id: int = auto(Field, description="An integer value representing the state.")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate the name of the state."""
        if not isinstance(value, str):
            raise TypeError(f"State name must be a string, got {type(value).__name__}.")
        return value.strip()

    def __eq__(self, other: object) -> bool:
        """Check equality with another state or integer."""
        if isinstance(other, State):
            return self.id == other.id and self.name.lower() == other.name.lower()
        if isinstance(other, int):
            return get_original(self.id) == get_original(other)
        if isinstance(other, str):
            return self.name.lower() == other.lower()
        return False

    def __str__(self) -> str:
        """Return the string representation of the state."""
        return self.name.lower()

    def __repr__(self) -> str:
        attrs: dict[str, str | bool | int] = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return f"State({', '.join(f'{k}={v!r}' for k, v in attrs.items())})"

    def __int__(self) -> int:
        """Return the integer representation of the state value."""
        if isinstance(self.id, (int | Auto)):
            return int(self.id)
        raise TypeError(f"Cannot convert state value '{self.id}' to int.")

    def __hash__(self) -> int:
        """Return the hash of the state value."""
        return hash(get_original(self.id))


__all__ = ["State"]
