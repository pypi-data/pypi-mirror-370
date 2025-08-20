"""A module for managing event callbacks using weak references."""

from asyncio import Task, gather, iscoroutinefunction
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from types import MethodType
from typing import Any
from weakref import WeakMethod, ref

_callbacks: dict[str, set[Callable[..., Any]]] = defaultdict(set)


def _make_cleanup_callback(name: str) -> Callable[[Any], None]:
    def callback(weak_ref: Any) -> None:
        _callbacks[name].discard(weak_ref)
        if not _callbacks[name]:
            del _callbacks[name]

    return callback


def set_callback(name: str, callback: Callable[..., Any]) -> None:
    """Register a callback for the given event name."""
    if isinstance(callback, MethodType):
        _callbacks[name].add(WeakMethod(callback, _make_cleanup_callback(name)))
    else:
        _callbacks[name].add(ref(callback, _make_cleanup_callback(name)))


def remove_callback(name: str, callback: Callable[..., Any]) -> bool:
    """Remove a specific callback. Returns True if found and removed."""
    target = WeakMethod(callback) if isinstance(callback, MethodType) else ref(callback)
    try:
        _callbacks[name].remove(target)
        return True
    except KeyError:
        return False


def clear_callbacks(name: str) -> None:
    """Remove all callbacks for the given event name."""
    _callbacks[name].clear()


def clear_all() -> None:
    """Remove all registered callbacks."""
    _callbacks.clear()


async def event_dispatch(name: str, *args, **kwargs) -> None:
    """Fire-and-forget event dispatch."""
    if name not in _callbacks:
        return

    tasks: list[Task | Any] = []
    for callback_ref in _callbacks[name]:
        callback = callback_ref()
        if callback is None:
            continue

        if iscoroutinefunction(callback):
            tasks.append(callback(*args, **kwargs))
        else:
            tasks.append(_sync_wrapper(callback, *args, **kwargs))

    if tasks:
        await gather(*tasks, return_exceptions=True)


async def event_call(name: str, *args, **kwargs) -> tuple[list[Any], list[BaseException]]:
    """Call event callbacks and return results and exceptions."""
    successes: list[Any] = []
    failures: list[BaseException] = []

    if name not in _callbacks:
        return successes, failures

    tasks: list[Task | Any] = []
    for callback_ref in _callbacks[name]:
        callback = callback_ref()
        if callback is None:
            continue

        if iscoroutinefunction(callback):
            tasks.append(callback(*args, **kwargs))
        else:
            tasks.append(_sync_wrapper(callback, *args, **kwargs))

    if not tasks:
        return successes, failures

    results: list[Any | BaseException] = await gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, BaseException):
            failures.append(result)
        else:
            successes.append(result)

    return successes, failures


async def _sync_wrapper(func: Callable[..., Any], *args, **kwargs) -> Any:
    return func(*args, **kwargs)


def event_handler(event_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a function as an event handler."""

    def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(callback)
        def wrapper(*args, **kwargs) -> Any:
            return callback(*args, **kwargs)

        set_callback(event_name, wrapper)
        return wrapper

    return decorator
