"""This is some terrible sinning that should not exist, don't look at it. It doesn't exist if you don't look at it."""

from __future__ import annotations

from logging import addLevelName
from threading import RLock
from typing import ClassVar, Literal, Self

from bear_utils.constants._meta import IntValue as Value, RichIntEnum

FAILURE: Literal[45] = 45
ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
SUCCESS: Literal[15] = 15
DEBUG: Literal[10] = 10
VERBOSE: Literal[5] = 5
NOTSET: Literal[0] = 0


class LogLevel(RichIntEnum):
    """Enumeration for logging levels."""

    NOTSET = Value(NOTSET, "NOTSET", default=NOTSET)
    VERBOSE = Value(VERBOSE, "VERBOSE", default=VERBOSE)
    DEBUG = Value(DEBUG, "DEBUG", default=DEBUG)
    INFO = Value(INFO, "INFO", default=INFO)
    WARNING = Value(WARNING, "WARNING", default=WARNING)
    ERROR = Value(ERROR, "ERROR", default=ERROR)
    FAILURE = Value(FAILURE, "FAILURE", default=FAILURE)
    SUCCESS = Value(SUCCESS, "SUCCESS", default=SUCCESS)
    INVALID_LEVEL = Value(999, "INVALID_LEVEL", default=999)

    @classmethod
    def level_to_name(cls, level: int | str | Self) -> str:
        """Get the name of a logging level."""
        if isinstance(level, LogLevel):
            level = level.value
        elif isinstance(level, str):
            level = level.upper()
            if level in LevelHandler.name_to_level:
                level = LevelHandler.name_to_level[level]
        raise ValueError(
            f"Invalid logging level name: {level!r}. Valid levels are: {list(LevelHandler.name_to_level.keys())}"
        )

    @classmethod
    def name_to_level(cls, name: str | Self) -> int:
        """Get the numeric value of a logging level by its name."""
        if isinstance(name, LogLevel):
            return name.value
        name = name.upper()
        if name in LevelHandler.name_to_level:
            return LevelHandler.name_to_level[name]
        raise ValueError(
            f"Invalid logging level name: {name!r}. Valid levels are: {list(LevelHandler.name_to_level.values())}"
        )


class LevelHandler:
    """A handler for managing custom logging levels."""

    _lock: ClassVar[RLock] = RLock()

    level_to_name: ClassVar[dict[int, str]] = {
        FAILURE: "FAILURE",
        ERROR: "ERROR",
        WARNING: "WARNING",
        INFO: "INFO",
        SUCCESS: "SUCCESS",
        DEBUG: "DEBUG",
        VERBOSE: "VERBOSE",
        NOTSET: "NOTSET",
    }

    name_to_level: ClassVar[dict[str, int]] = {
        "FAILURE": FAILURE,
        "ERROR": ERROR,
        "WARN": WARNING,
        "WARNING": WARNING,
        "INFO": INFO,
        "SUCCESS": SUCCESS,
        "DEBUG": DEBUG,
        "VERBOSE": VERBOSE,
        "NOTSET": NOTSET,
    }

    @classmethod
    def lvl_exists(cls, level: int | str | LogLevel) -> bool:
        """Check if a logging level already exists."""
        with cls._lock:
            level = cls.check_level(level, fail=False)
            return level in cls.level_to_name

    @classmethod
    def add_level_name(
        cls, log_level: LogLevel | None = None, level: int | None = None, name: str | None = None
    ) -> None:
        """Add a custom logging level name.

        This function allows you to add a new logging level with a custom name to the logging system.
        If the level already exists, it raises a ValueError.

        Args:
            level (int): The numeric value of the logging level.
            name (str): The name of the logging level.
            log_level (LogLevel | None): An optional LogLevel enum instance to use instead of
                the `level` and `name` parameters. If provided, `level` and `name` are
                derived from it.
        """
        with cls._lock:
            if log_level is not None and level is None and name is None:
                level = log_level.value
                name = log_level.name
            elif log_level is not None and (level is not None or name is not None):
                raise ValueError("Cannot provide both log_level and level/name parameters.")

            if level is None or name is None:
                raise ValueError("Both level and name must be provided and cannot be empty.")

            if level in cls.level_to_name:
                raise ValueError(f"Level {level} already exists with name {cls.level_to_name[level]}")

            cls.level_to_name[level] = name.upper()
            cls.name_to_level[name.upper()] = level
            addLevelName(level=level, levelName=name)

    @classmethod
    def check_level(cls, level: int | str | LogLevel | None, fail: bool = True) -> LogLevel:
        """Validate and normalize logging level to integer."""
        if isinstance(level, LogLevel) and level.value in cls.level_to_name:
            return level
        if (isinstance(level, str) and level.upper() in cls.name_to_level) or (
            isinstance(level, int) and level in cls.level_to_name
        ):
            return LogLevel.get(level, LogLevel.INVALID_LEVEL)
        if fail and not isinstance(level, (int | str | LogLevel)):
            raise TypeError(f"Level must be int or str, got {type(level).__name__}: {level!r}")
        raise ValueError(f"Invalid logging level: {level!r}. Valid levels are: {list(cls.name_to_level.keys())}")
