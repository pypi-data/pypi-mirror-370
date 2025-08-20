"""Log File Handler Module"""

from pathlib import Path
from typing import Any, ClassVar, cast

from ._base_file_handler import FileHandler


class LogFileHandler(FileHandler):
    """Class for handling .log files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["log"]
    valid_types: ClassVar[tuple[type, ...]] = (str,)

    @FileHandler.ValidateFileType
    def read_file(self, file_path: Path) -> str:
        """Read a log file and return its content as a string."""
        try:
            super().read_file(file_path)
            with open(file_path, encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    @FileHandler.ValidateFileType
    def write_file(self, file_path: Path, data: dict[str, Any] | str, **_) -> None:
        """Write data to a log file."""
        try:
            super().write_file(file_path=file_path, data=data)
            self.check_data_type(data=data, valid_types=self.valid_types)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(cast("str", data))
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    def present_file(self, data: dict[str, Any] | list[str] | str, **_) -> str:
        """Present data as a string."""
        if isinstance(data, dict):
            data = "\n".join(f"{key}: {value}" for key, value in data.items())
        return str(data)
