"""A module for state tracking in state machines."""

from ._common import MAGIC_FLAG, Auto, StateTransitionError, get_original, is_auto
from ._decorator import auto_value_decorator
from .state import State
from .state_machine import StateMachine

__all__ = [
    "MAGIC_FLAG",
    "Auto",
    "State",
    "StateMachine",
    "StateTransitionError",
    "auto_value_decorator",
    "get_original",
    "is_auto",
]
