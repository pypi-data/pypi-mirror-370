"""A module for input dialogs using PyQt6."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog, QLineEdit

from .qt_app import QTApplication


class InputDialog(QTApplication):
    """A class for displaying various input dialogs using PyQt6."""

    def get_text(
        self,
        title: str = "Input",
        label: str = "Enter text:",
        default: str = "",
        echo_mode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal,
    ) -> str | None:
        """Shows a text input dialog.

        Args:
            title: Dialog window title
            label: Text label above the input field
            default: Default text in the input field
            echo_mode: How text is displayed (Normal, Password, etc.)
            input_mode: Type of text input (TextInput, IntInput, etc.)

        Returns:
            str: Entered text or None if canceled
        """
        try:
            text, ok = QInputDialog.getText(
                None,
                title,
                label,
                echo_mode,
                default,
                Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint,
            )
            return text if ok else None
        except Exception as e:
            self.console.error(f"Error in text input dialog: {e}")
            return None

    def get_password(
        self,
        title: str = "Password",
        label: str = "Enter password:",
        default: str = "",
    ) -> str | None:
        """Shows a password input dialog with masked text.

        Args:
            title: Dialog window title
            label: Text label above the input field
            default: Default text in the input field

        Returns:
            str: Entered password or None if canceled
        """
        return self.get_text(
            title=title,
            label=label,
            default=default,
            echo_mode=QLineEdit.EchoMode.Password,
        )

    def get_int(
        self,
        title: str = "Input",
        label: str = "Enter number:",
        default: int = 0,
        min_value: int = -2147483647,
        max_value: int = 2147483647,
        step: int = 1,
    ) -> int | None:
        """Shows an integer input dialog with spinner.

        Args:
            title: Dialog window title
            label: Text label above the input field
            default: Default value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            step: Step size for spinner buttons

        Returns:
            int: Entered integer or None if canceled
        """
        try:
            value, ok = QInputDialog.getInt(
                None,
                title,
                label,
                default,
                min_value,
                max_value,
                step,
                Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint,
            )
            return value if ok else None
        except Exception as e:
            self.console.error(f"Error in integer input dialog: {e}")
            return None

    def get_double(
        self,
        title: str = "Input",
        label: str = "Enter number:",
        default: float = 0.0,
        min_value: float = -2147483647.0,
        max_value: float = 2147483647.0,
        decimals: int = 2,
    ) -> float | None:
        """Shows a floating-point input dialog with spinner.

        Args:
            title: Dialog window title
            label: Text label above the input field
            default: Default value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            decimals: Number of decimal places to show

        Returns:
            float: Entered value or None if canceled
        """
        try:
            value, ok = QInputDialog.getDouble(
                None,
                title,
                label,
                default,
                min_value,
                max_value,
                decimals,
                Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint,
            )
            return value if ok else None
        except Exception as e:
            self.console.error(f"Error in double input dialog: {e}")
            return None

    def get_item(
        self,
        title: str = "Select",
        label: str = "Select an item:",
        items: list[str] | None = None,
        current: int = 0,
        editable: bool = False,
    ) -> str | None:
        """Shows a dropdown selection dialog.

        Args:
            title: Dialog window title
            label: Text label above the dropdown
            items: List of items to choose from
            current: Index of the initially selected item
            editable: Whether the text can be edited

        Returns:
            str: Selected or entered text, or None if canceled
        """
        if items is None:
            items = ["Item 1", "Item 2", "Item 3"]

        try:
            item, ok = QInputDialog.getItem(
                None,
                title,
                label,
                items,
                current,
                editable,
                Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint,
            )
            return item if ok else None
        except Exception as e:
            self.console.error(f"Error in item selection dialog: {e}")
            return None

    def get_multiline_text(self, title: str = "Input", label: str = "Enter text:", default: str = "") -> str | None:
        """Shows a multi-line text input dialog.

        Args:
            title: Dialog window title
            label: Text label above the input field
            default: Default text in the input field

        Returns:
            str: Entered text or None if canceled
        """
        try:
            text, ok = QInputDialog.getMultiLineText(
                None,
                title,
                label,
                default,
                Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint,
            )
            return text if ok else None
        except Exception as e:
            self.console.error(f"Error in multiline text input dialog: {e}")
            return None


def get_text(
    title: str = "Input",
    label: str = "Enter text:",
    default: str = "",
    echo_mode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal,
) -> str | None:
    """Displays a text input dialog and returns the text entered by the user."""
    qt_app = InputDialog()
    return qt_app.get_text(title, label, default, echo_mode)


def get_password(title: str = "Password", label: str = "Enter password:", default: str = "") -> str | None:
    """Displays a password input dialog with masked text."""
    qt_app = InputDialog()
    return qt_app.get_password(title, label, default)


def get_api_key(
    title: str = "API Key Required",
    label: str = "Enter API key:",
    default: str = "",
    service_name: str = "",
) -> str | None:
    """Shows a secure input dialog optimized for entering API keys.

    Args:
        title: Dialog window title
        label: Text label above the input field
        default: Default API key (rarely used, but available)
        service_name: Name of the service requiring the API key

    Returns:
        str: Entered API key or None if canceled
    """
    qt_app = InputDialog()

    # Customize the label if service name is provided
    if service_name:
        label = f"Enter API key for {service_name}:"
        title = f"{service_name} API Key"

    return qt_app.get_text(title=title, label=label, default=default, echo_mode=QLineEdit.EchoMode.Password)


def get_int(
    title: str = "Input",
    label: str = "Enter number:",
    default: int = 0,
    min_value: int = -2147483647,
    max_value: int = 2147483647,
    step: int = 1,
) -> int | None:
    """Displays an integer input dialog with spinner buttons."""
    qt_app = InputDialog()
    return qt_app.get_int(title, label, default, min_value, max_value, step)


def get_double(
    title: str = "Input",
    label: str = "Enter number:",
    default: float = 0.0,
    min_value: float = -2147483647.0,
    max_value: float = 2147483647.0,
    decimals: int = 2,
) -> float | None:
    """Displays a floating-point input dialog with spinner buttons."""
    qt_app = InputDialog()
    return qt_app.get_double(title, label, default, min_value, max_value, decimals)


def get_item(
    title: str = "Select",
    label: str = "Select an item:",
    items: list[str] | None = None,
    current: int = 0,
    editable: bool = False,
) -> str | None:
    """Displays a dropdown selection dialog."""
    qt_app = InputDialog()
    return qt_app.get_item(title, label, items, current, editable)


def get_multiline_text(title: str = "Input", label: str = "Enter text:", default: str = "") -> str | None:
    """Displays a multi-line text input dialog."""
    qt_app = InputDialog()
    return qt_app.get_multiline_text(title, label, default)


if __name__ == "__main__":
    # Example usage
    api_key = get_api_key(
        title="API Key Required",
        label="Enter your API key:",
        default="",
        service_name="MyService",
    )
    print(f"API Key: {api_key}")
