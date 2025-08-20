"""A simple bridge for augmenting Typer with alias support and command execution for interactive use."""

from collections.abc import Callable
import shlex
from typing import Any, TypedDict

from rich.console import Console
from singleton_base import SingletonBase
from typer import Context, Exit, Typer
from typer.models import CommandInfo

from bear_utils.logger_manager import AsyncLoggerProtocol, LoggerProtocol


class CommandMeta(TypedDict):
    """Metadata for a Typer command."""

    name: str
    help: str
    hidden: bool


def get_command_meta(command: CommandInfo) -> CommandMeta:
    """Extract metadata from a Typer command."""
    return {
        "name": command.name or (command.callback.__name__ if command.callback else "unknown"),
        "help": (command.callback.__doc__ if command.callback else None) or "No description available",
        "hidden": command.hidden,
    }


# TODO: Add support for usage statements for a more robust help system


class TyperBridge(SingletonBase):
    """Simple bridge for Typer command execution."""

    def __init__(
        self,
        typer_app: Typer,
        console: AsyncLoggerProtocol | LoggerProtocol | Console,
        is_primary: bool = False,
    ) -> None:
        """Initialize the TyperBridge with a Typer app instance.

        Args:
            typer_app (Typer): The Typer application instance to bridge
            console (AsyncLoggerProtocol | LoggerProtocol | Console): The console or logger to use for output, it will use a
                Console instance if not provided.
            is_primary (bool): Whether to use directly instead of using the typer decorator to define commands.
        """
        self.app: Typer = typer_app
        self.console: AsyncLoggerProtocol | LoggerProtocol | Console = console or Console()
        self.is_primary: bool = is_primary
        self.command_meta: dict[str, CommandMeta] = {}
        self.ignore_list: list[str] = []

    def define(
        self,
        *alias_names: str,
        name: str | None = None,
        ignore: bool = False,
        usage_text: str = "",
        **kwargs,
    ) -> Callable[..., Callable[..., Any]]:
        """Decorator to register a command with optional aliases and ignore flag."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            meta_name: str = func.__name__ if name is None else name
            if usage_text:
                if func.__doc__ is not None:
                    func.__doc__ += f" | Usage: {usage_text}"
                else:
                    func.__doc__ = f"Usage: {usage_text}"

            if self.is_primary:
                self.app.command(name=meta_name, **kwargs)(func)

            for alias in alias_names:
                self.app.command(name=alias, hidden=True)(func)
            if ignore:
                func._ignore = True  # type: ignore[assignment]
                self.ignore_list.append(func.__name__)
                for alias in alias_names:
                    self.ignore_list.append(alias)
            return func

        return decorator

    def callback(self, **kwargs) -> Callable[..., Callable[..., Any]]:
        """Decorator to register a callback function for the Typer app.

        This decorator checks if the invoked subcommand is in the ignore list
        and skips execution if it is. This is useful for ignoring certain commands
        that are registered but should be run differently or not at all.
        It should be used when Typer is NOT the primary command handler.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(ctx: Context) -> None:
                if ctx.invoked_subcommand and ctx.invoked_subcommand in self.ignore_list:
                    return None
                return func(ctx)

            self.app.callback(**kwargs)(wrapper)
            return wrapper

        return decorator

    def alias(self, *alias_names: str) -> Callable[..., Callable[..., Any]]:
        """Register aliases as hidden Typer commands."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._aliases = alias_names  # type: ignore[assignment]
            for alias in alias_names:
                self.app.command(name=alias, hidden=True)(func)
            return func

        return decorator

    def ignore(self) -> Callable[..., Callable[..., Any]]:
        """Decorator to set an internal attribute so other code can ignore this command."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            func._ignore = True  # type: ignore[assignment]
            self.ignore_list.append(func.__name__)
            if hasattr(func, "_aliases"):
                for alias in func._aliases:  # type: ignore[attr-defined]
                    self.ignore_list.append(alias)
            return func

        return decorator

    def ignore_callback(self) -> Callable[..., Callable[..., Any]]:
        """Decorator on the app.callback to inject a check for ignored commands.

        This should be used when Typer is the primary command handler else use
        the above callback decorator.
        """

        def decorator(func: Callable) -> Callable[..., None]:
            def wrapper(ctx: Context) -> None:
                if ctx.invoked_subcommand and ctx.invoked_subcommand in self.ignore_list:
                    return None
                return func(ctx)

            return wrapper

        return decorator

    def execute_command(self, command_string: str) -> bool:
        """Execute command via Typer. Return True if successful."""
        try:
            parts: list[str] = shlex.split(command_string.strip())
            if not parts:
                return False
            self.app(parts, standalone_mode=False)
            return True
        except Exit:
            return True
        except Exception as e:
            if isinstance(self.console, Console):
                self.console.print(f"[red]Error executing command: {e}[/red]")
            else:
                self.console.error(f"Error executing command: {e}", exc_info=True)
            return False

    def bootstrap_command_meta(self) -> None:
        """Bootstrap command metadata from the Typer app."""
        if not self.command_meta:
            for cmd in self.app.registered_commands:
                cmd_meta: CommandMeta = get_command_meta(command=cmd)
                self.command_meta[cmd_meta["name"]] = cmd_meta

    def get_all_command_info(self, show_hidden: bool = False) -> dict[str, CommandMeta]:
        """Get all command information from the Typer app."""
        if not self.command_meta:
            self.bootstrap_command_meta()
        if not show_hidden:
            return {name: meta for name, meta in self.command_meta.items() if not meta["hidden"]}
        return self.command_meta

    def get_command_info(self, command_name: str) -> CommandMeta | None:
        """Get metadata for a specific command."""
        if not self.command_meta:
            self.bootstrap_command_meta()
        return self.command_meta.get(command_name)
