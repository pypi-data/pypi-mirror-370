from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ActionHolder:
    """A class to hold the action and its arguments."""

    # text, shortcut, callback)
    text: str
    shortcut: str
    callback: Callable
