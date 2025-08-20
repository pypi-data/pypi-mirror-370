"""A module for various utilities in Bear Utils extras."""

from singleton_base import SingletonBase

from bear_utils.graphics.font._utils import ascii_header

from ._tools import Counter
from ._zapper import zap, zap_as, zap_as_multi, zap_get, zap_multi
from .clipboard import ClipboardManager, clear_clipboard, copy_to_clipboard, paste_from_clipboard, shutil_which
from .platform_utils import OS, get_platform, is_linux, is_macos, is_windows
from .utility_classes._holder import BufferSpace, StringSpace
from .utility_classes._wrapper import BaseWrapper, ConsoleWrapper, LoggerWrapper, StringIOWrapper
from .utility_classes.multi_buffer import MultiBuffer
from .wrappers.add_methods import add_comparison_methods

__all__ = [
    "OS",
    "BaseWrapper",
    "BufferSpace",
    "ClipboardManager",
    "ConsoleWrapper",
    "Counter",
    "LoggerWrapper",
    "MultiBuffer",
    "SingletonBase",
    "StringIOWrapper",
    "StringSpace",
    "add_comparison_methods",
    "ascii_header",
    "clear_clipboard",
    "copy_to_clipboard",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "paste_from_clipboard",
    "shutil_which",
    "zap",
    "zap_as",
    "zap_as_multi",
    "zap_get",
    "zap_multi",
]
