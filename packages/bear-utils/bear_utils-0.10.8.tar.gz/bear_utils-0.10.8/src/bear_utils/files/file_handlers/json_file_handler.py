"""JsonFileHandler: A class for handling JSON files in Bear Utils."""

import json
from pathlib import Path
from typing import Any, ClassVar, overload

from ._base_file_handler import FileHandler


class JsonFileHandler(FileHandler):
    """Class for handling JSON files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["json"]
    valid_types: ClassVar[tuple[type, ...]] = (dict, list, str)

    @FileHandler.ValidateFileType
    def read_file(self, file_path: Path, **kwargs) -> dict[str, Any]:
        """Read a JSON file and return its content as a dictionary."""
        try:
            super().read_file(file_path=file_path)
            with open(file_path, encoding="utf-8") as file:
                return json.load(file, **kwargs)
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
        """Write data to a JSON file."""
        try:
            super().write_file(file_path=file_path, data=data)
            self.check_data_type(data=data, valid_types=self.valid_types)
            data = self.present_file(data, indent=indent, sort_keys=sort_keys)
            file_path.write_text(data=data, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    @overload
    def present_file(self, data: dict[str, Any], indent: int = 2, sort_keys: bool = False) -> str: ...

    @overload
    def present_file(self, data: str, **kwargs) -> str: ...

    def present_file(self, data: dict[str, Any] | str, indent: int = 2, sort_keys: bool = False, **_) -> str:
        """Present data as a JSON string."""
        try:
            if isinstance(data, list):
                data = {"data": data}
            elif isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON string: {e}") from e
            return json.dumps(data, indent=indent, sort_keys=sort_keys)
        except Exception as e:
            raise ValueError(f"Error presenting file: {e}") from e
