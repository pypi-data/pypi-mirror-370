"""A module for GUI-related utilities using PyQt6. Optional Module."""

try:
    from .gui_tools import QTApplication, get_text, select_color

    __all__ = ["QTApplication", "get_text", "select_color"]
except ImportError as e:
    raise ImportError("PyQt6 is required for GUI functionality. Install it with: uv pip install bear-utils[gui]") from e
