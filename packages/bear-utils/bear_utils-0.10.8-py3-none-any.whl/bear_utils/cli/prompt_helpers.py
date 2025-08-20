"""Prompt Helpers Module for user input handling."""

from typing import Any, TextIO, overload

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

from bear_utils.constants import STDOUT
from bear_utils.constants._exceptions import UserCancelledError
from bear_utils.constants._lazy_typing import OptBool, OptFloat, OptInt, OptStr
from bear_utils.logger_manager.loggers._console import LogConsole


def _parse_exit(value: str) -> bool:
    """Parse a string into a boolean indicating if the user wants to exit."""
    lower_value: str = value.lower().strip()
    return lower_value in ("exit", "quit", "q")


def _parse_bool(value: str) -> bool:
    """Parse a string into a boolean value."""
    lower_value: str = value.lower().strip()
    if lower_value in ("true", "t", "yes", "y", "1"):
        return True
    if lower_value in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"Cannot convert '{value}' to boolean")


def _convert_value(value: str, target_type: type) -> str | int | float | bool:
    """Convert a string value to the target type."""
    if target_type is str:
        return value
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    if target_type is bool:
        return _parse_bool(value)
    raise ValueError(f"Unsupported type: {target_type}")


class PromptHelpers:
    """A collection of helper methods for prompting user input."""

    _console: LogConsole[TextIO] = LogConsole(file=STDOUT)

    @overload
    @classmethod
    def ask_question(cls, question: str, expected_type: type[bool], default: OptBool = None) -> bool: ...

    @overload
    @classmethod
    def ask_question(cls, question: str, expected_type: type[int], default: OptInt = None) -> int: ...

    @overload
    @classmethod
    def ask_question(cls, question: str, expected_type: type[float], default: OptFloat = None) -> float: ...

    @overload
    @classmethod
    def ask_question(cls, question: str, expected_type: type[str], default: OptStr = None) -> str: ...

    @classmethod
    def ask_question(cls, question: str, expected_type: type, default: Any = None) -> Any:
        """Ask a question and return the answer, ensuring the entered type is correct.

        This function will keep asking until it gets a valid response or the user cancels with Ctrl+C.
        If the user cancels, a UserCancelledError is raised.

        Args:
            question: The prompt question to display
            expected_type: The expected type class (int, float, str, bool)
            default: Default value if no input is provided

        Returns:
            The user's response in the expected type

        Raises:
            UserCancelledError: If the user cancels input with Ctrl+C
            ValueError: If an unsupported type is specified
        """
        try:
            while True:
                cls._console.print(question)
                response: str = prompt("> ").strip()

                if not response:
                    if default is not None:
                        return default
                    cls._console.error("Input required. Please enter a value.")
                    continue
                try:
                    result: str | int | float | bool = _convert_value(response, expected_type)
                    cls._console.verbose(f"{expected_type.__name__} detected")
                    return result
                except ValueError as e:
                    cls._console.error(f"Invalid input: {e}. Please enter a valid {expected_type.__name__}.")

        except KeyboardInterrupt:
            raise UserCancelledError("User cancelled input") from None

    @classmethod
    def ask_yes_no(cls, question: str, default: bool | None = None) -> bool | None:
        """Ask a yes or no question and return the answer.

        Args:
            question: The prompt question to display
            default: Default value if no input is provided

        Returns:
            True for yes, False for no, or None if user exits
        """
        while True:
            try:
                response: str = prompt(f"{question}\n> ").strip().lower()
                if not response:
                    if default is not None:
                        return default
                    cls._console.print("Please enter 'yes', 'no', or 'exit'.")
                    continue
                if _parse_exit(response):
                    return None
                try:
                    return _parse_bool(response)
                except ValueError:
                    cls._console.print("Invalid input. Please enter 'yes', 'no', or 'exit'.", style="red")
            except KeyboardInterrupt:
                cls._console.print("KeyboardInterrupt: Exiting the prompt.", style="yellow")
                return None

    @classmethod
    def restricted_prompt(
        cls, question: str, valid_options: list[str], exit_command: str = "exit", case_sensitive: bool = False
    ) -> str | None:
        """Continuously prompt the user until they provide a valid response or exit.

        Args:
            question: The prompt question to display
            valid_options: List of valid responses
            exit_command: Command to exit the prompt (default: "exit")
            case_sensitive: Whether options are case-sensitive (default: False)

        Returns:
            The user's response or None if they chose to exit
        """
        completer_options: list[str] = [*valid_options, exit_command]
        completer = WordCompleter(completer_options)

        comparison_options: list[str] = valid_options if case_sensitive else [opt.lower() for opt in valid_options]
        comparison_exit: str = exit_command if case_sensitive else exit_command.lower()

        class OptionValidator(Validator):
            def validate(self, document: Any) -> None:
                """Validate the user's input against the valid options."""
                text: Any = document.text if case_sensitive else document.text.lower()
                if text and text != comparison_exit and text not in comparison_options:
                    raise ValidationError(
                        message=f"Invalid option. Choose from: {', '.join(valid_options)} or '{exit_command}'",
                        cursor_position=len(document.text),
                    )

        try:
            while True:
                response: str = prompt(
                    f"{question}\n> ",
                    completer=completer,
                    validator=OptionValidator(),
                    complete_while_typing=True,
                ).strip()
                comparison_response: str = response if case_sensitive else response.lower()
                if not response:
                    cls._console.print("Please enter a valid option or 'exit'.", style="red")
                    continue
                if comparison_response == comparison_exit:
                    return None
                if comparison_response in comparison_options:
                    if not case_sensitive:
                        idx: int = comparison_options.index(comparison_response)
                        return valid_options[idx]
                    return response
        except KeyboardInterrupt:
            cls._console.print("KeyboardInterrupt: Exiting the prompt.", style="yellow")
            return None


def ask_question(
    question: str,
    expected_type: type,
    default: Any = None,
) -> Any:
    """Ask a question and return the answer, ensuring the entered type is correct."""
    return PromptHelpers.ask_question(question, expected_type, default)


def ask_yes_no(question: str, default: bool | None = None) -> bool | None:
    """Ask a yes or no question and return the answer."""
    return PromptHelpers.ask_yes_no(question, default)


def restricted_prompt(
    question: str,
    valid_options: list[str],
    exit_command: str = "exit",
    case_sensitive: bool = False,
) -> str | None:
    """Continuously prompt the user until they provide a valid response or exit."""
    return PromptHelpers.restricted_prompt(question, valid_options, exit_command, case_sensitive)
