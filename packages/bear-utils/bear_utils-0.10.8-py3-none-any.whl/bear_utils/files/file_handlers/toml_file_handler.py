"""TOML File Handler Module"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

import toml

from ._base_file_handler import FileHandler


class TomlFileHandler(FileHandler):
    """Class for handling .toml files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["toml"]
    valid_types: ClassVar[tuple[type, ...]] = (dict, str)

    @FileHandler.ValidateFileType
    def read_file(self, file_path: Path) -> dict:
        """Read a TOML file and return its content as a dictionary."""
        try:
            super().read_file(file_path)

            return toml.load(file_path)
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    @FileHandler.ValidateFileType
    def write_file(self, file_path: Path, data: dict[str, Any] | str, **kwargs) -> None:
        """Write data to a TOML file."""
        try:
            super().write_file(file_path=file_path, data=data)
            self.check_data_type(data=data, valid_types=self.valid_types)
            with open(file_path, "w", encoding="utf-8") as file:
                if isinstance(data, dict):
                    toml.dump(data, file, **kwargs)
                else:
                    file.write(data)
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    def present_file(self, data: dict[str, Any] | str, **_) -> str:
        """Present data as a string."""
        # TODO: Actually implement this method to format TOML data nicely
        return str(data)


@dataclass
class PyProjectToml:
    """Dataclass for handling pyproject.toml files"""

    name: str
    version: str
    description: str | None = None
    author_name: str | None = None
    author_email: str | None = None
    dependencies: list[str] | None = None

    def __post_init__(self):
        if self.dependencies:
            self.dependencies = [dep.split(" ")[0] for dep in self.dependencies if isinstance(dep, str)]
            self.dependencies = [dep.split(">=")[0] for dep in self.dependencies]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PyProjectToml":
        """Create a PyProjectToml instance from a dictionary."""
        data = data.get("project", {})
        authors: dict = data.get("authors", {})[0]
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description"),
            author_name=authors.get("name") if authors else None,
            author_email=authors.get("email") if authors else None,
            dependencies=data.get("dependencies", []),
        )
