from collections.abc import Callable
import re
from typing import Any, Literal, Self


class Zapper[T]:
    """A class to remove specified symbols from a source string."""

    def __init__(
        self,
        str_input: str | tuple[str, ...],
        src: str,
        replace: str = "",
        expected_unpack: int = 0,
        sep: str = ".",
        atomic: bool = False,
        unpack_strict: bool = True,
        regex: bool = False,
        filter_start: bool = False,  # Will filter out any separators at the start of the string
        filter_end: bool = False,  # Will filter out any separators at the end of the string
        sorting: Literal["length", "order"] = "length",
        func: Callable[[str], T] = str,
    ) -> None:
        """Initialize the Zapper with symbols, source string, and optional parameters."""
        self.src: str = src
        self.replace: str = replace
        self.expected_unpack: int = expected_unpack
        self.sep: str = sep
        self.func: Callable[[str], T] = func
        self.atomic: bool = atomic
        self.unpack_strict: bool = unpack_strict
        self.regex_enabled: bool = regex
        self.filter_start: bool = filter_start
        self.filter_end: bool = filter_end
        self.sorting: Literal["length", "order"] = sorting
        self.input: list[str] = self._process_input(str_input)
        self.dst: str = ""
        self.result: tuple[Any, ...] | None = None

    @staticmethod
    def _get_chars(str_input: str) -> list[str]:
        """Get a list of characters from the input string."""
        return [char for char in str_input if char if char != ""]

    @staticmethod
    def _get_strs(str_input: tuple[str, ...]) -> list[str]:
        """Get a list of strings from the input tuple."""
        return [item for item in str_input if item if item != ""]

    @staticmethod
    def _de_dupe(strings: list[str], atomic: bool, sorting: Literal["length", "order"]) -> list[str]:
        """Remove duplicates from the input list based on the sorting method."""
        if atomic and sorting == "length":
            return sorted(set(strings), key=lambda x: len(x), reverse=True)
        seen = set()
        ordered_result = []
        for item in strings:
            if item not in seen:
                seen.add(item)
                ordered_result.append(item)
        return ordered_result

    def _process_input(self, str_input: str | tuple[str, ...]) -> list[str]:
        """Process the input symbols based on whether they are multi-input or single."""
        is_tuple = isinstance(str_input, tuple)
        is_string = isinstance(str_input, str)
        if str_input == "":
            return []
        strings_to_replace = []
        if is_string and not self.atomic:
            # If a single string is passed, treat each char as a string to replace
            chars: list[str] = self._get_chars(str_input)
            strings_to_replace.extend(chars)
        elif is_string and self.atomic:
            # If a single string is passed and self.atomic is True, treat it as a single string to replace
            strings_to_replace.append(str_input)
        elif is_tuple and not self.atomic:
            # If a tuple is passed while atomic is false, treat each char as a string to replace
            for item in str_input:
                chars = self._get_chars(item)
                strings_to_replace.extend(chars)
        elif is_tuple and self.atomic:
            # If a tuple is passed and atomic is True, treat each string as a thing to replace
            strings: list[str] = self._get_strs(str_input)
            strings_to_replace.extend(strings)
        return self._de_dupe(strings_to_replace, self.atomic, self.sorting)

    # region Zap Related

    @staticmethod
    def _re_sub(src: str, pattern: str, replacement: str) -> str:
        """Perform a regex substitution on the source string."""
        return re.sub(pattern, replacement, src)

    @property
    def value(self) -> str:
        """Return the modified source string."""
        return self.dst

    def _zap(self) -> str:
        """Remove specified symbols from the source string."""
        temp_str: str = self.src
        for to_replace in self.input:
            if self.regex_enabled:
                temp_str = self._re_sub(temp_str, to_replace, self.replace)
            else:
                temp_str = temp_str.replace(to_replace, self.replace)
        if self.filter_start and temp_str.startswith(self.sep):
            temp_str = temp_str[len(self.sep) :]
        if self.filter_end and temp_str.endswith(self.sep):
            temp_str = temp_str[: -len(self.sep)]
        if self.unpack_strict:
            temp_str = temp_str.replace(self.sep * 2, self.sep)  # Remove double separators
        self.dst = temp_str
        return self.dst

    def zap(self) -> Self:
        """Remove specified symbols from the source string."""
        self.dst = self._zap()
        return self

    # endregion
    # region Zap Get Related

    def _zap_get(self) -> tuple[str, ...]:
        """Remove specified symbols and return a tuple of unpacked values."""
        result: list[str] = self._zap().split(self.sep)[: self.expected_unpack]
        if self.unpack_strict and len(result) != self.expected_unpack:
            raise ValueError(f"Expected {self.expected_unpack} items, got {len(result)}: {result}")
        self.result = tuple(result)
        return self.result

    def zap_get(self) -> Self:
        """Remove specified symbols and return a tuple of unpacked values."""
        self.result = self._zap_get()
        if self.unpack_strict and len(self.result) != self.expected_unpack:
            raise ValueError(f"Expected {self.expected_unpack} items, got {len(self.result)}: {self.result}")
        return self

    @property
    def unpacked(self) -> tuple[Any, ...]:
        """Return the unpacked values as a tuple."""
        if isinstance(self.result, tuple):
            return self.result
        raise ValueError("Result is not unpacked yet. Call zap_get() first.")

    # endregion
    # region Zap As Related

    def _zap_as(self) -> tuple[T, ...]:
        """Convert the result in self.result to the specified type."""
        temp_list: list[Any] = []
        if self.result is None:
            raise ValueError("No result to convert. Call zap_get() first.")
        for item in self.result:
            temp_list.append(self.func(item))
        self.result = tuple(temp_list)
        return self.result

    def zap_as(self) -> Self:
        """Convert the result in self.result to the specified type."""
        if not self.result:
            raise ValueError("No result to convert. Call zap_get() first.")
        self._zap_as()
        return self

    # endregion


