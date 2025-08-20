from collections.abc import Callable
from inspect import isclass
from typing import Any

from bear_utils.extras import Counter
from bear_utils.extras.state_tracking._common import is_auto
from bear_utils.extras.state_tracking.state import State


def _counter_work(cls: type, state: State, state_name: str, _counter: Counter) -> None:
    if is_auto(state.id):
        local_value: int = int(state.id)
        if local_value > _counter:
            state.id = local_value
            _counter.set(local_value).increment()
        elif local_value == 0:
            state.id = _counter.get()
            _counter.increment()
    elif not is_auto(state.id) and isinstance(state.id, int):
        if state.id > _counter:
            _counter.set(value=state.id).increment()
        elif state.id == 0:
            state.id = _counter.get()
            _counter.increment()

    setattr(cls, state_name, state)


def auto_value_decorator() -> Callable[[type], Any]:
    """Decorator to find capitalized strings in a class and convert them to State instances with auto-incremented values."""

    def decorator(cls: type) -> Any:
        """Decorator function to convert class attributes to State instances with auto-incremented values."""
        if not isclass(cls):
            raise TypeError("auto_value_decorator can only be applied to classes.")

        _counter = Counter(0)
        states: dict[str, State] = {
            name: attr for name, attr in cls.__dict__.items() if not name.startswith("_") and name.isupper()
        }

        for state_name, state in states.items():
            if isinstance(state, str):
                setattr(cls, state_name, State(name=state))
            current_state: State = getattr(cls, state_name)
            _counter_work(cls, current_state, state_name, _counter)

        return cls

    return decorator
