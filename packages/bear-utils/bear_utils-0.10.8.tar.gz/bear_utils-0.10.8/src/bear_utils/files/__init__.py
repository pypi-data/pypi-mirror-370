"""A module for file handling utilities in Bear Utils."""

from .file_handlers import FileHandlerFactory
from .ignore_parser import IGNORE_PATTERNS

__all__ = ["IGNORE_PATTERNS", "FileHandlerFactory"]
