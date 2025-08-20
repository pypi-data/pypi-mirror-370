"""ConsoleLogger: A comprehensive console logger that combines Python's logging framework with Rich console styling."""

# region Imports
from contextlib import suppress
from functools import cached_property
from logging import DEBUG, Formatter, Handler, Logger
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, override

from prompt_toolkit import PromptSession
from rich.text import Text
from rich.theme import Theme

from bear_utils.constants.date_related import DATE_TIME_FORMAT
from bear_utils.logger_manager._constants import FIVE_MEGABYTES, VERBOSE_CONSOLE_FORMAT, VERBOSE_FORMAT, ExecValues
from bear_utils.logger_manager._formatters import ConsoleBuffering, ConsoleFormatter
from bear_utils.logger_manager._handlers import ConsoleHandler
from bear_utils.logger_manager._log_level import LogLevel
from bear_utils.logger_manager.loggers.base_logger import BaseLogger

if TYPE_CHECKING:
    from rich.traceback import Traceback

# endregion Imports


class ConsoleLogger(Logger, BaseLogger):
    """A comprehensive console logger that combines Python's logging framework with Rich console styling.

    This logger provides styled console output with configurable file logging, queue handling,
    buffering, and interactive input capabilities. It dynamically creates logging methods
    (info, error, debug, etc.) that forward to Rich's styled console printing.

    Features:
    - Rich styled console output with themes
    - Optional file logging with rotation
    - Queue-based async logging
    - Message buffering capabilities
    - Interactive prompt integration
    - Exception tracebacks with local variables

    Example:
        logger = ConsoleLogger.get_instance(init=True, verbose=True, name="MyLogger", level=DEBUG)
        logger.info("This is styled info")
        logger.error("This is styled error")
        logger.success("This is styled success")
    """

    # region Setup
    def __init__(
        self,
        theme: Theme | None = None,
        name: str = "ConsoleLogger",
        level: int | str | LogLevel = LogLevel.DEBUG,
        disabled: bool = True,
        console: bool = True,
        file: bool = False,
        queue_handler: bool = False,
        buffering: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the ConsoleLogger with optional file, console, and buffering settings."""
        handler_commands: dict[str, Any] = {
            "file": file,
            "console": console,
            "buffering": buffering,
            "queue_handler": queue_handler,
            "file_path": kwargs.pop("file_path", Path("console_logger.log")),
            "max_bytes": kwargs.pop("max_bytes", FIVE_MEGABYTES),
            "backup_count": kwargs.pop("backup_count", 5),
            "console_formatting": kwargs.pop("console_formatting", VERBOSE_CONSOLE_FORMAT),
        }
        log_level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        Logger.__init__(self, name=name, level=log_level.value)
        BaseLogger.__init__(self, output_handler=self._console_output, theme=theme, level=log_level, **kwargs)

        self.name = name
        self.level = log_level.value
        self.setLevel(self.level)
        self.session = None
        self.disabled = disabled
        self._handlers: list[Handler] = []

        if self.logger_mode:
            self.disabled = False
            self._handle_enable_booleans(**handler_commands)

    def _handle_enable_booleans(
        self,
        file: bool,
        console: bool,
        buffering: bool,
        queue_handler: bool,
        file_path: str | Path,
        max_bytes: int,
        backup_count: int,
        console_formatting: str,
    ) -> None:
        """Configure logging handlers based on initialization parameters."""
        self._console_handler(console_formatting=console_formatting, console=console, buffering=buffering)
        self._file_handler(file=file, file_path=file_path, max_bytes=max_bytes, backup_count=backup_count)
        self._queue_handler(queue_handler=queue_handler)

    def _console_handler(self, console_formatting: str, console: bool = True, buffering: bool = False) -> None:
        """Set up the console handler with the specified formatting."""
        if console or buffering:
            self.console_handler = ConsoleHandler(self.print, self.output_buffer)
            self.console_handler.setFormatter(ConsoleFormatter(fmt=console_formatting, datefmt=DATE_TIME_FORMAT))
            self.console_handler.setLevel(self._level.value)
            if console:
                self._handlers.append(self.console_handler)
            if buffering:
                self.buffer_handler = ConsoleBuffering(console_handler=self.console_handler)
                self._handlers.append(self.buffer_handler)

    def _file_handler(self, file: bool, file_path: str | Path, max_bytes: int, backup_count: int) -> None:
        """Set up the file handler with the specified path and rotation settings."""
        if file:
            self.file_handler = RotatingFileHandler(
                filename=str(Path(file_path).resolve()),
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            self.file_handler.setFormatter(Formatter(fmt=VERBOSE_FORMAT, datefmt=DATE_TIME_FORMAT))
            self.file_handler.setLevel(self._level.value)
            self._handlers.append(self.file_handler)

    def _queue_handler(self, queue_handler: bool = False) -> None:
        if queue_handler:
            self.queue = Queue()
            self.queue_handler = QueueHandler(self.queue)
            self.addHandler(self.queue_handler)
            self.listener = QueueListener(self.queue, *self._handlers)
            self.listener.start()
        else:
            for handler in self._handlers:
                self.addHandler(handler)

    def set_console_formatter(self, fmt: str = VERBOSE_CONSOLE_FORMAT) -> None:
        """Set the formatter for the console handler."""
        if hasattr(self, "console_handler"):
            self.console_handler.setFormatter(ConsoleFormatter(fmt=fmt, datefmt=DATE_TIME_FORMAT))
            self.verbose(f"ConsoleLogger: Console formatter set to {fmt}")

    def set_file_formatter(self, fmt: str = VERBOSE_FORMAT) -> None:
        """Set the formatter for the file handler."""
        if hasattr(self, "file_handler"):
            self.file_handler.setFormatter(Formatter(fmt=fmt, datefmt=DATE_TIME_FORMAT))
            self.verbose(f"ConsoleLogger: File formatter set to {fmt}")

    def set_buffer_formatter(self, fmt: str = VERBOSE_CONSOLE_FORMAT) -> None:
        """Set the formatter for the buffer handler."""
        if hasattr(self, "buffer_handler"):
            self.buffer_handler.setFormatter(ConsoleFormatter(fmt=fmt, datefmt=DATE_TIME_FORMAT))
            self.verbose(f"ConsoleLogger: Buffer formatter set to {fmt}")

    def stop_queue_listener(self) -> None:
        """Stop the queue listener if it exists and clean up resources."""
        if hasattr(self, "listener"):
            self.verbose("ConsoleLogger: QueueListener stopped and cleaned up.")
            self.listener.stop()
            del self.listener
            del self.queue
            del self.queue_handler

    def trigger_buffer_flush(self) -> Text:
        """Flush buffered messages to console output."""
        if hasattr(self, "buffer_handler"):
            return self.buffer_handler.flush_to_output()
        return Text("No buffering handler available.", style="bold red")

    def set_base_level(self, level: int | str | LogLevel) -> None:
        """Set the base logging level for the console logger."""
        log_value: int = LogLevel.get(level, default=self._level).value
        super().set_base_level(log_value)
        self.setLevel(log_value)
        if hasattr(self, "console_handler"):
            self.console_handler.setLevel(log_value)
        if hasattr(self, "buffer_handler"):
            self.buffer_handler.setLevel(log_value)
        if hasattr(self, "queue_handler"):
            self.queue_handler.setLevel(log_value)

    def _console_output(self, msg: object, extra: dict, *args, **kwargs) -> None:
        """Console-specific output handler that integrates with logging module."""
        if not self.logger_mode:
            self.print(msg, *args, **kwargs)
        else:
            kwargs.pop("style", None)
            self.log(
                extra.get("log_level", DEBUG),
                msg,
                *args,
                extra=extra,
                exc_info=kwargs.pop("exc_info", extra.get("style_name") == "exception"),
                **kwargs,
            )

    # endregion Setup
    # region Utility Methods

    async def input(self, msg: str, style: str = "info", **kwargs) -> str:
        """Display a styled prompt and return user input asynchronously."""
        if not self.session:
            self.session = PromptSession(**kwargs)
        self.print(msg, style=style)
        return await self.session.prompt_async()

    def output_buffer(
        self,
        msg: object,
        end: str = "\n",
        exc_info: str | None = None,
        exec_values: ExecValues | None = None,
        *_,
        **kwargs,
    ) -> str:
        """Capture console output to a string buffer without printing to terminal."""
        if exc_info and exec_values:
            exception: Traceback = self._get_exception(manual=True, exec_values=exec_values)
            self.console.print(exception, end=end)
        self.console.print(msg, end="", style=kwargs.get("style", "info"))
        output = self.console_buffer.getvalue()
        self._reset_buffer()
        return output

    # endregion Utility Methods
    # region Enhanced Print Methods

    def print(
        self,
        msg: object,
        end: str = "\n",
        exc_info: str | None = None,
        extra: dict | None = None,
        *args,
        **kwargs,
    ) -> None | str:
        """Print styled messages with enhanced exception handling and JSON support.

        Extends the base print method with proper exception tracebacks and
        integrated JSON printing for structured data output.
        """
        if exc_info is not None:
            with suppress(ValueError):
                self._print(self._get_exception(), end=end, width=100, show_locals=True, **kwargs)

        self._print(msg, end, *args, **kwargs)

        if extra:
            self._print(msg=extra, end=end, json=True, indent=4)

    @cached_property
    def stack_level(self) -> int:
        """Cached property to retrieve the current stack level."""
        return self.stack_tracker.record_end()

    @override
    def _log(  # type: ignore[override]
        self,
        level: int,
        msg: object,
        args: tuple,
        exc_info: str | None = None,
        extra: dict | None = None,
        stack_info: bool = False,
        stacklevel: int | None = None,
    ) -> None:
        """Custom logging implementation with enhanced exception handling.

        Overrides the standard logging._log method to provide better exception
        value extraction for Rich traceback integration while respecting log levels.
        """
        stacklevel = stacklevel or self.stack_level
        try:
            fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
        except ValueError:
            fn, lno, func, sinfo = "(unknown file)", 0, "(unknown function)", None
        final_extra = extra or {}
        if exc_info is not None:
            exec_values: ExecValues | None = self._extract_exception_values(exc_info)
            if exec_values is not None:
                final_extra = {**final_extra, "exec_values": exec_values}

        record = self.makeRecord(
            name=self.name,
            level=level,
            fn=fn,
            lno=lno,
            msg=msg,
            args=args,
            exc_info=None,
            func=func,
            extra=final_extra,
            sinfo=sinfo,
        )

        self.handle(record)

    def exit(self) -> None:
        """Clean up resources including queue listeners and console buffers."""
        if hasattr(self, "queue_handler"):
            self.queue_handler.flush()
            self.stop_queue_listener()

        self.console_buffer.close()

    # endregion Enhanced Print Methods
