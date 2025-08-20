"""A helper class to manage a set of StringIO wrapped buffers with named spaces.

Each StringIOWrapper has both a StringIO object and a cached string value.
This class allows you to set, write to, clear, and retrieve values from more than
one StringIOWrapper, each identified by a unique name.
"""

from collections.abc import Callable, Iterable
from typing import Any, ClassVar, Self

from bear_utils.extras.utility_classes._holder import ObjectHolder
from bear_utils.extras.utility_classes._wrapper import StringIOWrapper


class MultiBuffer(ObjectHolder[StringIOWrapper]):
    """A helper class to manage a set of StringIO wrapped buffers with named spaces."""

    _print_method: ClassVar[Callable | None] = None

    @classmethod
    def set_printer(cls, printer: Callable | Any) -> None:
        """Set the printer method to be used for printing output.

        Args:
            printer (Callable): The method to use for printing output, e.g., a logger or print function.
        """
        if not callable(printer):
            raise TypeError(f"Printer must be callable, got {type(printer).__name__}")
        cls._print_method = printer

    @classmethod
    def get_printer(cls) -> Callable:
        """Get the currently set printer method.

        Returns:
            Callable: The current printer method, or None if not set.
        """
        return cls._print_method if cls._print_method is not None else print

    def __init__(self, default_name: str = "default") -> None:
        """Initialize the ObjectHolder with StringIOWrapper as the type."""
        super().__init__(default_name=default_name)

    def write(self, *text: Iterable | Any, end: str = "\n") -> Self:
        """Write text to the buffer, joining multiple strings with the specified end character.

        Args:
            *text (Iterable): The text to write to the buffer. Can be multiple strings or an iterable of strings.
            end (str): The string to append at the end of the written text. Defaults to a newline character.
        """
        if not text:
            return self

        if len(text) == 1 and not isinstance(text[0], str) and hasattr(text[0], "__iter__"):
            joined_text: str = end.join(str(item) for item in text[0])
        else:
            joined_text: str = end.join(str(item) for item in text)
        self.active.write(joined_text)
        return self

    def clear(self, clr_cache: bool = False) -> Self:
        """Clear the buffer.

        Args:
            clr_cache (bool): If True, also clear the cached string value of the active buffer

        Returns:
            Self: The current instance for method chaining.
        """
        self.active.reset(clear=clr_cache)
        return self

    def get_buffer(self, name: str | None = None) -> StringIOWrapper:
        """Get the StringIOWrapper for the specified buffer name.

        Args:
            name (str | None): The name of the buffer to retrieve. If None, uses the current active buffer.

        Returns:
            StringIOWrapper: The StringIOWrapper for the specified buffer.
        """
        return self.active if name is None else self.get(name)

    def _save_output(self, value: str | None = None, name: str | None = None) -> None:
        """Save the current buffer content to the output space with the specified name.

        Args:
            value (str): The content to save.
            name (str | None): The name under which to save the content. If None,
            it saves under the current buffer name.
        """
        buffer: StringIOWrapper = self.get_buffer(name)
        if value is not None:
            buffer.write(value)
        buffer.flush()

    def flush(self, name: str | None = None) -> Self:
        """Store the last output written to the named buffer."""
        self._save_output(name=name)
        return self

    def getvalue(self, name: str | None = None, cache: bool = False) -> str:
        """Get the current content of the buffer as a string.

        Args:
            name (str | None): The name of the buffer to get the value from. If None, uses the current buffer.

        Returns:
            str: The content of the specified buffer.
        """
        buffer: StringIOWrapper = self.get_buffer(name)
        if cache and buffer.empty_buffer:
            return buffer.get_cache()
        return buffer.getvalue()

    def print(self, text: Iterable | None = None, end: str = "\n", **kwargs) -> Self:
        """Print text to the buffer and also to the printer (e.g., console or logger).

        Args:
            *text (Iterable): The text to print. Can be multiple strings or an iterable of strings.
            end (str): The string to append at the end of the printed text. Defaults to a newline character.
            **kwargs: Additional keyword arguments to pass to the printer's method.

        Returns:
            Self: The current instance for method chaining.
        """
        if text:
            self.write(*text, end=end)
        self.get_printer()(self.getvalue(), end=end, **kwargs)
        return self


if __name__ == "__main__":
    # Example usage
    buffer_helper = MultiBuffer()
    buffer_helper.write("Hello, World!")
    print(buffer_helper.flush().getvalue())  # Should print the message and clear the buffer
    print(buffer_helper.get_buffer())
    print(buffer_helper.active.getvalue())  # Should print an empty string since the buffer was cleared
