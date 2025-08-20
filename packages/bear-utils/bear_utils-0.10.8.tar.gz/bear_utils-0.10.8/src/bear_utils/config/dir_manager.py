"""Directory Manager Module for Bear Utils."""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class DirectoryManager:
    """A class to manage directories for bear_utils."""

    _base_path: ClassVar[Path] = Path.home() / ".config" / "bear_utils"
    _settings_path: ClassVar[Path] = _base_path / "settings"
    _temp_path: ClassVar[Path] = _base_path / "temp"

    def setup(self) -> None:
        """Ensure the base, settings, and temp directories exist."""
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._settings_path.mkdir(parents=True, exist_ok=True)
        self._temp_path.mkdir(parents=True, exist_ok=True)

    def clear_temp(self) -> None:
        """Clear the temporary directory."""
        if self.temp_path.exists():
            for item in self.temp_path.iterdir():
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()

    @property
    def base_path(self) -> Path:
        """Get the base path for bear_utils."""
        return self._base_path

    @property
    def settings_path(self) -> Path:
        """Get the path to the settings directory."""
        return self._settings_path

    @property
    def temp_path(self) -> Path:
        """Get the path to the temporary directory."""
        return self._temp_path


def get_base_path() -> Path:
    """Get the base path for bear_utils."""
    return DirectoryManager().base_path


def get_settings_path() -> Path:
    """Get the path to the settings directory."""
    return DirectoryManager().settings_path


def get_temp_path() -> Path:
    """Get the path to the temporary directory."""
    return DirectoryManager().temp_path


def setup_directories() -> None:
    """Set up the necessary directories for bear_utils."""
    DirectoryManager().setup()


def clear_temp_directory() -> None:
    """Clear the temporary directory."""
    DirectoryManager().clear_temp()
