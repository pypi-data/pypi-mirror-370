"""A set of command-line interface (CLI) utilities for bear_utils."""

from ._args import FAILURE, SUCCESS, ExitCode, args_process
from .commands import GitCommand, MaskShellCommand, OPShellCommand, UVShellCommand
from .shell._base_command import BaseShellCommand
from .shell._base_shell import SimpleShellSession, shell_session
from .shell._common import DEFAULT_SHELL

__all__ = [
    "DEFAULT_SHELL",
    "FAILURE",
    "SUCCESS",
    "BaseShellCommand",
    "ExitCode",
    "GitCommand",
    "MaskShellCommand",
    "OPShellCommand",
    "SimpleShellSession",
    "UVShellCommand",
    "args_process",
    "shell_session",
]
