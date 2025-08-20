from bear_utils.constants._meta import IntValue as Value, RichIntEnum


class ExitCode(RichIntEnum):
    """An enumeration of common exit codes used in shell commands."""

    SUCCESS = Value(0, "Success")
    FAILURE = Value(1, "General error")
    MISUSE_OF_SHELL_COMMAND = Value(2, "Misuse of shell command")
    COMMAND_CANNOT_EXECUTE = Value(126, "Command invoked cannot execute")
    COMMAND_NOT_FOUND = Value(127, "Command not found")
    INVALID_ARGUMENT_TO_EXIT = Value(128, "Invalid argument to exit")
    SCRIPT_TERMINATED_BY_CONTROL_C = Value(130, "Script terminated by Control-C")
    PROCESS_KILLED_BY_SIGKILL = Value(137, "Process killed by SIGKILL (9)")
    SEGMENTATION_FAULT = Value(139, "Segmentation fault (core dumped)")
    PROCESS_TERMINATED_BY_SIGTERM = Value(143, "Process terminated by SIGTERM (15)")
    EXIT_STATUS_OUT_OF_RANGE = Value(255, "Exit status out of range")


SUCCESS = ExitCode.SUCCESS
"""An exit code indicating success."""
FAIL = ExitCode.FAILURE
"""Deprecated alias for ExitCode.FAILURE."""
FAILURE = ExitCode.FAILURE
"""An exit code indicating a general error."""
MISUSE_OF_SHELL_COMMAND = ExitCode.MISUSE_OF_SHELL_COMMAND
"""An exit code indicating misuse of a shell command."""
COMMAND_CANNOT_EXECUTE = ExitCode.COMMAND_CANNOT_EXECUTE
"""An exit code indicating that the command invoked cannot execute."""
COMMAND_NOT_FOUND = ExitCode.COMMAND_NOT_FOUND
"""An exit code indicating that the command was not found."""
INVALID_ARGUMENT_TO_EXIT = ExitCode.INVALID_ARGUMENT_TO_EXIT
"""An exit code indicating an invalid argument to exit."""
SCRIPT_TERMINATED_BY_CONTROL_C = ExitCode.SCRIPT_TERMINATED_BY_CONTROL_C
"""An exit code indicating that the script was terminated by Control-C."""
PROCESS_KILLED_BY_SIGKILL = ExitCode.PROCESS_KILLED_BY_SIGKILL
"""An exit code indicating that the process was killed by SIGKILL (9)."""
SEGMENTATION_FAULT = ExitCode.SEGMENTATION_FAULT
"""An exit code indicating a segmentation fault (core dumped)."""
PROCESS_TERMINATED_BY_SIGTERM = ExitCode.PROCESS_TERMINATED_BY_SIGTERM
"""An exit code indicating that the process was terminated by SIGTERM (15)."""
EXIT_STATUS_OUT_OF_RANGE = ExitCode.EXIT_STATUS_OUT_OF_RANGE
"""An exit code indicating that the exit status is out of range."""


__all__ = [
    "COMMAND_CANNOT_EXECUTE",
    "COMMAND_NOT_FOUND",
    "EXIT_STATUS_OUT_OF_RANGE",
    "FAIL",
    "FAILURE",
    "INVALID_ARGUMENT_TO_EXIT",
    "MISUSE_OF_SHELL_COMMAND",
    "PROCESS_KILLED_BY_SIGKILL",
    "PROCESS_TERMINATED_BY_SIGTERM",
    "SCRIPT_TERMINATED_BY_CONTROL_C",
    "SEGMENTATION_FAULT",
    "SUCCESS",
    "ExitCode",
]
