"""A Base wrapper class for objects."""

from functools import partial
from io import StringIO
from logging import INFO, Formatter, Logger, StreamHandler
from typing import Self

from rich.console import Console

from bear_utils.constants import STDOUT
from bear_utils.extras._typing_stuff import InputObjectError, OutputObjectError, type_param, validate_type
from bear_utils.logger_manager.loggers._log_level import LevelHandler


class BaseWrapper[Incoming, Outgoing]:
    """A Base wrapper class for objects."""

    def __init__(self, incoming: Incoming | None, outgoing: Outgoing | None, **kwargs) -> None:
        """Initialize the BaseWrapper with a default value."""
        self._incoming_type: type[Incoming] = type_param(type(self), 0)
        self._outgoing_type: type[Outgoing] = type_param(type(self), 1)
        incoming = self._incoming_type() if incoming is None else incoming
        outgoing = self._outgoing_type() if outgoing is None else outgoing
        validate_type(incoming, self._incoming_type, InputObjectError)
        validate_type(outgoing, self._outgoing_type, OutputObjectError)
        self._root: Incoming = incoming
        self._cache: Outgoing = outgoing
        self.name: str = kwargs.get("name", "default")

    @property
    def root_obj(self) -> Incoming:
        """Get the root object."""
        return self._root

    @property
    def cache_obj(self) -> Outgoing:
        """Get the cached value."""
        return self._cache

    @cache_obj.setter
    def cache_obj(self, value: Outgoing) -> None:
        """Set the cached value."""
        validate_type(value, self._outgoing_type, OutputObjectError)
        self._cache = value


################################################################
################ EXAMPLE USAGE #################################
################################################################


class StringIOWrapper(BaseWrapper[StringIO, str]):
    """A utility wrapper around the StringIO and str classes.

    The StringIOWrapper class provides a way to manage
    a StringIO object with caching capabilities. It allows
    writing to the StringIO object, caching its content,
    and resetting the object while optionally clearing the cache.
    It also has a fluent interface for chaining method calls.
    """

    def __init__(self, default_in: StringIO | None = None, default_out: str | None = None, **kwargs) -> None:
        """Initialize the StringIOWrapper with a StringIO object."""
        super().__init__(incoming=default_in, outgoing=default_out, **kwargs)

    def _reset(self, clear: bool = False) -> Self:
        """Reset the current IO object."""
        self.cache_obj: str = self.root_obj.getvalue()
        if clear:
            self.cache_obj = ""
        self.root_obj.truncate(0)
        self.root_obj.seek(0)
        return self

    def cache(self) -> Self:
        """Cache the current value of the IO object."""
        self.cache_obj = self.root_obj.getvalue()
        return self

    def reset(self, clear: bool = False) -> Self:
        """Will only reset the IO object but not the cached value.

        Args:
            clear (bool): If True, will clear the cached value.
        """
        self._reset(clear=clear)
        return self

    def write(self, *values: str) -> None:
        """Write values to the StringIO object."""
        for value in values:
            self.root_obj.write(value)

    def flush(self) -> None:
        """Save the current content to the cache and reset the StringIO object."""
        self._reset(clear=False)

    @property
    def empty_buffer(self) -> bool:
        """Check if the StringIO object is empty."""
        return not self.root_obj.getvalue()

    @property
    def empty_cache(self) -> bool:
        """Check if the cached value is empty."""
        return not self.cache_obj

    def getvalue(self, cache: bool = False) -> str:
        """Get the string value from the StringIO object."""
        if cache and self.empty_buffer:
            return self.cache_obj
        return self.root_obj.getvalue()

    def get_cache(self) -> str:
        """Get the cached value from the str object."""
        return self.cache_obj

    def __repr__(self) -> str:
        """Return a string representation of the StringIOWrapper."""
        return f"{self.__class__.__name__}(root_obj={self.root_obj.getvalue()}, cache_obj={self.cache_obj})"


class ConsoleWrapper(BaseWrapper[Console, StringIO]):
    """A wrapper around the rich Console class."""

    def __init__(self, console: Console | None = None, cache: StringIO | None = None) -> None:
        """Initialize the ConsoleWrapper with a Console object."""
        super().__init__(incoming=console, outgoing=cache)
        self.root_obj.file = self.cache_obj

    def buffer(self, *args, **kwargs) -> None:
        """Buffer output to the console."""
        self.root_obj.print(*args, **kwargs)

    def print(self, *args, **kwargs) -> None:
        """Print to the console and cache the output."""
        self.root_obj.file = STDOUT
        self.root_obj.print(*args, **kwargs)
        self.root_obj.file = self.cache_obj

    def getvalue(self) -> str:
        """Get the cached value from the StringIO object."""
        return self.cache_obj.getvalue()


class LoggerWrapper(BaseWrapper[Logger, StringIO]):
    """A wrapper around the logging.Logger class."""

    def __init__(self, logger: Logger | None = None, cache: StringIO | None = None) -> None:
        """Initialize the LoggerWrapper with a Logger object."""
        super().__init__(incoming=logger, outgoing=cache)
        handler: StreamHandler[StringIO] = StreamHandler(self.cache_obj)
        formatter = Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.root_obj.addHandler(handler)

        for level in LevelHandler.name_to_level:
            setattr(self, level.lower(), partial(self.wrapper, level=level))

    def __getattr__(self, name: str) -> partial[None]:
        """Handle dynamic attribute access for logging levels."""
        if name.upper() in LevelHandler.name_to_level:
            return partial(self.wrapper, level=name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def wrapper(self, msg: str, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        level: str = kwargs.pop("level", "info").upper()
        self.root_obj.log(LevelHandler.name_to_level.get(level.upper(), INFO), msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        self.root_obj.log(level, msg, *args, **kwargs)

    def getvalue(self) -> str:
        """Get the cached value from the StringIO object."""
        return self.cache_obj.getvalue()


__all__ = [
    "BaseWrapper",
    "ConsoleWrapper",
    "LoggerWrapper",
    "StringIOWrapper",
]

if __name__ == "__main__":
    # # Example usage
    wrapper = StringIOWrapper()
    wrapper.write("Hello, World!")
    output: str = wrapper.cache().reset().getvalue()

    print(f"Cached: {output}")  # Output: Hello, World!
    wrapper.reset(clear=False)
    print(f"Cached 1: {wrapper.getvalue()}")  # Output: Hello World!
    wrapper.reset(clear=True)
    print(f"Cached 2: {wrapper.getvalue()}")  # Output: (empty string)

    console = ConsoleWrapper()
    console.buffer("Hello, Buffer!")
    value: str = console.getvalue()
    print(f"Console Output: {value}")  # Output: Hello, Console!
    console.print("Hello, Print!")
    value = console.getvalue()
    print(f"Console Output: {value}")  # Output: Hello, Print!

    logger = LoggerWrapper(logger=Logger("TestLogger"))
    logger.log(INFO, "This is a test log message.")
    logger.info("This is an info message.")
    log_value = logger.getvalue()
    print(f"Logger Output: {log_value}")  # Output: This is a test
