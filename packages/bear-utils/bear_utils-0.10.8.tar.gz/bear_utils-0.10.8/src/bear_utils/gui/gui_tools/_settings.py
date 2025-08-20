from typing import Any

from PyQt6.QtCore import QSettings

from .qt_app import QTApplication


class Settings(QTApplication):
    """Settings class that inherits from QTApplication for standalone use."""

    def __init__(self, app_name: str = "Settings App", org_name: str = "YourOrg", org_domain: str = "org.domain"):
        super().__init__(app_name, org_name, org_domain)

        self._settings = QSettings(org_name, app_name)

    def get(self, key: str, default: Any = None, value_type: type | None = None) -> Any:
        """Get a setting value with optional type conversion."""
        if value_type:
            return self._settings.value(key, default, type=value_type)
        return self._settings.value(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings.setValue(key, value)

    def has(self, key: str) -> bool:
        """Check if a setting exists."""
        return self._settings.contains(key)

    def remove_key(self, key: str) -> None:
        """Remove a setting."""
        self._settings.remove(key)

    def clear_settings(self) -> None:
        """Clear all settings."""
        self._settings.clear()
