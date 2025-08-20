"""Settings Manager Module for Bear Utils."""

import atexit
from collections.abc import Generator
from contextlib import contextmanager
import hashlib
from pathlib import Path
from typing import Any, Self

from tinydb import Query, TinyDB

DEFAULT_PATH: Path = Path.home() / ".config" / "bear_utils"


def get_config_folder(path: str | Path | None = None) -> Path:
    """Get the path to the bear configuration directory."""
    config_path: Path = Path(path) if isinstance(path, str) else path or DEFAULT_PATH
    config_path.mkdir(parents=True, exist_ok=True)
    return config_path


def get_file_hash(file_path: Path) -> str:
    """Return the blake2 hash of the file at the given path."""
    hasher = hashlib.blake2b()
    with file_path.open("rb") as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


class SettingsManager:
    """A class to manage settings using TinyDB and an in-memory cache."""

    __slots__ = ("cache", "db", "file_hash", "file_path", "settings_name")

    def __init__(self, settings_name: str, folder_path: str | Path | None = None) -> None:
        """Initialize the SettingsManager with a specific settings name."""
        self.settings_name: str = settings_name
        self.cache: dict[str, Any] = {}
        file_name: str = f"{settings_name}.json"
        self.file_path: Path = get_config_folder(folder_path) / file_name
        self.db: TinyDB = TinyDB(self.file_path, indent=4, ensure_ascii=False)
        self.file_hash: str = get_file_hash(self.file_path) if self.file_path.exists() else ""
        atexit.register(self.close)
        self._load_cache()

    def __getattr__(self, key: str) -> Any:
        """Handle dot notation access for settings."""
        if key in self.__slots__:
            raise AttributeError(f"'{key}' not initialized")
        if key.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
        return self.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """Handle dot notation assignment for settings."""
        if key in self.__slots__:
            object.__setattr__(self, key, value)
            return
        self.set(key=key, value=value)

    def invalidate_cache(self) -> None:
        """Invalidate the in-memory cache."""
        self.cache.clear()
        self._load_cache()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        file_hash = get_file_hash(self.file_path)

        if file_hash != self.file_hash:
            self.invalidate_cache()
            self.file_hash = file_hash

        if key in self.cache:
            return self.cache[key]
        if result := self.db.search(Query().key == key):
            value = result[0]["value"]
            self.cache[key] = value
            return value
        return default

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self.db.upsert({"key": key, "value": value}, Query().key == key)
        self.cache[key] = value

    def has(self, key: str) -> bool:
        """Check if a setting exists."""
        return key in self.cache or self.db.contains(Query().key == key)

    def _load_cache(self) -> None:
        """Load all settings into cache."""
        for record in self.db.all():
            self.cache[record["key"]] = record["value"]

    def open(self) -> None:
        """Reopen the settings file after it's been closed/destroyed."""
        self.db = TinyDB(self.file_path, indent=4, ensure_ascii=False)
        self.cache = {}
        self._load_cache()

    def close(self) -> None:
        """Close the database."""
        if hasattr(self, "db"):
            self.db.close()
        if hasattr(self, "cache"):
            self.cache.clear()

    def destroy_settings(self) -> bool:
        """Delete the settings file."""
        if self.file_path.exists():
            self.close()
            self.file_path.unlink()
            self.cache.clear()
            return True
        return False

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def keys(self) -> list[str]:
        """Get all setting keys."""
        return list(self.cache.keys())

    def items(self) -> list[tuple[str, Any]]:
        """Get all setting key-value pairs."""
        return list(self.cache.items())

    def values(self) -> list[Any]:
        """Get all setting values."""
        return list(self.cache.values())

    def __len__(self):
        return len(self.cache)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<SettingsManager settings_name='{self.settings_name}'>"

    def __str__(self) -> str:
        return f"SettingsManager for '{self.settings_name}' with {len(self.keys())} settings."


_settings_managers: dict[str, SettingsManager] = {}


def get_settings_manager(settings_name: str) -> SettingsManager:
    """Get or create a SettingsManager instance."""
    if settings_name not in _settings_managers:
        _settings_managers[settings_name] = SettingsManager(settings_name=settings_name)
    return _settings_managers[settings_name]


@contextmanager
def settings(settings_name: str) -> Generator[SettingsManager]:
    """Context manager for SettingsManager."""
    sm: SettingsManager = get_settings_manager(settings_name)
    try:
        yield sm
    finally:
        sm.close()


if __name__ == "__main__":
    # Example usage of the SettingsManager
    with settings(settings_name="example_settings") as sm:
        sm.sample_setting = "This is a sample setting"
        print(sm.sample_setting)
        print(sm.keys())
        for key, value in sm.items():
            print("This is items()")
            print(f"Key: {key}, Value: {value}")
        print(sm.file_path)
