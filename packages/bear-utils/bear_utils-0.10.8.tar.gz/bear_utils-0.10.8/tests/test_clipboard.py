from unittest.mock import patch

import pytest

from bear_utils.extras import ClipboardManager, shutil_which, OS


def mock_which_func(cmd: str) -> None | str:
    """Mock function to simulate shutil.which behavior for testing."""
    if cmd == "wl-copy":
        return "/usr/bin/wl-copy"
    if cmd == "wl-paste":
        return "/usr/bin/wl-paste"
    if cmd == "xclip":
        return "/usr/bin/xclip"
    return None


@patch("bear_utils.extras.clipboard.shutil.which", side_effect=mock_which_func)
def test_shutil_which(mock_which) -> None:
    """Test the shutil_which function."""
    assert shutil_which("wl-copy") == "/usr/bin/wl-copy"
    assert shutil_which("wl-paste") == "/usr/bin/wl-paste"
    assert shutil_which("xclip") == "/usr/bin/xclip"
    assert shutil_which("nonexistent-command") is None


@patch("bear_utils.extras.clipboard.get_platform", return_value=OS.DARWIN)
def test_macos_commands(mock_platform) -> None:
    manager = ClipboardManager()
    assert manager._copy.command_name == "pbcopy"
    assert manager._paste.command_name == "pbpaste"


@patch("bear_utils.extras.clipboard.shutil.which", side_effect=mock_which_func)
@patch("bear_utils.extras.clipboard.get_platform", return_value=OS.LINUX)
def test_linux_wayland(mock_platform, mock_which) -> None:
    manager = ClipboardManager()
    assert manager._copy.command_name == "wl-copy"
    assert manager._paste.command_name == "wl-paste"


@patch("bear_utils.extras.clipboard.shutil_which", return_value=None)
@patch("bear_utils.extras.clipboard.get_platform", return_value=OS.LINUX)
def test_linux_no_clipboard(mock_platform, mock_which) -> None:
    with pytest.raises(RuntimeError):
        ClipboardManager()


@patch("bear_utils.extras.clipboard.get_platform", return_value=OS.WINDOWS)
def test_windows_commands(mock_platform) -> None:
    manager = ClipboardManager()
    assert manager._copy.cmd == "clip"
    assert manager._paste.cmd == "powershell Get-Clipboard"
