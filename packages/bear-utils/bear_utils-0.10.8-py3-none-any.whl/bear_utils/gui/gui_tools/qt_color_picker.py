"""A module for a color picker dialog using PyQt6."""

from dataclasses import dataclass
from typing import Any

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog
from rich.color_triplet import ColorTriplet

from .qt_app import QTApplication


@dataclass
class ColorInfo:
    """Data class to hold color information."""

    qcolor: QColor
    hex: str
    rgb: ColorTriplet
    rgba: tuple[int, int, int, int]
    hsv: tuple[int, int, int]


class QTColorPicker(QTApplication):
    """Singleton class to manage the color picker dialog."""

    def select_color(
        self,
        initial_color: str | None = None,
        title: str = "Select Color",
        options: Any | None = None,
    ) -> ColorInfo | None:
        """Shows a color selection dialog and returns the selected color.

        Args:
            initial_color: Initial color to show in the dialog. Can be:
                           - QColor object
                           - Hex string (e.g., "#FF5733")
                           - RGB tuple (e.g., (255, 87, 51))
            title (str): The dialog window title
            options: QColorDialog options (optional)

        Returns:
            dict: Color information with keys:
                  - 'qcolor': QColor object
                  - 'hex': Hex string (e.g., "#FF5733")
                  - 'rgb': RGB tuple (e.g., (255, 87, 51))
                  - 'rgba': RGBA tuple (e.g., (255, 87, 51, 255))
                  - 'hsv': HSV tuple (e.g., (16, 80, 100))
                  Or None if dialog was canceled
        """
        try:
            dialog = QColorDialog()
            channels_num = 3
            if title:
                dialog.setWindowTitle(title)

            if options:
                dialog.setOptions(options)

            if initial_color:
                if isinstance(initial_color, QColor):
                    dialog.setCurrentColor(initial_color)
                elif isinstance(initial_color, str) and initial_color.startswith("#"):
                    dialog.setCurrentColor(QColor(initial_color))
                elif isinstance(initial_color, tuple) and len(initial_color) >= channels_num:
                    r, g, b = initial_color[:channels_num]
                    a = initial_color[channels_num] if len(initial_color) > channels_num else 255
                    dialog.setCurrentColor(QColor(int(r), int(g), int(b), int(a)))

            if dialog.exec() == QColorDialog.DialogCode.Accepted:
                selected_color = dialog.selectedColor()

                if not selected_color.isValid():
                    return None

                return ColorInfo(
                    qcolor=selected_color,
                    hex=selected_color.name(),
                    rgb=ColorTriplet(selected_color.red(), selected_color.green(), selected_color.blue()),
                    rgba=(
                        selected_color.red(),
                        selected_color.green(),
                        selected_color.blue(),
                        selected_color.alpha(),
                    ),
                    hsv=(selected_color.hue(), selected_color.saturation(), selected_color.value()),
                )
            return None
        except Exception as e:
            self.console.error(f"Error in color selection dialog: {e}")
            return None


def select_color(
    initial_color: str | None = None,
    title: str = "Select Color",
    options: Any | None = None,
) -> ColorInfo | None:
    """Select a color using the QTColorPicker singleton instance.

    Args:
        initial_color: Initial color to show in the dialog. Can be:
                       - QColor object
                       - Hex string (e.g., "#FF5733")
                       - RGB tuple (e.g., (255, 87, 51))
        title (str): The dialog window title
        options: QColorDialog options (optional)

    Returns:
        dict: Color information with keys:
              - 'qcolor': QColor object
              - 'hex': Hex string (e.g., "#FF5733")
              - 'rgb': RGB tuple (e.g., (255, 87, 51))
              - 'rgba': RGBA tuple (e.g., (255, 87, 51, 255))
              - 'hsv': HSV tuple (e.g., (16, 80, 100))
              Or None if dialog was canceled
    """
    qt_color_picker = QTColorPicker()
    return qt_color_picker.select_color(initial_color, title, options)


if __name__ == "__main__":
    # Example usage
    color_picker = QTColorPicker()
    selected_color: ColorInfo | None = color_picker.select_color(initial_color="#FF5733", title="Choose a Color")
    if selected_color:
        color_picker.console.info(f"Selected Color: {selected_color}")
    else:
        color_picker.console.warning("No color selected.")
