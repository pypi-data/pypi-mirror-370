"""A module for managing a PyQt6 application instance and providing utility methods for dialogs and menus."""

import atexit
from collections.abc import Callable
from pathlib import Path
import sys

from PyQt6.QtCore import QCoreApplication, QObject, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QMenu, QMenuBar, QMessageBox, QVBoxLayout

from bear_utils.logger_manager import VERBOSE, ConsoleLogger

from ._types import ActionHolder


class QTApplication(QObject):
    """Singleton class to manage the QApplication instance.

    This ensures that only one instance of QApplication is created.
    """

    def __init__(
        self,
        app_name: str = "Qt Application",
        org_name: str = "Organization",
        org_domain: str = "org.domain",
    ) -> None:
        """Initialize the QTApplication instance."""
        super().__init__()
        if not QApplication.instance():
            self.app: QCoreApplication | None = QApplication(sys.argv)
            if self.app:
                self.app.setApplicationName(app_name)
                self.app.setOrganizationName(org_name)
                self.app.setOrganizationDomain(org_domain)
        else:
            self.app = QApplication.instance()
        self.console: ConsoleLogger = ConsoleLogger.get_instance(init=True, name=app_name, level=VERBOSE)
        atexit.register(self.cleanup)

    def _default_exit_shortcuts(self) -> None:
        """Set up default exit shortcuts for the application."""
        self._add_shortcut(QKeySequence("Escape"), self.cleanup)

    def _add_shortcut(self, shortcut: QKeySequence | QKeySequence.StandardKey, callback: Callable) -> None:
        """Add a shortcut to the application."""
        q_shortcut = QShortcut(shortcut, self.dialog)
        q_shortcut.activated.connect(callback)

    def _add_to_menu(self, menu_name: str, actions: list[ActionHolder]) -> QMenu:
        """Add an action to the menu."""
        menu = QMenu(menu_name, self.dialog)
        for a in actions:
            action: QAction = self._add_action(text=a.text, shortcut=a.shortcut, callback=a.callback)
            menu.addAction(action)
        return menu

    def _add_action(self, text: str, shortcut: str, callback: Callable) -> QAction:
        """Create and return an action for the menu."""
        action = QAction(text, self.dialog)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    def _start_menu_bar(self) -> None:
        """Create and setup the menu bar."""
        self.menu_bar = QMenuBar(self.dialog)

    def _end_menu_bar(self, menus_to_add: list[QMenu]) -> None:
        for menu in menus_to_add:
            self.menu_bar.addMenu(menu)
        self.main_layout.setMenuBar(self.menu_bar)

    def _setup_initial_window(self, title: str, icon_path: Path, width: int, height: int) -> None:
        """Create and show the initial window with loading indicator."""
        self.dialog = QDialog(None)
        self.dialog.setWindowTitle(title)
        self.dialog.setMinimumSize(width, height)

        if icon_path.exists():
            self.dialog.setWindowIcon(QIcon(str(icon_path)))

        self.main_layout = QVBoxLayout(self.dialog)
        self.loading_label = QLabel("Loading...")
        self.main_layout.addWidget(self.loading_label)

    def get_app(self) -> QApplication | QCoreApplication | None:
        """Get the current QApplication instance."""
        if not self.app and not QApplication.instance():
            self.app = QApplication(sys.argv)
        elif not self.app:
            self.app: QCoreApplication | None = QApplication.instance()
        return self.app

    def show_message(
        self,
        message: str,
        title: str = "Message",
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
        on_ok_action: Callable[[], None] | None = None,
    ) -> None:
        """Show a message dialog with configurable icon and action.

        Args:
            message: The message to display
            title: Dialog title
            icon: Message box icon (Information, Warning, Critical, Question)
            on_ok_action: Function to call when OK is clicked
        """
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setWindowModality(Qt.WindowModality.ApplicationModal)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Ok and on_ok_action:
            on_ok_action()

    def show_warning(
        self, message: str, on_ok_action: Callable[[], None] | None = None, title: str = "Warning"
    ) -> None:
        """Show a warning dialog."""
        self.show_message(message, title=title, icon=QMessageBox.Icon.Warning, on_ok_action=on_ok_action)

    def show_error(self, message: str, on_ok_action: Callable[[], None] | None = None, title: str = "Error") -> None:
        """Show an error dialog."""
        self.show_message(message, title=title, icon=QMessageBox.Icon.Critical, on_ok_action=on_ok_action)

    def show_info(self, message: str, title: str = "Information") -> None:
        """Show an information dialog."""
        self.show_message(message, title=title, icon=QMessageBox.Icon.Information)

    def cleanup(self) -> None:
        """Clean up the QTApplication instance."""
        if self.app:
            self.console.verbose("Cleaning up QTApplication instance.")
            self.app.quit()
            self.app = None


if __name__ == "__main__":
    qt_app = QTApplication()
    qt_app.show_info("This is an info message.")
    qt_app.show_warning("This is a warning message.")
    qt_app.show_error("This is an error message.")
    qt_app.cleanup()
