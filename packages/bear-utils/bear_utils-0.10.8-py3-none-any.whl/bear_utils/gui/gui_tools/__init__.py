"""A module for managing a PyQt6 application instance and providing utility methods for dialogs and menus."""

try:
    from .qt_app import QTApplication
    from .qt_color_picker import select_color
    from .qt_input_dialog import get_text

    __all__ = ["QTApplication", "get_text", "select_color"]
except ImportError as e:
    raise ImportError("PyQt6 is required for GUI functionality. Install it with: pip install bear-utils[gui]") from e
