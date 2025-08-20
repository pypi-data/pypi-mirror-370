"""Text File Handler Module for .txt files"""

import json
from pathlib import Path
from typing import Any, ClassVar, overload

from ._base_file_handler import FileHandler


class TextFileHandler(FileHandler):
    """Class for handling .txt files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["txt"]
    valid_types: ClassVar[tuple[type, ...]] = (str, dict, list)

    @FileHandler.ValidateFileType
    def read_file(self, file_path: Path) -> str:
        """Read a text file and return its content as a string."""
        try:
            super().read_file(file_path)
            with open(file_path, encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    @overload
    def write_file(self, file_path: Path, data: str) -> None: ...

    @overload
    def write_file(self, file_path: Path, data: list[str]) -> None: ...

    @overload
    def write_file(self, file_path: Path, data: dict[str, Any], indent: int = 2, sort_keys: bool = False) -> None: ...

    @FileHandler.ValidateFileType
    def write_file(
        self,
        file_path: Path,
        data: dict[str, Any] | str,
        indent: int = 2,
        sort_keys: bool = False,
        **_,
    ) -> None:
        """Write data to a text file."""
        try:
            super().write_file(file_path=file_path, data=data)
            self.check_data_type(data=data, valid_types=self.valid_types)
            if isinstance(data, dict):
                data = json.dumps(data, indent=indent, sort_keys=sort_keys)
            elif isinstance(data, list):
                data = "\n".join(data)
            file_path.write_text(data=data, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    def present_file(self, data: dict[str, Any] | list[str] | Any, **kwargs) -> str:
        """Present data as a string.

        This method converts the data to a string representation if it is a dictionary,

        Args:
            data (dict[str, Any] | str): Data to present
        Returns:
            str: String representation of the data
        """
        converted_data: str | None = None
        if data is None:
            raise ValueError("No data to present")
        if isinstance(data, dict):
            converted_data = json.dumps(data, indent=kwargs.get("indent", 2), sort_keys=kwargs.get("sort", False))
        elif isinstance(data, list):
            converted_data = "\n".join(data)
        elif not isinstance(data, str):
            raise TypeError("Data must be a string for text files")

        return str(converted_data if isinstance(data, dict | list) else data)
