from types import TracebackType
from typing import NotRequired, Required, TypedDict

from rich.theme import Theme

from bear_utils.logger_manager.loggers._log_level import (
    DEBUG,
    ERROR,
    FAILURE,
    INFO,
    SUCCESS,
    VERBOSE,
    WARNING,
    LogLevel,
)


class ExecValues(TypedDict, total=True):
    exc_type: Required[type[BaseException]]
    exc_value: Required[BaseException]
    exc_traceback: Required[TracebackType]


class LoggerExtraInfo(TypedDict):
    """Type definition for extra info that can be added to log records."""

    style_name: Required[str]
    style: Required[str]
    namespace: NotRequired[str]
    log_level: Required[int]
    log_level_style: Required[str]
    log_level_enum: NotRequired[LogLevel]


LOGGER_METHODS: dict[str, LoggerExtraInfo] = {
    "info": {
        "style_name": "info",
        "style": "dim green",
        "log_level": INFO,
        "log_level_style": "black on white",
        "log_level_enum": LogLevel.INFO,
    },
    "debug": {
        "style_name": "debug",
        "style": "bold blue",
        "log_level": DEBUG,
        "log_level_style": "black on blue",
        "log_level_enum": LogLevel.DEBUG,
    },
    "warning": {
        "style_name": "warning",
        "style": "bold yellow",
        "log_level": WARNING,
        "log_level_style": "yellow on black",
        "log_level_enum": LogLevel.WARNING,
    },
    "error": {
        "style_name": "error",
        "style": "bold red",
        "log_level": ERROR,
        "log_level_style": "bold white on red",
        "log_level_enum": LogLevel.ERROR,
    },
    "exception": {
        "style_name": "exception",
        "style": "bold red",
        "log_level": ERROR,
        "log_level_style": "bold white on red",
        "log_level_enum": LogLevel.ERROR,
    },
    "success": {
        "style_name": "success",
        "style": "bold green",
        "log_level": SUCCESS,
        "log_level_style": "black on bright_green",
        "log_level_enum": LogLevel.SUCCESS,
    },
    "failure": {
        "style_name": "failure",
        "style": "bold red underline",
        "log_level": FAILURE,
        "log_level_style": "bold red on white",
        "log_level_enum": LogLevel.FAILURE,
    },
    "verbose": {
        "style_name": "verbose",
        "style": "bold blue",
        "log_level": VERBOSE,
        "log_level_style": "black on bright_blue",
        "log_level_enum": LogLevel.VERBOSE,
    },
}


def get_method(name: str) -> LoggerExtraInfo:
    """Get the name info from the logger methods.

    Args:
        name (str): The name of the logger method.

    Returns:
        LoggerExtraInfo | dict: The info of the logger method or an empty dict if not found.
    """
    if not LOGGER_METHODS.get(name):
        raise ValueError(f"Logger method '{name}' does not exist. Available methods: {list(LOGGER_METHODS.keys())}")
    return LOGGER_METHODS[name]


DEFAULT_STYLES: dict[str, str] = {**{method: info["style"] for method, info in LOGGER_METHODS.items()}}
"""Just the styles of the logger methods, used to create the theme."""
DEFAULT_THEME = Theme(styles=DEFAULT_STYLES)
"""The default theme for the logger, used to apply styles to log messages."""
VERBOSE_FORMAT = "%(asctime)s |%(levelname)s| {%(module)s|%(funcName)s|%(lineno)d} %(message)s"
"""The verbose format for log messages, used in detailed logging scenarios."""
VERBOSE_CONSOLE_FORMAT = "%(asctime)s <[{}]{}[/{}]> %(message)s"
"""The verbose format for log messages, used in detailed logging scenarios."""
SIMPLE_FORMAT = "%(message)s"
"""The simple format for log messages, used in basic logging scenarios."""
FIVE_MEGABYTES = 1024 * 1024 * 5
"""The size limit for file handlers, set to 5 MB."""
