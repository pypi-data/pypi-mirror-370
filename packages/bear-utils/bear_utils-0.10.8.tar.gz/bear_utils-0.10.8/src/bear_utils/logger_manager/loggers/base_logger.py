"""BaseLogger: A comprehensive console logger that is the foundation for all other loggers."""

from functools import partial
from io import StringIO
import sys
from typing import Any, Self

from prompt_toolkit.formatted_text import ANSI, FormattedText, to_formatted_text
from prompt_toolkit.shortcuts import print_formatted_text
from rich.text import Text
from rich.theme import Theme
from rich.traceback import Traceback
from singleton_base import SingletonBase

from bear_utils.logger_manager._constants import DEFAULT_THEME, LOGGER_METHODS, ExecValues, LoggerExtraInfo
from bear_utils.logger_manager._stack_tracker import StackLevelTracker
from bear_utils.logger_manager.loggers._console import LogConsole
from bear_utils.logger_manager.loggers._log_level import LevelHandler, LogLevel
from bear_utils.logger_manager.loggers.sub_logger import SubConsoleLogger

# TODO: Needs some work since this is so tightly coupled with the ConsoleLogger


class BaseLogger(SingletonBase):
    """BaseLogger: A comprehensive console logger that is the foundation for all other loggers."""

    def __init__(
        self,
        output_handler: Any = None,
        theme: Theme | None = None,
        style_disabled: bool = False,
        logger_mode: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the BaseLogger with an optional style_disabled flag.

        This flag can be used to disable styled output in the logger.
        """
        self.output_handler = output_handler or self._default_output
        self._level: LogLevel = LogLevel.get(kwargs.get("level", LogLevel.INFO), default=LogLevel.INFO)
        self.stack_tracker: StackLevelTracker = StackLevelTracker()
        self.logger_mode: bool = logger_mode
        self.theme: Theme = DEFAULT_THEME if theme is None else theme
        self.style_disabled: bool = style_disabled
        self.name: str = kwargs.pop("name", "BaseLogger")
        self.console: LogConsole[StringIO] = self.get_console(self.theme, style_disabled, **kwargs)
        self.console_buffer: StringIO = self.console.file
        self.backup_console = LogConsole(theme=self.theme, highlight=True, force_terminal=True)
        self._generate_style_methods()

    @staticmethod
    def get_console(theme: Theme, style_disabled: bool, **kwargs) -> LogConsole:
        """Create and return a Console instance with the specified theme and styling options."""
        if style_disabled:
            console = LogConsole(
                file=StringIO(),
                highlight=False,
                force_terminal=True,
                style=None,  # Disable styling
                **kwargs,
            )
        else:
            console: LogConsole = LogConsole(
                file=StringIO(),
                highlight=False,
                force_terminal=True,
                color_system="truecolor",
                theme=theme,
                **kwargs,
            )
        return console

    def _default_output(self, msg: object, _: LoggerExtraInfo, *args, **kwargs) -> None:
        """Default output handler that prints to console."""
        if not self.logger_mode:
            self.print(msg, *args, **kwargs)

    def __enter__(self) -> Self:
        """Enter the context manager, returning the ConsoleLogger instance.

        This allows for using the logger in a with statement.
        """
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the context manager, cleaning up resources.

        This is called when the with statement is exited.
        """
        self.exit()

    def trigger_buffer_flush(self) -> str | Text:
        """Flush buffered messages to console output."""
        return "No buffering handler available."

    def set_base_level(self, level: int | str | LogLevel) -> None:
        """Set the logging level for the console.

        This method allows changing the logging level dynamically.

        This isn't actually a logging logger so we are having to add this while avoiding messing with
        any subclasses that do subclass Logger.

        Args:
            level (int): The logging level to set. This should be a valid logging level constant.
        """
        self._level = LevelHandler.check_level(level)

    def filter_by_level(self, level: str | int | LogLevel) -> bool:
        """Filter method to determine if a message should be logged based on its level.

        This method checks if the provided level is greater than or equal to the logger's level.

        Args:
            level (int): The logging level of the message.

        Returns:
            bool: True if the message should be logged, False otherwise.
        """
        level = LevelHandler.check_level(level)
        return level >= self._level

    def get_sub_logger(self, namespace: str, **kwargs) -> "SubConsoleLogger":
        """Get a sub-logger with a specific namespace."""
        return SubConsoleLogger(self, namespace, **kwargs)  # type: ignore[return-value]

    def _generate_style_methods(self) -> None:
        """Generate dynamic logging methods with proper log level registration."""
        for style_name, extra in LOGGER_METHODS.items():
            if not LevelHandler.lvl_exists(extra["log_level"]):  # I'd rather if things crash than silently fail
                LevelHandler.add_level_name(level=extra["log_level"], name=extra.get("style_name"))
            setattr(self, style_name, partial(self.replacement_method, injected_extra=extra.copy()))

    def replacement_method(self, msg: object, *args, **kwargs) -> None:
        """Replacement method for logging messages with additional context."""
        if self.stack_tracker.not_set:
            self.stack_tracker.record_start()
        filter_func = kwargs.pop("filter_func", self.filter_by_level)
        extra: LoggerExtraInfo = kwargs.pop("injected_extra") | kwargs.pop("extra", {})
        kwargs["style"] = extra.pop("style", None)
        if extra.get("namespace"):
            msg = f"<{extra.get('namespace')}> {msg}"
        if filter_func(extra.get("log_level", self._level)):
            self.output_handler(msg, extra, *args, **kwargs)

    def print(
        self,
        msg: object,
        end: str = "\n",
        exc_info: object | None = None,
        extra: dict | None = None,
        *_,
        **kwargs,
    ) -> None | str:
        """Print a message to the console with the specified formatting.

        This method allows for printing messages with additional context and formatting.
        """
        if exc_info is not None:
            try:
                exception: Traceback = self._get_exception(manual=True)
                self._print(exception, end=end, **kwargs)
            except Exception as e:
                print(
                    f"ConsoleLogger: Error printing exception traceback. Message: {msg} Exception: {exc_info} Error: {e}"
                )
        self._print(msg, end, style=kwargs.pop("style", None))
        if extra:
            self._print(msg=extra, end=end, json=True, indent=4)

    def print_json(
        self,
        json: str | None = None,
        data: dict | None = None,
        indent: int = 2,
        sort: bool = False,
        **kwargs,
    ) -> None:
        """Just a pass-through to the console.print_json method."""
        self.console.print_json(json=json, data=data, indent=indent, sort_keys=sort, **kwargs)

    def raw_print(self, msg: object, end: str = "\n", *_, **kwargs) -> None:
        """Use the underlying console directly and bypass all the extra formatting and handling.

        Args:
            msg (object): The message to print.
            end (str, optional): The string appended after the message. Defaults to new line.
        """
        self.backup_console.print(msg, end=end, style=kwargs.pop("style", "white"), **kwargs)

    def _print(self, msg: object, end: str, json: bool = False, *args, **kwargs) -> None:
        """Print a message to the console with the specified formatting.

        This method allows for printing messages with additional context and formatting.
        """
        try:
            if json:
                self.print_json(msg, *args, **kwargs)  # type: ignore[arg-type]
            else:
                self.console.print(msg, end="", style=kwargs.pop("style", "white"))
            formatted_text: FormattedText = to_formatted_text(ANSI(self.console_buffer.getvalue()))
            print_formatted_text(formatted_text, end=end)
            self._reset_buffer()
        except Exception as e:
            print(
                f"{self.__class__.__name__.upper()}: Error printing message. Message: {msg} Exception: {e}. "
                "Please check the console buffer for more details."
            )
            self._reset_buffer()

    def _extract_exception_values(self, exc_info: Any) -> ExecValues | None:
        """Extract exception values in a clean, reusable way."""
        if isinstance(exc_info, BaseException):
            exc_tuple = (type(exc_info), exc_info, exc_info.__traceback__)
        elif exc_info is True:
            exc_tuple = sys.exc_info()
        else:
            exc_tuple = exc_info
        if exc_tuple:
            exc_type, exc_value, exc_traceback = exc_tuple
            if exc_type is not None and exc_value is not None and exc_traceback is not None:
                return {"exc_type": exc_type, "exc_value": exc_value, "exc_traceback": exc_traceback}
        return None

    def _get_exception(self, manual: bool = False, exec_values: ExecValues | None = None) -> Traceback:
        if manual and exec_values:
            return Traceback.from_exception(
                exc_type=exec_values["exc_type"],
                exc_value=exec_values["exc_value"],
                traceback=exec_values["exc_traceback"],
                show_locals=True,
                width=100,
            )
        return Traceback(show_locals=True, width=100)

    def _reset_buffer(self) -> None:
        """Reset the console buffer."""
        self.console_buffer.truncate(0)
        self.console_buffer.seek(0)

    def exit(self) -> None:
        """Exit the console logger.

        This method is called when the program exits to clean up resources.
        """
        self.console_buffer.close()
