"""Logger adapter module that provides an alternative to SubLogger using standard library tools.

This implementation shows how to use LoggerAdapter and contextvars to maintain
all the functionality of the existing SubLogger while reducing complexity.
"""

from functools import partial
from typing import TYPE_CHECKING, Any

from rich.text import Text

from bear_utils.logger_manager._constants import LOGGER_METHODS, LoggerExtraInfo
from bear_utils.logger_manager._log_level import LevelHandler, LogLevel

if TYPE_CHECKING:
    from collections.abc import Callable

    from bear_utils.logger_manager.loggers.base_logger import BaseLogger


class SubConsoleLogger[T: BaseLogger]:
    """SubConsoleLogger: A logger that wraps another logger with a namespace."""

    def __init__(self, logger: T, namespace: str, **kwargs) -> None:
        """Initialize the SubConsoleLogger with a logger and a namespace.

        Args:
            logger: The underlying logger to wrap with a namespace.
            namespace: The namespace to prefix log messages with
        """
        self.logger: T = logger
        self._level: LogLevel = LogLevel.get(kwargs.get("level"), default=logger._level)
        self.logger_mode: bool = logger.logger_mode
        self.namespace: str = namespace
        self._setup(self.namespace)

    def print(
        self,
        msg: object,
        end: str = "\n",
        exc_info: Any = None,
        extra: dict | None = None,
        *_,
        **kwargs,
    ) -> None | str:
        """Print a message to the console with the specified formatting.

        This method allows for printing messages with additional context and formatting.
        """
        return self.logger.print(msg, end=end, exc_info=exc_info, extra=extra, **kwargs)

    def set_sub_level(self, level: int | str | LogLevel) -> None:
        """Set the logging level for the logger.

        This method allows changing the logging level dynamically.
        """
        previous_lvl: LogLevel = self._level
        self._level = LogLevel.get(level, default=previous_lvl)

    def filter_by_level(self, level: int | str | LogLevel) -> bool:
        """Filter method to determine if a message should be logged based on its level.

        This method checks if the provided level is greater than or equal to the logger's level.

        Args:
            level (int | str): The logging level of the message.

        Returns:
            bool: True if the message should be logged, False otherwise.
        """
        return LevelHandler.check_level(level) >= self._level

    def trigger_buffer_flush(self) -> str | Text:
        """Flush buffered messages to console output.

        This method is used to ensure that any buffered log messages are printed
        to the console, similar to the SubLogger's buffer flush functionality.
        """
        return self.logger.trigger_buffer_flush()

    def _setup(self, name: str) -> None:
        """Get an attribute from the logger.

        This allows for accessing logger methods directly.
        """
        filter_func: Callable[..., bool] = self.filter_by_level
        for style_name, og_extra in LOGGER_METHODS.items():
            extra: LoggerExtraInfo = og_extra.copy()

            extra["namespace"] = name

            setattr(
                self,
                style_name,
                partial(
                    self.logger.replacement_method,
                    injected_extra=extra,
                    filter_func=filter_func,
                ),
            )

    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"ConsoleAdapter(namespace={self.namespace}"
