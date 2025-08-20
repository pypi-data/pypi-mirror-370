"""A file-based logger that writes log messages to files, styling is disabled as it is not applicable for file output."""

from logging import DEBUG
from pathlib import Path
from typing import TYPE_CHECKING, Any, override

from rich.theme import Theme

from bear_utils.logger_manager._constants import FIVE_MEGABYTES
from bear_utils.logger_manager._log_level import LogLevel
from bear_utils.logger_manager.loggers.console_logger import ConsoleLogger
from bear_utils.logger_manager.loggers.sub_logger import SubConsoleLogger

if TYPE_CHECKING:
    from bear_utils.logger_manager._constants import LoggerExtraInfo


class FileLogger(ConsoleLogger):
    """A file-based logger that writes styled log messages to files.

    Combines Python's logging framework with Rich console styling, but outputs
    to files instead of console. Supports file rotation, custom formatting,
    and maintains the same interface as other loggers.

    Features:
    - File logging with rotation
    - Rich-style method generation (info, error, debug, etc.)
    - Consistent print() interface
    - Exception tracebacks in file format
    - JSON logging support

    Example:
        logger = FileLogger.get_instance(
            init=True,
            name="FileLogger",
            file_path="app.log",
            max_bytes=10*1024*1024,
            backup_count=5
        )
        logger.info("This goes to the file")
        logger.error("This error is logged to file")
    """

    def __init__(
        self,
        theme: Theme | None = None,
        name: str = "FileLogger",
        level: int | str | LogLevel = LogLevel.DEBUG,
        file_path: str = "app.log",
        max_bytes: int = FIVE_MEGABYTES,
        backup_count: int = 5,
        *_,
        **kwargs,
    ) -> None:
        """Initialize the FileLogger with file path and rotation settings."""
        self.file_path = Path(file_path)  # TODO: Add more options for filename patterns (timestamps, process IDs, etc.)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        ConsoleLogger.__init__(
            self,
            name=name,
            level=level,
            file=True,
            console=False,
            queue_handler=kwargs.pop("queue_handler", False),
            file_path=self.file_path,
            max_bytes=self.max_bytes,
            backup_count=self.backup_count,
            theme=theme,
            style_disabled=True,
            logger_mode=True,
            **kwargs,
        )

    @override
    def get_sub_logger(self, namespace: str, **kwargs: Any) -> SubConsoleLogger:
        return SubConsoleLogger(self, namespace, **kwargs)

    @override
    def replacement_method(self, msg: object, *args, **kwargs) -> None:
        """Handle logging method calls with proper file logging integration."""
        extra: LoggerExtraInfo = kwargs.pop("injected_extra")
        if kwargs.get("extra"):
            extra.update(kwargs.pop("extra"))
        if extra.get("namespace"):
            msg = f"<{extra.get('namespace')}> {msg}"
        if self.stack_tracker.not_set:
            self.stack_tracker.record_start()

        self.log(
            extra.get("log_level", DEBUG),
            msg,
            extra,
            *args,
            **kwargs,
        )

    def print(
        self,
        msg: object,
        _: str = "\n",
        exc_info: str | None = None,
        extra: dict | None = None,
        *__,
        **___,
    ) -> None:
        """Print a message to the file with proper formatting.

        Maintains the same interface as other loggers but writes to file instead of console.
        """
        try:
            # For file logging, we want to use the logging system rather than direct file writing
            # This ensures proper formatting, rotation, etc.
            if exc_info is not None:
                # Log with exception info
                self.error(f"{msg}", exc_info=exc_info, extra=extra)
            else:
                # Regular info log
                self.info(f"{msg}", extra=extra)

            if extra:
                # Log extra data as JSON-like format
                self.info(f"Extra data: {extra}")
        except Exception as e:
            print(f"FileLogger: Failed to write to log file. Message: {msg}, Error: {e}")

    def get_file_size(self) -> int:
        """Get current size of the log file in bytes."""
        if self.file_path.exists():
            return self.file_path.stat().st_size
        return 0

    def get_file_path(self) -> Path:
        """Get the current log file path."""
        return self.file_path

    def rotate_file(self) -> None:
        """Manually trigger file rotation."""
        if hasattr(self.file_handler, "doRollover"):
            self.file_handler.doRollover()

    @override
    def exit(self) -> None:
        """Clean up file resources."""
        if hasattr(self, "file_handler"):
            self.file_handler.flush()
            self.file_handler.close()
            self.removeHandler(self.file_handler)

        # Call parent exit
        super().exit()
