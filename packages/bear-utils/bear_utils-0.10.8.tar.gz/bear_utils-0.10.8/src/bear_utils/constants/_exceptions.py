"""Custom exceptions for the application."""


class UserCancelledError(Exception):
    """Exception raised when a user cancels an operation."""

    def __init__(self, message: str = "User cancelled the operation"):
        super().__init__(message)