def zap_multi(
    *sym: str,
    src: str,
    replace: str = "",
    atomic: bool = True,
) -> str:
    """Remove specified symbols from the source string.

    Args:
        *sym: A variable number of strings containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).

    Returns:
        str: The modified source string with specified symbols removed.

    Example:
        >>> zap_multi("!?*", "Hello!? World! *", "")
        'Hello World '
        >>> zap_multi("!?*", "Hello!? World! *", "-")
        'Hello- World- -'
    """
    zapper: Zapper[str] = Zapper(sym, src, replace, atomic=atomic)
    return zapper.zap().value


def zap(sym: str, src: str, replace: str = "") -> str:
    """Remove specified symbols from the source string.

    Args:
        sym (str): A string containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).

    Returns:
        str: The modified source string with specified symbols removed.

    Example:
        >>> zap("!?*", "Hello!? World! *", "")
        'Hello World '
        >>> zap("!?*", "Hello!? World! *", "-")
        'Hello- World- -'
    """
    zapper: Zapper[str] = Zapper(sym, src, replace, unpack_strict=False)
    return zapper.zap().value


def zap_get_multi(
    *sym: str,
    src: str,
    unpack_val: int,
    replace: str = "",
    sep: str = ".",
) -> tuple[str, ...]:
    """Remove specified symbols from the source string and return a tuple of unpacked values.

    Args:
        *sym: A variable number of strings containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        unpack_val (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").

    Returns:
        tuple[str, ...]: A tuple of unpacked values from the modified source string.

    Raises:
        ValueError: If the number of items in the result does not match unpack_val.
    """
    zapper: Zapper[str] = Zapper(sym, src, replace, expected_unpack=unpack_val, sep=sep, unpack_strict=True)
    try:
        return zapper.zap_get().unpacked
    except Exception as e:
        raise ValueError(f"Error unpacking values: {e}") from e


def zap_get(sym: str, src: str, unpack_val: int, replace: str = "", sep: str = ".") -> tuple[str, ...]:
    """Remove specified symbols from the source string and return a tuple of unpacked values.

    Args:
        sym (str): A string containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        unpack_val (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").

    Returns:
        tuple[str, ...]: A tuple of unpacked values from the modified source string.

    Raises:
        ValueError: If the number of items in the result does not match unpack_val.
    """
    zapper: Zapper[str] = Zapper(sym, src, replace, expected_unpack=unpack_val, sep=sep, unpack_strict=True)
    try:
        return zapper.zap_get().unpacked
    except Exception as e:
        raise ValueError(f"Error unpacking values: {e}") from e


