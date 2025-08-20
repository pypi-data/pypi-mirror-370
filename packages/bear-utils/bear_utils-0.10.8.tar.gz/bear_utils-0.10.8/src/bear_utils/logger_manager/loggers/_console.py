from collections.abc import Callable, Mapping
from datetime import datetime
import sys
import threading
from time import monotonic
from typing import TYPE_CHECKING, Literal, TextIO, cast

from rich._log_render import FormatTimeCallable, LogRender
from rich._null_file import NULL_FILE
from rich.console import COLOR_SYSTEMS, Console, ConsoleThreadLocals, RenderHook, _is_jupyter, detect_legacy_windows
from rich.emoji import EmojiVariant
from rich.highlighter import NullHighlighter, ReprHighlighter
from rich.style import StyleType
from rich.text import Text
from rich.theme import Theme, ThemeStack
from rich.themes import DEFAULT

from bear_utils.logger_manager._log_level import LogLevel

if TYPE_CHECKING:
    from rich.color import ColorSystem
    from rich.live import Live
    from rich.segment import Segment

HighlighterType = Callable[[str, Text], Text] | Text
JUPYTER_DEFAULT_COLUMNS = 115
JUPYTER_DEFAULT_LINES = 100
WINDOWS: bool = sys.platform == "win32"

_null_highlighter = NullHighlighter()


class LogConsole[T: TextIO](Console):
    """A Console from Rich that has added methods named after the logger methods."""

    def __init__(
        self,
        *,
        color_system: Literal["auto", "standard", "256", "truecolor", "windows"] | None = "auto",
        force_terminal: bool | None = None,
        force_jupyter: bool | None = None,
        force_interactive: bool | None = None,
        soft_wrap: bool = False,
        theme: Theme | None = None,
        stderr: bool = False,
        file: T | None = None,
        quiet: bool = False,
        width: int | None = None,
        height: int | None = None,
        style: StyleType | None = None,
        no_color: bool | None = None,
        tab_size: int = 8,
        record: bool = False,
        markup: bool = True,
        emoji: bool = True,
        emoji_variant: EmojiVariant | None = None,
        highlight: bool = True,
        log_time: bool = True,
        log_path: bool = True,
        log_time_format: str | FormatTimeCallable = "[%X]",
        highlighter: HighlighterType | None = ReprHighlighter(),  # type: ignore[assignment] # noqa: B008
        legacy_windows: bool | None = None,
        safe_box: bool = True,
        get_datetime: Callable[[], datetime] | None = None,
        get_time: Callable[[], float] | None = None,
        _environ: Mapping[str, str] | None = None,
        level: str | int | LogLevel = LogLevel.DEBUG,
    ):
        # Copy of os.environ allows us to replace it for testing
        if _environ is not None:
            self._environ = _environ

        self.is_jupyter = _is_jupyter() if force_jupyter is None else force_jupyter
        if self.is_jupyter:
            if width is None:
                jupyter_columns = self._environ.get("JUPYTER_COLUMNS")
                if jupyter_columns is not None and jupyter_columns.isdigit():
                    width = int(jupyter_columns)
                else:
                    width = JUPYTER_DEFAULT_COLUMNS
            if height is None:
                jupyter_lines = self._environ.get("JUPYTER_LINES")
                if jupyter_lines is not None and jupyter_lines.isdigit():
                    height = int(jupyter_lines)
                else:
                    height = JUPYTER_DEFAULT_LINES

        self.tab_size = tab_size
        self.record = record
        self._markup = markup
        self._emoji = emoji
        self._emoji_variant: EmojiVariant | None = emoji_variant
        self._highlight = highlight
        self.legacy_windows: bool = (
            (detect_legacy_windows() and not self.is_jupyter) if legacy_windows is None else legacy_windows
        )

        if width is None:
            columns = self._environ.get("COLUMNS")
            if columns is not None and columns.isdigit():
                width = int(columns) - self.legacy_windows
        if height is None:
            lines = self._environ.get("LINES")
            if lines is not None and lines.isdigit():
                height = int(lines)

        self.soft_wrap = soft_wrap
        self._width = width
        self._height = height

        self._color_system: ColorSystem | None

        self._force_terminal = None
        if force_terminal is not None:
            self._force_terminal = force_terminal

        self._file: T | None = file
        self.quiet = quiet
        self.stderr = stderr

        if color_system is None:
            self._color_system = None
        elif color_system == "auto":
            self._color_system = self._detect_color_system()
        else:
            self._color_system = COLOR_SYSTEMS[color_system]

        self._lock = threading.RLock()
        self._log_render = LogRender(
            show_time=log_time,
            show_path=log_path,
            time_format=log_time_format,
        )
        self.highlighter: HighlighterType = highlighter or _null_highlighter  # type: ignore[assignment]
        self.safe_box = safe_box
        self.get_datetime = get_datetime or datetime.now
        self.get_time = get_time or monotonic
        self.style = style
        self.no_color = no_color if no_color is not None else self._environ.get("NO_COLOR", "") != ""
        self.is_interactive = (
            (self.is_terminal and not self.is_dumb_terminal) if force_interactive is None else force_interactive
        )
        self._record_buffer_lock = threading.RLock()
        self._thread_locals = ConsoleThreadLocals(theme_stack=ThemeStack(DEFAULT if theme is None else theme))
        self._record_buffer: list[Segment] = []
        self._render_hooks: list[RenderHook] = []
        self._live: Live | None = None
        self._is_alt_screen = False
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)

    @property
    def file(self) -> T:
        """Get the file object to write to."""
        file = self._file or (sys.stderr if self.stderr else sys.stdout)
        file = getattr(file, "rich_proxied_file", file)
        if file is None:
            file = NULL_FILE
        return cast("T", file)

    @file.setter
    def file(self, new_file: T) -> None:  # type: ignore[override]
        """Set a new file object."""
        self._file = new_file

    def _log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Log a message at the specified level.

        Args:
            level (LogLevel): The log level for the message. We aren't using this parameter in the current implementation,
            msg (object): The message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if level.value >= self.level.value:
            """Log a message at the specified level."""
            with self._lock:
                if not self.quiet:
                    self.log(msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an informational message to the console."""
        self._log(LogLevel.INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message to the console."""
        self._log(LogLevel.WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message to the console."""
        self._log(LogLevel.ERROR, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message to the console."""
        self._log(LogLevel.DEBUG, msg, *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Log a verbose message to the console."""
        self._log(LogLevel.VERBOSE, msg, *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        """Log a success message to the console."""
        self._log(LogLevel.SUCCESS, msg, *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        """Log a failure message to the console."""
        self._log(LogLevel.FAILURE, msg, *args, **kwargs)

    def exception(self, msg: object, *args, **kwargs) -> None:
        """Log an exception message to the console."""
        self._log(LogLevel.ERROR, msg, *args, **kwargs)


if __name__ == "__main__":
    from io import StringIO

    console = LogConsole(file=StringIO())
    console.info("This is an info message")
    value = console.file
    print(value.getvalue())  # Print the captured log messages from StringIO
