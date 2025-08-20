from logging import Logger
from logging.handlers import QueueHandler, RotatingFileHandler
from pathlib import Path
from typing import Any

from rich.text import Text
from rich.theme import Theme

from bear_utils.logger_manager._formatters import ConsoleBuffering
from bear_utils.logger_manager._handlers import ConsoleHandler
from bear_utils.logger_manager._log_level import LogLevel

from .base_logger import BaseLogger
from .sub_logger import SubConsoleLogger

class ConsoleLogger(Logger, BaseLogger):
    name: str
    level: LogLevel  # type: ignore[assignment]
    file: bool
    queue_handler: QueueHandler
    buffer_handler: ConsoleBuffering
    console_handler: ConsoleHandler
    file_handler: RotatingFileHandler
    sub_logger: dict[str, SubConsoleLogger[ConsoleLogger]]

    def __init__(
        self,
        theme: Theme | None = None,
        name: str = "ConsoleLogger",
        level: int | str | LogLevel = ...,
        disabled: bool = True,
        queue_handler: bool = False,
        buffering: bool = False,
        file: bool = False,
        console: bool = True,
        style_disabled: bool = False,
        logger_mode: bool = True,
        file_path: str | Path = "console_logger.log",
        max_bytes: int = 5_242_880,  # 5 MB
        backup_count: int = 5,
        console_formatting: str = "verbose",
        *args,
        **kwargs,
    ) -> None: ...
    # fmt: off
    def debug(self, msg: object, *args, **kwargs: Any) -> None: ...
    def info(self, msg: object, *args, **kwargs: Any) -> None: ...
    def warning(self, msg: object, *args, **kwargs: Any) -> None: ...
    def error(self, msg: object, *args, **kwargs: Any) -> None: ...
    def success(self, msg: object, *args, **kwargs: Any) -> None: ...
    def failure(self, msg: object, *args, **kwargs: Any) -> None: ...
    def verbose(self, msg: object, *args, **kwargs: Any) -> None: ...
    def set_base_level(self, level: int) -> None: ...
    def input(self, msg: str, style: str = "info") -> str: ...
    def trigger_buffer_flush(self) -> str | Text: ...
    def print(self, msg: object, end: str="\n", exc_info:str|None=None, extra: dict | None = None, *args, **kwargs) -> None | str: ...
    def exit(self) -> None: ...
