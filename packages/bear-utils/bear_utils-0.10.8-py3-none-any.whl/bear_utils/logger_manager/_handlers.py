from collections.abc import Callable
from logging import Handler, LogRecord
from typing import TYPE_CHECKING, Any

from bear_utils.logger_manager._misc import extract_exec_info, get_extra

if TYPE_CHECKING:
    from bear_utils.logger_manager._constants import ExecValues, LoggerExtraInfo


class ConsoleHandler(Handler):
    def __init__(self, print_func: Callable, buffer_output: Callable) -> None:
        super().__init__()
        self.print_func: Callable = print_func
        self.buffer_func: Callable = buffer_output

    def emit(self, record: LogRecord, return_str: bool = False) -> Any:
        """Emit a log record either to console or return as string.

        Args:
            record: The LogRecord to emit
            return_str: If True, return formatted string instead of printing

        Returns:
            str if return_str=True, None otherwise
        """
        formatted_msg: str = self.format(record)
        extra: LoggerExtraInfo = get_extra(record)
        exec_values: dict[str, ExecValues] | None = extract_exec_info(record)
        exc_info: bool = bool(exec_values)
        style_name: str = extra.get("style_name", "")

        print_kwargs: dict[str, Any] = {
            "msg": formatted_msg,
            "style": style_name,
            "exc_info": exc_info if exc_info is not None else False,
            "exec_values": exec_values,
            "return_str": return_str,
        }
        if return_str:
            return self.buffer_func(**print_kwargs)

        return self.print_func(**print_kwargs)
