"""Tests for prompt_helpers module."""

import signal
from typing import Any, NoReturn
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from bear_utils.cli.prompt_helpers import (
    _convert_value,
    _parse_bool,
    ask_question,
    ask_yes_no,
    restricted_prompt,
    PromptHelpers,
)
from bear_utils.constants._exceptions import UserCancelledError


class TestParseBool:
    """Test the _parse_bool helper function."""

    def setup_method(self):
        """Set up timeout for each test method."""
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(5)

    def teardown_method(self) -> None:
        """Clean up timeout after each test."""
        signal.alarm(0)

    def _timeout_handler(self, signum: Any, frame: Any) -> NoReturn:
        """Handle timeout by raising an exception."""
        print(signum, frame)
        raise TimeoutError("Test timed out - likely infinite loop in _parse_bool")

    def test_parse_bool_true_values(self):
        """Test that various true values are parsed correctly."""
        true_values = ["true", "t", "yes", "y", "1", "TRUE", "True", "YES", "Y"]
        for value in true_values:
            assert _parse_bool(value) is True

    def test_parse_bool_false_values(self):
        """Test that various false values are parsed correctly."""
        false_values: list[str] = ["false", "f", "no", "n", "0", "FALSE", "False", "NO", "N"]
        for value in false_values:
            assert _parse_bool(value) is False

    def test_parse_bool_invalid_values(self):
        """Test that invalid values raise ValueError."""
        invalid_values = ["maybe", "yep", "nah", "2", "true-ish", ""]
        for value in invalid_values:
            with pytest.raises(ValueError, match="Cannot convert"):
                _parse_bool(value)

    def test_parse_bool_whitespace_handling(self):
        """Test that whitespace is properly stripped."""
        assert _parse_bool("  true  ") is True
        assert _parse_bool("\tfalse\n") is False


