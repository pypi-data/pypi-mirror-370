"""A set of utilities for managing the system clipboard with platform-specific commands."""

import asyncio
from asyncio.subprocess import PIPE
from collections import deque
import shutil
from typing import TYPE_CHECKING

from bear_utils.cli.shell._base_command import BaseShellCommand as ShellCommand
from bear_utils.cli.shell._base_shell import AsyncShellSession
from bear_utils.extras.platform_utils import OS, get_platform

if TYPE_CHECKING:
    from subprocess import CompletedProcess


def shutil_which(cmd: str) -> None | str:
    """A wrapper around shutil.which to return None if the command is not found."""
    return shutil.which(cmd)


class ClipboardManager:
    """A class to manage clipboard operations such as copying, pasting, and clearing.

    This class provides methods to interact with the system clipboard.
    """

    def __init__(self, maxlen: int = 10) -> None:
        """Initialize the ClipboardManager with a maximum history length."""
        self.clipboard_history: deque[str] = deque(maxlen=maxlen)
        self.shell = AsyncShellSession(env={"LANG": "en_US.UTF-8"}, verbose=False)
        self._copy: ShellCommand[str]
        self._paste: ShellCommand[str]

        platform: OS = get_platform()
        match platform:
            case OS.DARWIN:
                self._copy = ShellCommand.adhoc(name="pbcopy")
                self._paste = ShellCommand.adhoc(name="pbpaste")
            case OS.LINUX:
                if shutil_which(cmd="wl-copy") and shutil_which(cmd="wl-paste"):
                    self._copy = ShellCommand.adhoc(name="wl-copy")
                    self._paste = ShellCommand.adhoc(name="wl-paste")
                elif shutil_which(cmd="xclip"):
                    self._copy = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard")
                    self._paste = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard").value("-o")
                else:
                    raise RuntimeError("No clipboard command found on Linux")
            case OS.WINDOWS:
                self._copy = ShellCommand.adhoc(name="clip")
                self._paste = ShellCommand.adhoc(name="powershell").sub("Get-Clipboard")
            case _:
                raise RuntimeError(f"Unsupported platform: {platform}")

    def _copy_cmd(self) -> ShellCommand[str]:
        """Get the copy command based on the platform."""
        return self._copy

    def _paste_cmd(self) -> ShellCommand[str]:
        """Get the paste command based on the platform."""
        return self._paste

    def get_history(self) -> deque:
        """Get the clipboard history.

        Returns:
            deque: The history of clipboard entries.
        """
        return self.clipboard_history

    async def copy(self, output: str) -> int:
        """A function that copies the output to the clipboard.

        Args:
            output (str): The output to copy to the clipboard.

        Returns:
            int: The return code of the command.
        """
        await self.shell.run(cmd=self._copy, stdin=PIPE)
        result: CompletedProcess[str] = await self.shell.communicate(stdin=output)
        if result.returncode == 0:
            self.clipboard_history.append(output)  # Only append to history if the copy was successful
        return result.returncode

    async def paste(self) -> str:
        """Paste the output from the clipboard.

        Returns:
            str: The content of the clipboard.

        Raises:
            RuntimeError: If the paste command fails.
        """
        try:
            await self.shell.run(cmd=self._paste)
            result: CompletedProcess[str] = await self.shell.communicate()
        except Exception as e:
            raise RuntimeError(f"Error pasting from clipboard: {e}") from e
        if result.returncode != 0:
            raise RuntimeError(f"{self._paste.cmd} failed with return code {result.returncode}")
        return result.stdout

    async def clear(self) -> int:
        """A function that clears the clipboard.

        Returns:
            int: The return code of the command.
        """
        return await self.copy(output="")


def copy_to_clipboard(output: str) -> int:
    """Copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.copy(output))


async def copy_to_clipboard_async(output: str) -> int:
    """Asynchronously copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.copy(output=output)


def paste_from_clipboard() -> str:
    """Paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.paste())


async def paste_from_clipboard_async() -> str:
    """Asynchronously paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.paste()


def clear_clipboard() -> int:
    """Clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(clipboard_manager.clear())


async def clear_clipboard_async() -> int:
    """Asynchronously clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.clear()
