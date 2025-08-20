from types import NoneType
from typing import Any, get_args


class ObjectTypeError(TypeError):
    """Base class for object type errors."""

    def __init__(self, expected: type = NoneType, received: type = NoneType, **kwargs) -> None:
        """Initialize the ObjectTypeError with expected and received types."""
        if kwargs.get("msg") is not None:
            super().__init__(kwargs.pop("msg"))
            return
        super().__init__(f"Expected object of type {expected.__name__}, but got {received.__name__}.")


class InputObjectError(ObjectTypeError):
    """Exception raised for errors in the input object type."""

    def __init__(self, expected: type, received: type) -> None:
        msg: str = f"Expected input object of type {expected.__name__}, but got {received.__name__}."
        super().__init__(msg=msg)


class OutputObjectError(ObjectTypeError):
    """Exception raised for errors in the output object type."""

    def __init__(self, expected: type, received: type) -> None:
        msg: str = f"Expected output object of type {expected.__name__}, but got {received.__name__}."
        super().__init__(msg=msg)


def validate_type(val: Any, expected: type, exception: type[ObjectTypeError] | None = None) -> None:
    """Validate the type of the given value.

    Args:
        val (Any): The value to validate.
        expected (type): The expected type of the value.
        exception (type[ObjectTypeError] | None): The exception to raise if the type
            does not match. If None, a TypeError is raised.
    """
    if not isinstance(val, expected):
        if exception is None:
            raise TypeError(f"Expected object of type {expected.__name__}, but got {type(val).__name__}.")
        raise exception(expected=expected, received=type(val))


def num_type_params(cls: type) -> int:
    """Get the number of type parameters of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the number of type parameters.

    Returns:
        int: The number of type parameters.

    Raises:
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    return len(args)


def type_param(cls: type, index: int = 0) -> type:
    """Get the type parameter of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the type parameter.
        index (int): The index of the type parameter to retrieve. Defaults to 0.

    Returns:
        type: The type parameter at the specified index.

    Raises:
        IndexError: If the specified index is out of range for the type parameters.
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except IndexError:
        raise IndexError(f"Index {index} is out of range for type parameters of {cls.__name__}.") from None
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    if args[index] is NoneType:
        raise TypeError(f"Type parameter at index {index} is NoneType for {cls.__name__}.")
    return args[index]
