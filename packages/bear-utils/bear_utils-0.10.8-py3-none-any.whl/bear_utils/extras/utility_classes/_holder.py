from collections import defaultdict
from io import StringIO
from typing import Any, Self

from bear_utils.extras._typing_stuff import InputObjectError, num_type_params, type_param, validate_type


class GenericClassProperties:
    """A class that provides properties for generic class handling."""

    @property
    def _class(self) -> type:
        """Return the type of the class."""
        return type(self)

    @property
    def _num_type_params(self) -> int:
        """Return the number of type parameters of the class."""
        return num_type_params(self._class)

    @classmethod
    def _cls_type_param(cls, index: int = 0) -> type:
        """Return the type parameter of the class."""
        if index < 0 or index >= num_type_params(cls):
            raise IndexError(f"Index {index} out of range for type parameters of {cls._class.__name__}.")
        return type_param(cls, index=index)

    @property
    def _type_name(self) -> str:
        """Return the name of the type parameter of the class."""
        return self._cls_type_param(0).__name__

    @property
    def _init_type(self) -> Any:
        """Return a new instance of the type held by this class."""
        _get_type = self._cls_type_param(0)
        return _get_type()


class ObjectHolder[Held](GenericClassProperties):
    """A holder for multiple objects of one type, allowing access by name."""

    def __init__(self, default: Held | None = None, default_name: str = "default") -> None:
        """Initialize the Holder with a default value and type.

        Args:
            default (Held): The default object to hold. This will be used to determine the type of objects stored.
        """
        held_object: Held = default if default is not None else self._init_type
        self._container_type: type = self._cls_type_param(0)
        validate_type(held_object, self._container_type, InputObjectError)
        self._container: defaultdict[str, Held] = defaultdict(self._container_type)
        self._container[default_name] = held_object
        self._pointer: str = default_name

    @property
    def active(self) -> Held:
        """Get the currently active object."""
        return self.get(self._pointer)

    @active.setter
    def active(self, name: str) -> None:
        """Set the currently active object by name."""
        self.get(name)

    @property
    def current(self) -> str:
        """Get the name of the currently active object."""
        return self._pointer

    def _update_pointer(self, name: str) -> None:
        """Update the active pointer to the current active held object."""
        self._pointer = name

    @property
    def names(self) -> list[str]:
        """Get the names of all objects held in the holder."""
        return list(self._container.keys())

    def has(self, name: str) -> bool:
        """Check if an object with the given name exists in the holder.

        Args:
            name (str): The name of the object to check for.
        """
        return name in self.names

    def _new(self, name: str, update: bool = False) -> None:
        self.set(name, self._init_type)
        if update:
            self._update_pointer(name)

    def _check_and_set(self, name: str) -> Held:
        """Create a default object of the specified type.

        Args:
            name (str): The name of the object to create.

        Returns:
            Held: The created holder object.
        """
        if not self.has(name):
            try:
                self._new(name, update=True)
            except TypeError as e:
                raise TypeError(f"Cannot auto-create {self._type_name} - requires arguments") from e
        return self.get(name)

    def get(self, name: str | None = None) -> Held:
        """Get the value of the object with the given name.

        Args:
            name (str): The name of the object to retrieve.

        Returns:
            Held: The value of the object with the given name.
        """
        if name is None:
            name = self.current
        if not self.has(name):
            self._check_and_set(name)
        return self._container[name]

    def set(self, name: str, value: Held) -> Self:
        """Set the value of the object with the given name.

        Args:
            name (str): The name of the object to set.
            value (Held): The value to set for the object.

        Returns:
            Self: The current instance for method chaining.
        """
        if not isinstance(value, self._container_type):
            raise TypeError(f"Value must be of type {self._type_name}, got {type(value).__name__}")
        self._container[name] = value
        return self

    def set_active(self, name: str) -> Self:
        """Set the active holder object by name."""
        if not self.has(name):
            self._check_and_set(name)
        self._update_pointer(name)
        return self


class BufferSpace(ObjectHolder[StringIO]):
    """A specialized ObjectHolder for StringIO buffers."""

    def __init__(self, default: StringIO | Any = None) -> None:
        """Initialize the BufferSpace with a default StringIO buffer."""
        super().__init__(default=default)

    def getvalue(self, name: str | None = None) -> str:
        """Get the value of the StringIO buffer by name."""
        if name is None:
            name = self.current
        if not self.has(name):
            raise ValueError(f"No buffer found with name '{name}'")
        return self.active.getvalue()

    def reset(self, name: str | None = None) -> Self:
        """Reset the StringIO buffer by name."""
        if name is None:
            name = self.current
        self.set_active(name)
        self.active.truncate(0)
        self.active.seek(0)
        return self


class StringSpace(ObjectHolder[str]):
    """A specialized ObjectHolder for string values."""

    def __init__(self, default: str | None = None) -> None:
        """Initialize the StringSpace with a default string value."""
        super().__init__(default)


if __name__ == "__main__":
    string_space = StringSpace(default="Hello, World!")
    print(string_space.get("default"))  # Output: Hello, World!
