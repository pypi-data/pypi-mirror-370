from pathlib import Path

from bear_utils.cli import DEFAULT_SHELL


def test_default_shell_exists() -> None:
    assert Path(DEFAULT_SHELL).exists()
