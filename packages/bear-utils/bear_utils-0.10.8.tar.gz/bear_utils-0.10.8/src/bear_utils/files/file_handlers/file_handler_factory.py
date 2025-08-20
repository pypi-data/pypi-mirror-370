"""Factory for creating and managing file handlers based on file types."""

from pathlib import Path
from typing import Any, cast
import warnings

from ._base_file_handler import FileHandler
from .json_file_handler import JsonFileHandler
from .log_file_handler import LogFileHandler
from .toml_file_handler import TomlFileHandler
from .txt_file_handler import TextFileHandler
from .yaml_file_handler import YamlFileHandler


class FileHandlerFactory:
    """Factory class to create and manage FileHandler instances based on file types.

    This factory maintains state about the current file path and can create appropriate
    handlers for different file types.
    """

    def __init__(self, file_path: Path | None = None) -> None:
        """Initialize the factory with an optional file path.

        Args:
            file_path: Optional Path to the file to handle
        """
        self._file_path: Path | None = file_path
        self._handler_registry: dict[str, type[FileHandler]] = {}
        self._handler_instance: FileHandler | None = None
        self._register_default_handlers()

    @property
    def file_path(self) -> Path | None:
        """Get the current file path."""
        return self._file_path

    @file_path.setter
    def file_path(self, path: Path) -> None:
        """Set the current file path and reset the handler instance.

        Args:
            path: New file path to set
        """
        self._file_path = path
        self._handler_instance = None

    def _register_default_handlers(self) -> None:
        """Register all default handlers from the package.

        This method imports and registers all standard FileHandler implementations.
        """
        try:
            self.register_handler(handler_class=JsonFileHandler)
            self.register_handler(handler_class=TextFileHandler)
            self.register_handler(handler_class=YamlFileHandler)
            self.register_handler(handler_class=LogFileHandler)
            self.register_handler(handler_class=TomlFileHandler)

        except ImportError as e:
            warnings.warn(f"Could not import all default handlers: {e}", UserWarning, stacklevel=2)

    def register_handler(self, handler_class: type[FileHandler]) -> None:
        """Register a handler class for its supported extensions.

        Args:
            handler_class: The FileHandler class to register
        """
        for ext in handler_class.valid_extensions:
            self._handler_registry[ext] = handler_class

    def get_handler_class(self, extension: str) -> type[FileHandler] | None:
        """Get the handler class for a specific extension.

        Args:
            extension: File extension (without the dot)

        Returns:
            FileHandler class for the extension or None if not found
        """
        return self._handler_registry.get(extension)

    def get_handler_for_path(self, file_path: Path | None = None) -> FileHandler:
        """Get or create a handler instance for the given path or the current path.

        Args:
            file_path: Path to get handler for (uses stored path if None)

        Returns:
            Appropriate FileHandler instance

        Raises:
            ValueError: If no file path is provided or stored, or if no handler exists for the file extension
        """
        path: Path | None = file_path or self._file_path
        if path is None:
            raise ValueError("No file path provided or stored in factory")

        if file_path is not None:
            self._file_path = file_path
            self._handler_instance = None

        if self._handler_instance and file_path is None:
            return self._handler_instance

        extension: str = path.suffix.lstrip(".")
        handler_class: type[FileHandler] | None = self.get_handler_class(extension)

        if handler_class is None:
            raise ValueError(f"No handler registered for extension: {extension}")

        handler = handler_class()
        if file_path is None:
            self._handler_instance = handler

        return handler

    def handle_file(self, operation: str, file_path: Path | None = None, data: Any = None, **kwargs) -> Any:
        """Handle file operations using the appropriate handler.

        Args:
            operation: Operation to perform ('read', 'write', 'present', 'info')
            file_path: Path to the file (uses stored path if None)
            data: Data for write operations
            **kwargs: Additional arguments for the operation

        Returns:
            Result of the operation

        Raises:
            ValueError: If an invalid operation is specified
        """
        path: Path | None = file_path or self._file_path
        if not path and operation != "present":
            raise ValueError("File path required for this operation")

        match operation:
            case "read":
                handler = self.get_handler_for_path(path)
                return handler.read_file(cast("Path", path), **kwargs)
            case "write":
                if data is None:
                    raise ValueError("Data required for write operation")
                handler = self.get_handler_for_path(path)
                return handler.write_file(cast("Path", path), data, **kwargs)
            case "present":
                if data is None:
                    raise ValueError("Data required for present operation")
                if path:
                    handler: FileHandler = self.get_handler_for_path(path)
                elif isinstance(data, dict):
                    yaml_class = self.get_handler_class("yaml")
                    if yaml_class:
                        handler = yaml_class()
                    else:
                        raise ValueError("No handler available for dict data")
                elif isinstance(data, str):
                    text_class = self.get_handler_class("txt")
                    if text_class:
                        handler = text_class()
                    else:
                        raise ValueError("No handler available for string data")
                else:
                    raise ValueError(f"Cannot determine handler for data type: {type(data)}")
                return handler.present_file(data)

            case "info":
                handler = self.get_handler_for_path(path)
                return handler.get_file_info(cast("Path", path))
            case _:
                raise ValueError(f"Invalid operation: {operation}")

    def read(self, file_path: Path | None = None, **kwargs) -> Any:
        """Read a file using the appropriate handler.

        Args:
            file_path: Path to read (uses stored path if None)
            **kwargs: Additional arguments for read_file

        Returns:
            File contents
        """
        return self.handle_file("read", file_path, **kwargs)

    def write(self, data: dict | str, file_path: Path | None = None, **kwargs) -> None:
        """Write to a file using the appropriate handler.

        Args:
            data: Data to write
            file_path: Path to write to (uses stored path if None)
            **kwargs: Additional arguments for write_file
        """
        return self.handle_file("write", file_path, data, **kwargs)

    def present(self, data: dict | str, file_path: Path | None = None) -> str:
        """Present data using the appropriate handler.

        Args:
            data: Data to present
            file_path: Optional path to determine format (uses stored path if None)

        Returns:
            String representation of the data
        """
        return self.handle_file("present", file_path, data)

    def get_info(self, file_path: Path | None = None) -> dict[str, Any]:
        """Get information about a file.

        Args:
            file_path: Path to get info for (uses stored path if None)

        Returns:
            Dictionary with file information
        """
        return self.handle_file("info", file_path)

    def convert(self, source_path: Path, target_path: Path, **kwargs) -> None:
        """Convert a file from one format to another.

        Args:
            source_path: Path to the source file
            target_path: Path to the target file
            **kwargs: Additional arguments for read_file and write_file
        """
        source_handler = self.get_handler_for_path(source_path)
        data = source_handler.read_file(source_path, **kwargs)

        target_handler = self.get_handler_for_path(target_path)
        target_handler.write_file(target_path, data, **kwargs)


_default_factory = FileHandlerFactory()


def get_handler_for_file(file_path: Path) -> FileHandler:
    """Get a handler for the given file path.

    Args:
        file_path: Path to the file

    Returns:
        Appropriate FileHandler instance
    """
    return _default_factory.get_handler_for_path(file_path)


def read_file(file_path: Path, **kwargs) -> Any:
    """Read a file using the appropriate handler.

    Args:
        file_path: Path to the file
        **kwargs: Additional arguments for read_file

    Returns:
        File contents
    """
    return _default_factory.read(file_path, **kwargs)


def write_file(file_path: Path, data: Any, **kwargs) -> None:
    """Write to a file using the appropriate handler.

    Args:
        file_path: Path to the file
        data: Data to write
        **kwargs: Additional arguments for write_file
    """
    return _default_factory.write(data, file_path, **kwargs)


def convert_file(source_path: Path, target_path: Path, **kwargs) -> None:
    """Convert a file from one format to another.

    Args:
        source_path: Path to the source file
        target_path: Path to the target file
        **kwargs: Additional arguments for read_file and write_file
    """
    return _default_factory.convert(source_path, target_path, **kwargs)
