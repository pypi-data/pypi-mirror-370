from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, ClassVar, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


class FileHandler(ABC):
    """Abstract class for file handling with read, write, and present methods

    :attr ext str: File extension to check for.
    :method file_checker: Class method to check if file is of correct type.
    :method read_file: Read file method.
    :method write_file: Write file method.
    :method present_file: Present file method.
    """

    valid_extensions: ClassVar[list[str]] = []
    valid_types: ClassVar[tuple[type, ...]] = ()

    @classmethod
    def file_checker(cls, file_path: Path) -> bool:
        """Check if the file is of the correct type.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if the file is of the correct type, False otherwise
        """
        return file_path.suffix.lstrip(".") in cls.valid_extensions

    @classmethod
    def check_data_type(cls, data: dict[str, Any] | str, valid_types: tuple[type, ...]) -> None:
        """Check if the data is of the correct type.

        Args:
            data: Data to check the type of

        Returns:
            bool: True if the data is of the correct type, False otherwise
        """
        if not isinstance(data, valid_types):
            raise TypeError(f"Data must be one of {valid_types}, got {type(data)}")

    @classmethod
    def ValidateFileType(cls, method: Callable[P, R]) -> Callable[P, R]:  # noqa: N802 disable=invalid-name
        """Decorator to validate file type before executing a method.

        This decorator checks if the file is of the correct type before
        executing the method. If not, it raises a ValueError.

        Args:
            method: Method to decorate

        Returns:
            Decorated method
        """

        @wraps(method)
        def wrapper(self: "FileHandler", file_path: Path, *args: Any, **kwargs: Any) -> R:
            if not self.file_checker(file_path):
                raise ValueError(f"Invalid file type. Expected {self.valid_extensions}")
            return method(self, file_path, *args, **kwargs)  # type: ignore[return-value]

        return cast("Callable[P, R]", wrapper)

    @abstractmethod
    def read_file(self, file_path: Path) -> dict[str, Any] | str:
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

    @abstractmethod
    def write_file(self, file_path: Path, data: dict[str, Any] | str, **kwargs) -> None:
        if not file_path.parent.exists():
            if kwargs.get("mkdir", False):
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(f"Directory does not exist: {file_path.parent}. Set mkdir=True to create it.")

    @abstractmethod
    def present_file(self, data: dict[str, Any] | str) -> str: ...

    @staticmethod
    def get_file_info(file_path: Path) -> dict[str, Any]:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        return {
            "path": file_path,
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "is_file": file_path.is_file() if file_path.exists() else False,
            "modified": file_path.stat().st_mtime if file_path.exists() else None,
        }
