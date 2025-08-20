"""A set of helper caching utilities for bear_utils."""

import functools
from pathlib import Path
from typing import Any

from diskcache import Cache

DEFAULT_CACHE_DIR = Path("~/.cache/app_cache").expanduser()


class CacheWrapper:
    """A simple wrapper around diskcache.Cache to provide a consistent interface.

    This class allows for easy caching of function results with a specified directory,
    size limit, and default timeout.
    """

    def __init__(
        self,
        directory: str | None = None,
        size_limit: int | None = None,
        default_timeout: int | None = None,
        **kwargs,
    ) -> None:
        """Initialize the CacheWrapper with a specified directory, size limit, and default timeout.

        Args:
            directory (str, optional): Directory path for the cache. Defaults to ~/.cache/app_cache.
            size_limit (int, optional): Maximum size of the cache in bytes. Defaults to 1_000_000_000.
            default_timeout (int, optional): Default timeout for cache entries in seconds. Defaults to None.
        """
        self.cache = Cache(directory or DEFAULT_CACHE_DIR, size_limit=size_limit or 1_000_000_000, **kwargs)
        self.default_timeout = default_timeout

    def get(self, key: Any, default: Any = None) -> Any:
        """Get a value from the cache."""
        return self.cache.get(key, default=default)

    def set(self, key: Any, value: Any, expire: int | None = None) -> None:
        """Set a value in the cache."""
        if expire is None:
            expire = self.default_timeout
        self.cache.set(key, value, expire=expire)


def cache_factory(
    directory: str | None = None,
    size_limit: int | None = None,
    default_timeout: int | None = None,
    **kwargs: Any,
) -> Any:
    """Creates and configures a cache decorator factory.

    Args:
        directory (str, optional): Cache directory path. Defaults to ~/.cache/app_cache.
        size_limit (int, optional): Maximum size in bytes. Defaults to None.
        default_timeout (int, optional): Default timeout in seconds. Defaults to None.
        **kwargs: Additional arguments to pass to the Cache constructor.

    Returns:
        function: A decorator function that can be used to cache function results.

    Examples:
        # Create a custom cache
        my_cache = cache_factory(directory='/tmp/mycache', default_timeout=3600)

        # Use as a simple decorator
        @my_cache
        def expensive_function(x, y):
            return x + y

        # Use with custom parameters
        @my_cache(expire=60)
        def another_function(x, y):
            return x * y
    """
    local_directory: Path | None = Path(directory).expanduser() if directory else None
    if local_directory is None:
        local_directory = Path(DEFAULT_CACHE_DIR)
    local_directory.mkdir(parents=True, exist_ok=True)

    if size_limit is None:
        size_limit = 1_000_000_000

    cache_instance = Cache(local_directory, size_limit=size_limit, **kwargs)

    def decorator(func: object | None = None, *, expire: int | None = default_timeout, key: Any = None) -> object:
        """Decorator that caches function results.

        Args:
            func: The function to cache (when used as @cache)
            expire (int, optional): Expiration time in seconds.
            key (callable, optional): Custom key function.

        Returns:
            callable: Decorated function or decorator
        """

        def actual_decorator(fn: Any) -> object:
            """Actual decorator that wraps the function with caching logic."""

            def wrapper(*args, **kwargs) -> tuple[Any, ...]:
                if key is not None:
                    cache_key = key(fn, *args, **kwargs)
                else:
                    cache_key = (fn.__module__, fn.__qualname__, args, frozenset(kwargs.items()))

                result = cache_instance.get(cache_key, default=None)
                if result is not None:
                    return result

                # If not in cache, compute and store
                result: Any = fn(*args, **kwargs)
                cache_instance.set(cache_key, result, expire=expire)
                return result

            # Preserve function metadata
            return functools.update_wrapper(wrapper, fn)

        # Handle both @cache and @cache(expire=300) styles
        if func is None:
            return actual_decorator
        return actual_decorator(func)

    return decorator


cache = cache_factory()

__all__ = ["CacheWrapper", "cache", "cache_factory"]
