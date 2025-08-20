"""Simple logger implementation with log levels and timestamped output."""

from io import StringIO
from typing import TextIO

from bear_utils.constants import STDERR, STDOUT, NullFile
from bear_utils.logger_manager._log_level import LogLevel
from bear_utils.time import EpochTimestamp


class SimpleLogger[T: TextIO]:
    """A simple logger that writes messages to stdout, stderr, or StringIO with a timestamp."""

    def __init__(self, level: str | int | LogLevel = "DEBUG", file: T = STDERR) -> None:
        """Initialize the logger with a minimum log level and output file."""
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        self.file: T = file  # Can be STDOUT, STDERR, StringIO, NullFile or other TextIO Objects
        self.buffer: list[str] = []

    def print(self, msg: object, end: str = "\n") -> None:
        """Print the message to the specified file with an optional end character."""
        print(msg, end=end, file=self.file)

    def _log(self, level: LogLevel, msg: object, end: str = "\n", *args, **kwargs) -> None:
        timestamp: str = EpochTimestamp.now().to_string()
        try:
            self.buffer.append(f"[{timestamp}] {level.value}: {msg}")
            if args:
                self.buffer.append(" ".join(str(arg) for arg in args))
            if kwargs:
                for key, value in kwargs.items():
                    self.buffer.append(f"{key}={value}")
            self.print(f"{end}".join(self.buffer))
        except Exception as e:
            self.print(f"[{timestamp}] {level.value}: {msg} - Error: {e}")
        finally:
            self.buffer.clear()

    def log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        if level.value >= self.level.value:
            self._log(level, msg, *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Alias for debug level logging."""
        self.log(LogLevel.VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, msg, *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        """Log a success message."""
        self.log(LogLevel.SUCCESS, msg, *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        """Log a failure message."""
        self.log(LogLevel.FAILURE, msg, *args, **kwargs)


__all__ = [
    "STDERR",
    "STDOUT",
    "LogLevel",
    "NullFile",
    "SimpleLogger",
]

# Example usage:
if __name__ == "__main__":
    logger = SimpleLogger(file=StringIO())
    logger_two = SimpleLogger(level="INFO", file=NullFile())
    logger.info(msg="This is an info message")
    logger_two.info(msg="This is an info message")

    value = logger.file
    print(value.getvalue())  # Print the captured log messages from StringIO
    # print(logger_two.file.getvalue())  # should throw a typing error since it is not a StringIO