def zap_take(sym: str, src: str, unpack_val: int, replace: str = "", sep: str = ".") -> tuple[str, ...]:
    """Remove specified symbols from the source string and return a tuple of unpacked values.

    This function is similar to zap_get but does not raise an error if the number of items does not match unpack_val.
    Instead, it returns as many items as possible.

    Args:
        sym (str): A string containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        unpack_val (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").

    Returns:
        tuple[str, ...]: A tuple of unpacked values from the modified source string.
    """
    zapper: Zapper[str] = Zapper(sym, src, replace, expected_unpack=unpack_val, sep=sep, unpack_strict=False)
    return zapper.zap_get().unpacked


def zap_as_multi[T](
    *sym,
    src: str,
    unpack_val: int,
    replace: str = "",
    sep: str | None = None,
    func: Callable[[str], T] = str,
    strict: bool = True,
    regex: bool = False,
    atomic: bool = True,
    filter_start: bool = False,  # Will filter out any separators at the start of the string
    filter_end: bool = False,  # Will filter out any separators at the end of the string
    sorting: Literal["length", "order"] = "length",  # Will sort the input symbols by length in descending order
) -> tuple[T, ...]:
    """Remove specified symbols from the source string, unpack the result, and convert it to a specified type.

    Args:
        *sym: A variable number of strings containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        unpack_val (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").
        func (type, optional): The type of the result to cast/convert to (default is str).

    Returns:
        Zapper: An instance of the Zapper class configured with the provided parameters.
    """
    if sep is None:
        sep = replace

    zapper: Zapper[T] = Zapper(
        str_input=sym,
        src=src,
        replace=replace,
        expected_unpack=unpack_val,
        sep=sep,
        func=func,
        unpack_strict=strict,
        regex=regex,
        atomic=atomic,
        filter_start=filter_start,
        filter_end=filter_end,
        sorting=sorting,
    )
    try:
        return zapper.zap_get().zap_as().unpacked
    except Exception as e:
        raise ValueError(f"Error converting values: {e}") from e


def zap_as[T](
    sym: str,
    src: str,
    unpack_val: int,
    replace: str = "",
    sep: str | None = None,
    func: Callable[[str], T] = str,
    strict: bool = True,
    regex: bool = False,
    filter_start: bool = False,  # Will filter out any separators at the start of the string
    filter_end: bool = False,  # Will filter out any separators at the end of the string
    atomic: bool = False,  # If True, treat the input symbols as a single string to replace
    sorting: Literal["length", "order"] = "length",  # length ordering or by the order of input
) -> tuple[T, ...]:
    """Remove specified symbols from the source string, unpack the result, and convert it to a specified type.

    Args:
        sym (str): A string containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        unpack_val (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").
        func (type, optional): The type of the result to cast/convert to (default is str).

    Returns:
        Zapper: An instance of the Zapper class configured with the provided parameters.
    """
    if sep is None:
        sep = replace

    zapper: Zapper[T] = Zapper(
        str_input=sym,
        src=src,
        replace=replace,
        expected_unpack=unpack_val,
        sep=sep,
        func=func,
        unpack_strict=strict,
        regex=regex,
        filter_start=filter_start,
        filter_end=filter_end,
        atomic=atomic,
        sorting=sorting,
    )
    try:
        return zapper.zap_get().zap_as().unpacked
    except Exception as e:
        raise ValueError(f"Error converting values: {e}") from e


__all__ = [
    "Zapper",
    "zap",
    "zap_as",
    "zap_as_multi",
    "zap_get",
    "zap_get_multi",
    "zap_multi",
    "zap_take",
]

if __name__ == "__main__":
    # # Example usage
    # result = zap_as_multi("()", "(", ")", src="(a)(b)(c)", unpack_val=3, replace="|", atomic=False)
    # print(result)
    # assert result == ("a", "b", "c")

    version_string = "v1.2.3-beta+build"
    result = zap_as_multi(
        "v", "-", "+", src=version_string, unpack_val=3, replace=".", func=int, strict=True, filter_start=True
    )
    print(result)
