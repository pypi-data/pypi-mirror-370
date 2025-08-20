"""BufferLogger: A buffer-based logger that writes styled log messages to a buffer for later retrieval."""

from typing import Any, override

from rich.theme import Theme

from bear_utils.logger_manager._log_level import LogLevel

from .console_logger import ConsoleLogger
from .sub_logger import SubConsoleLogger


class BufferLogger(ConsoleLogger):
    """A buffer-based logger that writes styled log messages to a buffer.

    Combines Python's logging framework with Rich console styling, but outputs
    to a buffer instead of console or file. Supports buffering of log messages,

    Features:
    - Buffering of log messages
    - Rich-style method generation (info, error, debug, etc.)
    - Consistent print() interface
    - Exception tracebacks in buffer format

    Example:
        logger = BufferLogger.get_instance(
            init=True,
            name="BufferLogger",
        )
        logger.info("This goes to the buffer")
        logger.error("This error is logged to buffer")
    """

    def __init__(
        self,
        theme: Theme | None = None,
        name: str = "BufferLogger",
        level: int | str | LogLevel = LogLevel.DEBUG,
        **kwargs,
    ) -> None:
        """Initialize the BufferLogger with buffering settings."""
        ConsoleLogger.__init__(
            self,
            name=name,
            level=level,
            file=False,
            console=False,
            buffering=True,
            theme=theme,
            logger_mode=True,
            **kwargs,
        )

    @override
    def get_sub_logger(self, namespace: str, **kwargs: Any) -> SubConsoleLogger:
        return SubConsoleLogger(self, namespace, **kwargs)
