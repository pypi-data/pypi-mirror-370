"""Basic logger using the Rich library."""

from collections.abc import Callable

from rich import inspect
from rich.console import Console
from rich.theme import Theme

THEME: dict[str, str] = {
    "info": "dim green",
    "debug": "bold blue",
    "warning": "bold yellow",
    "error": "bold red",
    "exception": "bold red",
    "success": "bold green",
    "failure": "bold red underline",
    "verbose": "bold blue",
}


class BasicLogger:
    """A basic logger that uses the Rich library to print messages to the console."""

    def __init__(self) -> None:
        """Initialize the BasicLogger with a Rich Console instance."""
        self.console = Console(theme=Theme(THEME))
        for level in THEME:
            method = self.replacement_method(level)
            setattr(self, level, method)

    def replacement_method(self, level: str) -> Callable:
        """Create a method that logs messages at the specified level."""

        def method(msg: object, **kwargs) -> None:
            """Log a message at the specified level with the given style.

            Args:
                msg (object): The message to log.
                **kwargs: Additional keyword arguments for formatting.
            """
            self.log(level, msg, **kwargs)

        return method

    def log(self, level: str, msg: object, **kwargs) -> None:
        """Log a message at the specified level.

        Args:
            level (str): The logging level (e.g., 'info', 'debug', 'warning', etc.).
            msg (object): The message to log.
            **kwargs: Additional keyword arguments for formatting.
        """
        self.console.print(msg, style=level, **kwargs)

    def print(self, msg: object, **kwargs) -> None:
        """Print a message to the console with the specified style.

        Args:
            msg (object): The message to print.
            **kwargs: Additional keyword arguments for formatting.
        """
        self.console.print(msg, **kwargs)

    def inspect(self, obj: object, **kwargs) -> None:
        """Inspect an object and print its details to the console.

        Args:
            obj (object): The object to inspect.
            **kwargs: Additional keyword arguments for formatting.
        """
        inspect(obj, console=self.console, **kwargs)

    def print_json(self, data: object, **kwargs) -> None:
        """Print a JSON object to the console.

        Args:
            data (object): The JSON data to print.
            **kwargs: Additional keyword arguments for formatting.
        """
        self.console.print_json(data=data, **kwargs)
