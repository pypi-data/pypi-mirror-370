# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m bear_utils` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `bear_utils.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `bear_utils.__main__` in `sys.modules`.
from __future__ import annotations

from argparse import Action, ArgumentParser, Namespace
import sys
from typing import Any

from bear_utils._internal import debug
from bear_utils.cli._get_version import VALID_BUMP_TYPES, cli_bump
from bear_utils.constants import STDERR, ExitCode


class _DebugInfo(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        debug._print_debug_info()
        sys.exit(ExitCode.SUCCESS)


class _About(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        print(debug._get_package_info())
        sys.exit(ExitCode.SUCCESS)


class _Version(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        version: str = f"{debug._get_name()} v{debug._get_version()}"
        print(version)
        sys.exit(ExitCode.SUCCESS)


def get_version() -> ExitCode:
    """CLI command to get the version of the package."""
    print(debug._get_version())
    return ExitCode.SUCCESS


def bump_version(bump_type: str) -> ExitCode:
    """CLI command to bump the version of the package."""
    return cli_bump([bump_type, debug._get_name(), debug._get_version()])


def get_parser() -> ArgumentParser:
    name: str = debug._get_name()
    parser = ArgumentParser(description=name.capitalize(), prog=name, exit_on_error=False)
    parser.add_argument("-V", "--version", action=_Version, help="Print the version of the package")
    subparser = parser.add_subparsers(dest="command", required=False, help="Available commands")
    subparser.add_parser("get-version", help="Get the current version of the package")
    bump: ArgumentParser = subparser.add_parser("bump-version", help="Bump the version of the package")
    bump.add_argument("bump_type", type=str, choices=VALID_BUMP_TYPES, help="major, minor, or patch")
    parser.add_argument("--about", action=_About, help="Print information about the package")
    parser.add_argument("--debug_info", action=_DebugInfo, help="Print debug information")
    return parser


def _execute_command(command: str, opts: Namespace) -> ExitCode:
    """Execute the specified command with given options.

    Args:
        command: The command to execute
        opts: Parsed command line options

    Returns:
        ExitCode: Result of command execution
    """
    if command == "get-version":
        return get_version()

    if command == "bump-version":
        if not hasattr(opts, "bump_type"):
            print("Error: 'bump-version' command requires a 'bump_type' argument.", file=STDERR)
            return ExitCode.FAILURE
        return bump_version(bump_type=opts.bump_type)
    print(f"Unknown command: {command}", file=STDERR)
    return ExitCode.FAILURE


def main(args: list[str] | None = None) -> ExitCode:
    """Main entry point for the CLI.

    This function is called when the CLI is executed. It can be used to
    initialize the CLI, parse arguments, and execute commands.

    Args:
        args (list[str] | None): A list of command-line arguments. If None, uses sys.argv[1:].

    Returns:
        int: Exit code of the CLI execution. 0 for success, non-zero for failure.
    """
    if args is None:
        args = sys.argv[1:]

    try:
        parser: ArgumentParser = get_parser()
        opts: Namespace = parser.parse_args(args)
        command: str | None = opts.command
        if command is None:
            parser.print_help()
            return ExitCode.SUCCESS
        return _execute_command(command, opts)
    except Exception as e:
        print(f"Error initializing CLI: {e}", file=STDERR)
        return ExitCode.FAILURE


if __name__ == "__main__":
    main()
