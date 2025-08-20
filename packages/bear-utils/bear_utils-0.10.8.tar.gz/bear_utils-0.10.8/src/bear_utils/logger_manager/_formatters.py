from io import StringIO
import json
from logging import Formatter, LogRecord
from logging.handlers import BufferingHandler
import threading
from typing import TYPE_CHECKING

from prompt_toolkit import print_formatted_text
from prompt_toolkit.output.defaults import create_output
from rich.text import Text

from bear_utils.constants.date_related import DATE_TIME_FORMAT
from bear_utils.logger_manager._constants import SIMPLE_FORMAT, VERBOSE_CONSOLE_FORMAT
from bear_utils.logger_manager._handlers import ConsoleHandler
from bear_utils.logger_manager._misc import get_extra

if TYPE_CHECKING:
    from bear_utils.logger_manager._constants import LoggerExtraInfo


class ConsoleFormatter(Formatter):
    def __init__(self, fmt: str = SIMPLE_FORMAT, datefmt: str = DATE_TIME_FORMAT):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.log_format: str = fmt

    def format(self, record: LogRecord) -> str:
        extra: LoggerExtraInfo = get_extra(record)
        if self.log_format == VERBOSE_CONSOLE_FORMAT:
            log_level_color: str = extra["log_level_style"]
            style_name: str = extra.get("style_name", "")
            dynamic_format = self.log_format.format(
                log_level_color,
                style_name.upper(),
                log_level_color,
            )
            temp_formatter = Formatter(fmt=dynamic_format, datefmt=self.datefmt)
            return temp_formatter.format(record)

        if self.log_format == SIMPLE_FORMAT:
            record.msg = f"{record.msg}"

        return super().format(record)


class JSONLFormatter(Formatter):
    """A formatter that outputs log records in JSON Lines format."""

    def format(self, record: LogRecord) -> str:
        extra: LoggerExtraInfo = get_extra(record)
        log_entry = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.msg,
            "funcName": record.funcName,
            "name": record.name,
            "module": record.module,
            "line": record.lineno,
            **extra,
        }
        return json.dumps(log_entry)


class ConsoleBuffering(BufferingHandler):
    def __init__(
        self,
        capacity: int = 9999,
        console_handler: ConsoleHandler | None = None,
        return_auto: bool = False,
    ):
        super().__init__(capacity=capacity)
        # should come with a formatter before getting here
        self.console_handler: ConsoleHandler = console_handler or ConsoleHandler(
            print_func=lambda **kwargs: None, buffer_output=lambda **kwargs: ""
        )
        self._lock = threading.RLock()
        self.flush_auto = return_auto

    def flush_to_output(self) -> Text:
        """Flush all buffered records to the console handler."""
        with self._lock:
            output_buffer = StringIO()
            output = create_output(stdout=output_buffer)
            for record in self.buffer:
                formatted_msg = self.console_handler.emit(record, return_str=True)
                print_formatted_text(formatted_msg, output=output, end="\n")
        output = output_buffer.getvalue()
        output_buffer.close()
        self.buffer.clear()
        return Text.from_ansi(output)

    def trigger_flush(self) -> None:
        """Immediately flush all buffered records to console."""
        self.flush()

    def flush(self) -> None:
        """Flush all buffered records to the console handler."""
        if self.flush_auto:
            with self._lock:
                for record in self.buffer:
                    self.console_handler.emit(record)
                self.buffer.clear()