class TestConvertValue:
    """Test the _convert_value helper function."""

    def test_convert_string(self):
        """Test string conversion (passthrough)."""
        assert _convert_value("hello", str) == "hello"
        assert _convert_value("123", str) == "123"

    def test_convert_int(self):
        """Test integer conversion."""
        assert _convert_value("42", int) == 42
        assert _convert_value("-17", int) == -17
        assert _convert_value("0", int) == 0

    def test_convert_int_invalid(self):
        """Test invalid integer conversion."""
        with pytest.raises(ValueError):
            _convert_value("not_a_number", int)
        with pytest.raises(ValueError):
            _convert_value("12.5", int)

    def test_convert_float(self):
        """Test float conversion."""
        assert _convert_value("3.14", float) == 3.14
        assert _convert_value("-2.5", float) == -2.5
        assert _convert_value("42", float) == 42.0

    def test_convert_float_invalid(self):
        """Test invalid float conversion."""
        with pytest.raises(ValueError):
            _convert_value("not_a_number", float)

    def test_convert_bool(self):
        """Test boolean conversion using _parse_bool."""
        assert _convert_value("true", bool) is True
        assert _convert_value("false", bool) is False

    def test_convert_unsupported_type(self):
        """Test that unsupported types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported type"):
            _convert_value("test", list)


class TestAskQuestion:
    """Test the ask_question function."""

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_string_input(self, mock_console, mock_prompt):
        mock_console.print = MagicMock()
        mock_console.verbose = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "hello world"

        result = ask_question("Enter text: ", str)

        assert result == "hello world"
        mock_console.print.assert_called_with("Enter text: ")
        mock_console.verbose.assert_called_with("str detected")

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_int_input(self, mock_console, mock_prompt):
        """Test asking for integer input."""
        mock_console.verbose = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "42"

        result = ask_question("Enter number: ", int)

        assert result == 42
        assert isinstance(result, int)
        mock_console.verbose.assert_called_with("int detected")

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_bool_input(self, mock_console, mock_prompt):
        """Test asking for boolean input."""
        mock_console.verbose = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "yes"

        result = ask_question("Continue? ", bool)

        assert result is True
        mock_console.verbose.assert_called_with("bool detected")

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_with_default(self, mock_console, mock_prompt):
        """Test asking with default value."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = ""

        result = ask_question("Enter name: ", str, "default_name")

        assert result == "default_name"

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_invalid_then_valid(self, mock_console, mock_prompt):
        """Test handling invalid input followed by valid input."""
        mock_console.error = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = ["not_a_number", "42"]

        result = ask_question("Enter number: ", int)

        assert result == 42
        mock_console.error.assert_called_with(
            "Invalid input: invalid literal for int() with base 10: 'not_a_number'. Please enter a valid int."
        )

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_keyboard_interrupt(self, mock_console, mock_prompt):
        """Test handling KeyboardInterrupt."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = KeyboardInterrupt()

        with pytest.raises(UserCancelledError):
            ask_question("Enter text: ", str)


class TestAskYesNo:
    """Test the ask_yes_no function."""

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_yes_responses(self, mock_console, mock_prompt):
        """Test various yes responses."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)

        yes_responses: list[str] = ["yes", "y", "YES", "Y"]
        for response in yes_responses:
            mock_prompt.return_value = response
            result: bool | None = ask_yes_no("Continue? ")
            assert result is True

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_no_responses(self, mock_console, mock_prompt):
        """Test various no responses."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)

        no_responses = ["no", "n", "NO", "N"]
        for response in no_responses:
            mock_prompt.return_value = response
            result = ask_yes_no("Continue? ")
            assert result is False

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_exit_responses(self, mock_console, mock_prompt):
        """Test exit responses."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)

        exit_responses = ["exit", "quit", "EXIT", "QUIT"]
        for response in exit_responses:
            mock_prompt.return_value = response
            result = ask_yes_no("Continue? ")
            assert result is None

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_with_default(self, mock_console, mock_prompt):
        """Test with default value."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = ""

        result: bool | None = ask_yes_no("Continue? ", default=True)
        assert result is True

        result = ask_yes_no("Continue? ", default=False)
        assert result is False

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_invalid_then_valid(self, mock_console, mock_prompt):
        """Test invalid input followed by valid input."""
        mock_console.print = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = ["maybe", "yes"]

        result: bool | None = ask_yes_no("Continue? ")

        assert result is True
        mock_console.print.assert_called_with("Invalid input. Please enter 'yes', 'no', or 'exit'.", style="red")

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_yes_no_keyboard_interrupt(self, mock_console, mock_prompt):
        """Test KeyboardInterrupt handling."""
        mock_console.print = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = KeyboardInterrupt()

        result: bool | None = ask_yes_no("Continue? ")

        assert result is None
        mock_console.print.assert_called_with("KeyboardInterrupt: Exiting the prompt.", style="yellow")


class TestRestrictedPrompt:
    """Test the restricted_prompt function."""

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_valid_option(self, mock_console, mock_prompt):
        """Test selecting a valid option."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "option1"

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"])

        assert result == "option1"

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_exit(self, mock_console, mock_prompt):
        """Test exiting with exit command."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "exit"

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"])

        assert result is None

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_case_insensitive(self, mock_console, mock_prompt):
        """Test case insensitive matching (default)."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "OPTION1"

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"])

        assert result == "option1"

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_case_sensitive(self, mock_console, mock_prompt):
        """Test case sensitive matching."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = ["OPTION1", "option1"]  # First fails, second succeeds

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"], case_sensitive=True)

        assert result == "option1"

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_custom_exit(self, mock_console, mock_prompt):
        """Test custom exit command."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "quit"

        result = restricted_prompt("Choose: ", ["option1", "option2"], exit_command="quit")

        assert result is None

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_empty_input(self, mock_console, mock_prompt):
        """Test handling empty input."""
        mock_console.print = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = ["", "option1"]

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"])

        assert result == "option1"
        mock_console.print.assert_called_with("Please enter a valid option or 'exit'.", style="red")

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_restricted_prompt_keyboard_interrupt(self, mock_console, mock_prompt):
        """Test KeyboardInterrupt handling."""
        mock_console.print = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.side_effect = KeyboardInterrupt()

        result: str | None = restricted_prompt("Choose: ", ["option1", "option2"])

        assert result is None
        mock_console.print.assert_called_with("KeyboardInterrupt: Exiting the prompt.", style="yellow")


class TestPromptHelpersIntegration:
    """Integration tests for prompt helpers."""

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_ask_question_whitespace_handling(self, mock_console, mock_prompt):
        """Test that whitespace is properly handled in all cases."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)
        mock_prompt.return_value = "  hello world  "

        result = ask_question("Enter text: ", str)

        assert result == "hello world"  # Should be stripped

    @patch("bear_utils.cli.prompt_helpers.prompt")
    @patch.object(PromptHelpers, "_console")
    def test_bool_question_comprehensive(self, mock_console, mock_prompt):
        """Test comprehensive boolean input handling."""
        mock_console = MagicMock()
        mock_sub = MagicMock()
        mock_console.return_value = (mock_console, mock_sub)

        # Test all acceptable boolean values
        test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("y", True),
            ("n", False),
            ("1", True),
            ("0", False),
            ("T", True),
            ("F", False),
            ("YES", True),
            ("NO", False),
        ]

        for input_val, expected in test_cases:
            mock_prompt.return_value = input_val
            result = ask_question("Boolean question: ", bool)
            assert result is expected
