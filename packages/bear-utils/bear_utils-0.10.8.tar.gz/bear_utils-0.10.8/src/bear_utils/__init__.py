"""A module for Bear Utils, providing various utilities and tools."""

from bear_utils.cache import CacheWrapper, cache, cache_factory
from bear_utils.config.settings_manager import SettingsManager, get_settings_manager
from bear_utils.constants import DEVNULL, STDERR, STDOUT, ExitCode, HTTPStatusCode
from bear_utils.database import DatabaseManager, PostgresDB, SingletonDB
from bear_utils.events import (
    clear_all,
    clear_callbacks,
    event_call,
    event_dispatch,
    event_handler,
    remove_callback,
    set_callback,
)
from bear_utils.extras.responses import FunctionResponse
from bear_utils.files.file_handlers.file_handler_factory import FileHandlerFactory
from bear_utils.logger_manager import BaseLogger, BufferLogger, ConsoleLogger, FileLogger, LoggingClient, LoggingServer
from bear_utils.logger_manager._constants import VERBOSE, VERBOSE_CONSOLE_FORMAT
from bear_utils.time import (
    DATE_FORMAT,
    DATE_TIME_FORMAT,
    EpochTimestamp,
    TimeTools,
    convert_to_milliseconds,
    seconds_to_time,
)

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DEVNULL",
    "STDERR",
    "STDOUT",
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "BaseLogger",
    "BufferLogger",
    "CacheWrapper",
    "ConsoleLogger",
    "DatabaseManager",
    "EpochTimestamp",
    "ExitCode",
    "FileHandlerFactory",
    "FileLogger",
    "FunctionResponse",
    "HTTPStatusCode",
    "LoggingClient",
    "LoggingServer",
    "PostgresDB",
    "SettingsManager",
    "SingletonDB",
    "TimeTools",
    "cache",
    "cache_factory",
    "clear_all",
    "clear_callbacks",
    "convert_to_milliseconds",
    "event_call",
    "event_dispatch",
    "event_handler",
    "get_settings_manager",
    "remove_callback",
    "seconds_to_time",
    "set_callback",
]
