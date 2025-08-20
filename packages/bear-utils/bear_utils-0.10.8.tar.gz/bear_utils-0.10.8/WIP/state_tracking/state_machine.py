"""State Machine Base Class with a mapping of states and an initial state."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from bear_utils.extras import Counter
from bear_utils.extras.state_tracking._common import StateTransitionError, get_original, is_auto
from bear_utils.extras.state_tracking.state import State


class StateMachine:
    """A base class for state machines, providing a mapping of states and an initial state."""

    def __init__(self) -> None:
        """Initialize the StateMachine."""
        self.state_map: dict[str, State] = self._process_state_map(self.__class__.__dict__)
        self._current_state: State = self.initial_state

    @staticmethod
    def _process_state_map(dict_items: dict) -> dict[str, State]:
        """Process the state map to ensure all states are properly initialized."""
        processed_map: dict[str, State] = {}
        _counter: Counter = Counter(0)
        raw_states: dict[str, State] = {
            k: v for k, v in dict_items.items() if isinstance(v, State) and not k.startswith("_")
        }
        for state_name, state in raw_states.items():
            if _counter == 0:
                state.initial = True
            if is_auto(state.id):
                local_value: int = get_original(state.id)
                if local_value > _counter:
                    state.id = local_value
                    _counter.set(local_value).increment()
                elif local_value == 0:
                    state.id = _counter.get(increment_after=True)
            elif not is_auto(state.id) and isinstance(state.id, int):
                if state.id > _counter:
                    _counter.set(state.id).increment()
                elif state.id == 0:
                    state.id = _counter.get(increment_after=True)
            processed_map[state_name.lower()] = state
        return processed_map

    @cached_property
    def first_state(self) -> State:
        """Get the first state of the state machine, value is only set once."""
        if len(self.state_map) == 0:
            raise ValueError("State machine has no states defined.")
        return next(iter(self.state_map.values()))

    @cached_property
    def initial_state(self) -> State:
        """Get the initial state of the state machine, value is only set once."""
        if len(self.state_map) == 0:
            raise ValueError("State machine has no states defined.")

        state: State | None = (
            (state for state in self.state_map.values() if state.initial).__next__()
            if self.state_map
            else self.first_state
        )
        if state is None:
            state = next(iter(self.state_map.values()))
        return state

    @property
    def current_state(self) -> State:
        """Get the current state of the state machine."""
        return self._current_state

    def has(self, state: State | Any) -> bool:
        """Check if the state machine has a specific state."""
        state = self._get(state)
        if state is None:
            return False
        return bool(isinstance(state, State))

    def _get(self, state: State | str | int, default: Any = None) -> State:
        """Get a state by its name or value."""
        try:
            if isinstance(state, State):
                return state
            if isinstance(state, str):
                return self._get_by_name(state)
            if isinstance(state, int):
                return self._get_by_value(state)
        except (ValueError, TypeError):
            return default

    def _get_by_name(self, name: str) -> State:
        """Get a state by its name."""
        name_get: State | None = self.state_map.get(name)
        if name_get is None:
            raise ValueError(f"State '{name_get}' not found in the state machine.")
        return name_get

    def _get_by_value(self, value: int) -> State:
        """Get a state by its integer value."""
        value_get: State | None = next((s for s in self.state_map.values() if s.id == value), None)
        if value_get is None:
            raise ValueError(f"State with value '{value}' not found in the state machine.")
        return value_get

    @current_state.setter
    def current_state(self, state: State | str | int | Any) -> None:
        """Set the current state of the state machine.

        Args:
            state (State | str | int): The new state to set. Can be a State instance, a string name, or an integer value.

        Raises:
            ValueError: If the state is not defined in the state machine.
            TypeError: If the provided state is not a valid type (State, str, or int).
            StateTransitionError: If the state is final or initial and cannot be set as the current state.
        """
        if self.current_state.final:
            raise StateTransitionError(f"Cannot change from final state {self.current_state}.")

        if not self.has(state):
            raise ValueError(f"State {state} is not defined in the state machine.")
        if not isinstance(state, (State | str | int)):
            raise TypeError(f"Invalid state: {state}")
        state = self._get(state)
        if state == self.current_state:
            return
        if state.initial:
            raise StateTransitionError(f"Cannot set initial state {state} as current state.")
        self._current_state = state

    def set_state(self, state: State | int | str) -> None:
        """Set the current state of the state machine."""
        if not self.has(state):
            raise ValueError(f"State {state} is not defined in the state machine.")
        self.current_state = state


__all__ = ["StateMachine"]
