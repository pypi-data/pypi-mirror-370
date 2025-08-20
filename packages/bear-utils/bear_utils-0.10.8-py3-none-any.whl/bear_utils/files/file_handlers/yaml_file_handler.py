"""YamlFileHandler class for handling YAML files."""

from pathlib import Path
from typing import Any, ClassVar

import yaml

from ._base_file_handler import FileHandler


class YamlFileHandler(FileHandler):
    """Class for handling .yaml/.yml files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["yaml", "yml"]
    valid_types: ClassVar[tuple[type, ...]] = (dict, str)

    @FileHandler.ValidateFileType
    def unsafe_read_file(self, file_path: Path, **kwargs) -> dict[str, Any]:
        """Read YAML file with potentially unsafe loader.

        WARNING: This method can execute arbitrary code and should only be used
        with trusted files.

        Args:
            file_path: Path to the YAML file
            **kwargs: Additional arguments passed to yaml.load

        Returns:
            Dictionary containing the parsed YAML data
        """
        try:
            super().read_file(file_path=file_path)
            with open(file=file_path, encoding="utf-8") as file:
                return yaml.load(stream=file, **kwargs)  # noqa: S506 # Using unsafe loader intentionally
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    @FileHandler.ValidateFileType
    def read_file(self, file_path: Path) -> dict[str, Any]:
        """Read YAML file safely."""
        try:
            super().read_file(file_path=file_path)
            with open(file=file_path, encoding="utf-8") as file:
                return yaml.safe_load(stream=file)
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    @FileHandler.ValidateFileType
    def write_file(self, file_path: Path, data: dict[str, Any] | str, **kwargs) -> None:
        """Write data to a YAML file."""
        try:
            super().write_file(file_path=file_path, data=data)
            self.check_data_type(data=data, valid_types=self.valid_types)
            with open(file=file_path, mode="w", encoding="utf-8") as file:
                yaml.dump(data, stream=file, default_flow_style=False, sort_keys=False, **kwargs)
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    def present_file(self, data: dict[str, Any] | str, **kwargs) -> str:
        """Present data as a YAML string."""
        try:
            return yaml.dump(data, default_flow_style=False, sort_keys=False, **kwargs)
        except Exception as e:
            raise ValueError(f"Error presenting file: {e}") from e
