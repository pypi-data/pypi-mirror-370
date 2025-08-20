"""Constants Module for Bear Utils."""

from pathlib import Path
import sys
from typing import TextIO

from bear_utils.constants._exit_code import (
    COMMAND_CANNOT_EXECUTE,
    COMMAND_NOT_FOUND,
    EXIT_STATUS_OUT_OF_RANGE,
    FAIL,
    FAILURE,
    INVALID_ARGUMENT_TO_EXIT,
    MISUSE_OF_SHELL_COMMAND,
    PROCESS_KILLED_BY_SIGKILL,
    PROCESS_TERMINATED_BY_SIGTERM,
    SCRIPT_TERMINATED_BY_CONTROL_C,
    SEGMENTATION_FAULT,
    SUCCESS,
    ExitCode,
)
from bear_utils.constants._http_status_code import (
    BAD_REQUEST,
    CONFLICT,
    FORBIDDEN,
    PAGE_NOT_FOUND,
    SERVER_ERROR,
    SERVER_OK,
    UNAUTHORIZED,
    HTTPStatusCode,
)
from bear_utils.constants._meta import IntValue, RichIntEnum, RichStrEnum, StrValue
from bear_utils.constants._text import MockTextIO, NullFile

VIDEO_EXTS = [".mp4", ".mov", ".avi", ".mkv"]
"""Extensions for video files."""
IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".gif"]
"""Extensions for image files."""
FILE_EXTS = IMAGE_EXTS + VIDEO_EXTS
"""Extensions for both image and video files."""

PATH_TO_DOWNLOADS = Path.home() / "Downloads"
"""Path to the Downloads folder."""
PATH_TO_PICTURES = Path.home() / "Pictures"
"""Path to the Pictures folder."""
GLOBAL_VENV = Path.home() / ".global_venv"
"""Path to the global virtual environment."""

STDOUT: TextIO = sys.stdout
"""Standard output stream."""
STDERR: TextIO = sys.stderr
"""Standard error stream."""
DEVNULL: TextIO = NullFile()
"""A null file that discards all writes."""

__all__ = [
    "BAD_REQUEST",
    "COMMAND_CANNOT_EXECUTE",
    "COMMAND_NOT_FOUND",
    "CONFLICT",
    "EXIT_STATUS_OUT_OF_RANGE",
    "FAIL",
    "FAILURE",
    "FILE_EXTS",
    "FORBIDDEN",
    "GLOBAL_VENV",
    "IMAGE_EXTS",
    "INVALID_ARGUMENT_TO_EXIT",
    "MISUSE_OF_SHELL_COMMAND",
    "PAGE_NOT_FOUND",
    "PATH_TO_DOWNLOADS",
    "PATH_TO_PICTURES",
    "PROCESS_KILLED_BY_SIGKILL",
    "PROCESS_TERMINATED_BY_SIGTERM",
    "SCRIPT_TERMINATED_BY_CONTROL_C",
    "SEGMENTATION_FAULT",
    "SERVER_ERROR",
    "SERVER_OK",
    "STDERR",
    "STDOUT",
    "SUCCESS",
    "UNAUTHORIZED",
    "VIDEO_EXTS",
    "ExitCode",
    "HTTPStatusCode",
    "IntValue",
    "MockTextIO",
    "NullFile",
    "RichIntEnum",
    "RichStrEnum",
    "StrValue",
]
