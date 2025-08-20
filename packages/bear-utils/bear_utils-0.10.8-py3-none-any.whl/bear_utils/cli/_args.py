import sys

from bear_utils.constants._exit_code import FAILURE, SUCCESS, ExitCode


def args_process(args: list[str] | None = None) -> tuple[list[str], ExitCode]:
    args = sys.argv[1:] if args is None else args

    if not args:
        return [], FAILURE

    return args, SUCCESS
