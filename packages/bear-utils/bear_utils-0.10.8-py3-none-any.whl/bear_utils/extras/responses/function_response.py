"""Function Response Class for handling function call results."""

from __future__ import annotations

import json
from subprocess import CompletedProcess
from types import SimpleNamespace as Namespace
from typing import TYPE_CHECKING, Any, Literal, Self, overload

from pydantic import BaseModel, Field, field_validator

from bear_utils.extras._async_helpers import AsyncResponseModel, create_async_task, is_async_function

# Pydantic will yell if we put this into a TYPE_CHECKING block.
from bear_utils.logger_manager import AsyncLoggerProtocol, LoggerProtocol  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Callable


class FunctionResponse(BaseModel):
    """A class to represent the response of a function call, including success status, content, and error messages."""

    name: str = Field(default="", description="Name of the function that was called.")
    returncode: int = Field(default=0, description="Return code of the function, 0 for success, !=0 for failure.")
    extra: dict = Field(default_factory=dict, description="Additional metadata or information related to the response.")
    content: list[str] = Field(default=[], description="Content returned by the function call")
    error: list[str] = Field(default=[], description="Error message if the function call failed")
    sub_tasks: list[FunctionResponse] = Field(default_factory=list, description="List of sub-tasks.")
    number_of_tasks: int = Field(default=0, description="Number of tasks processed in this response.")
    logger: LoggerProtocol | AsyncLoggerProtocol | None = Field(
        default=None, description="Logger instance for logging messages."
    )
    attrs: Namespace = Field(default_factory=Namespace, description="Storing additional attributes dynamically.")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def _has_attr(self, key: str) -> bool:
        """Check if the attribute exists in the attrs Namespace."""
        return hasattr(self.attrs, key)

    def _get_attr(self, key: str, default: Any = None) -> Any:
        """Get the attribute from the attrs Namespace, returning default if not found."""
        if self._has_attr(key):
            return getattr(self.attrs, key, default)
        return default

    def _get_attrs(self) -> dict[str, Any]:
        """Get all attributes from the attrs Namespace as a dictionary."""
        return {k: getattr(self.attrs, k, None) for k in self.attrs.__dict__ if not k.startswith("_")}

    def __getattr__(self, key: str, default: Any = None) -> Any:
        if key in FunctionResponse.model_fields:
            raise AttributeError(f"This should never be called, {key} is a model field.")
        return self._get_attr(key, default)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in FunctionResponse.model_fields:
            object.__setattr__(self, key, value)
            return
        setattr(self.attrs, key, value)

    def __repr__(self) -> str:
        """Return a string representation of Response."""
        parts: list[str] = []

        def add(k: str, v: Any, _bool: bool = True, fmt_func: Callable | None = None) -> None:
            if _bool:
                formatted_value: str = fmt_func(v) if fmt_func else repr(v)
                parts.append(f"{k}={formatted_value}")

        add("name", self.name, bool(self.name))
        add("content", ", ".join(self.content), bool(self.content))

        # error state depends on returncode or error
        add("error", ", ".join(self.error), self.error_state)
        add("success", self.success, _bool=True)
        add("returncode", self.returncode, self.error_state)
        add("number_of_tasks", self.number_of_tasks, self.error_state)
        add("extra", self.extra, bool(self.extra), json.dumps)
        attrs = self._get_attrs()
        for attr in attrs:
            add(attr, attrs[attr])
        return f"Response({', '.join(parts)})"

    def __str__(self) -> str:
        """Return a string representation of Response."""
        return self.__repr__()

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | Any) -> str:
        """Ensure name is a string, lowercased, and without spaces."""
        if value is None:
            return ""
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception as e:
                raise TypeError(f"Name must be a string, got {type(value).__name__}.") from e
        return value.lower().replace(" ", "_")

    @field_validator("returncode")
    @classmethod
    def validate_returncode(cls, value: int) -> int:
        """Ensure returncode is an integer above or equal to zero."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Return code must be a non-negative integer.")
        return value

    @field_validator("extra", mode="before")
    @classmethod
    def validate_extra(cls, value: dict | Any) -> dict:
        """Ensure extra is always a dictionary."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("Extra must be a dictionary.")
        return value

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: str | list[str] | Any) -> list[str]:
        """Ensure content is always a list of strings."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise TypeError("Content must be a list of strings.")
            return value
        raise TypeError("Content must be a string or a list of strings.")

    @field_validator("error", mode="before")
    @classmethod
    def validate_error(cls, value: str | list[str] | Any) -> list[str]:
        """Ensure error is always a list of strings."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise TypeError("Error must be a list of strings.")
            return value
        raise TypeError("Error must be a string or a list of strings.")

    @classmethod
    def from_process(cls, process: CompletedProcess[str], **kwargs) -> Self:
        """Create a FunctionResponse from a CompletedProcess object."""
        returncode: int = process.returncode if process.returncode is not None else 0
        content: str = process.stdout.strip() if process.stdout else ""
        error: str = process.stderr.strip() if process.stderr else ""

        if returncode == 0 and not content and error:  # Some processes return empty stdout on success
            error, content = content, error
        return cls().add(returncode=returncode, content=content, error=error, **kwargs)

    @property
    def error_state(self) -> bool:
        """Check if the returncode or error field indicates an error state."""
        return self.returncode != 0 or bool(self.error)

    @property
    def success(self) -> bool:
        """Check if the response indicates success."""
        return self.returncode == 0 and not bool(self.error)

    def sub_task(
        self,
        name: str = "",
        content: str | list[str] = "",
        error: str | list[str] = "",
        extra: dict[str, Any] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
    ) -> Self:
        """Add a sub-task response to the FunctionResponse."""
        func_response: FunctionResponse = FunctionResponse(name=name, logger=self.logger).add(
            content=content,
            error=error,
            returncode=returncode or self.returncode,
            log_output=log_output,
            extra=extra,
        )
        self.add(content=func_response)
        self.sub_tasks.append(func_response)
        return self

    def successful(
        self,
        content: str | list[str] | CompletedProcess | FunctionResponse,
        error: str | list[str] = "",
        returncode: int | None = None,
        log_output: bool = False,
        **kwargs,
    ) -> Self:
        """Set the response to a success state with optional content."""
        return_code: int = returncode if returncode is not None else 0
        self.add(content=content, error=error, returncode=return_code, log_output=log_output, **kwargs)
        return self

    def fail(
        self,
        content: list[str] | str | CompletedProcess = "",
        error: str | list[str] = "",
        returncode: int | None = None,
        log_output: bool = False,
        **kwargs,
    ) -> Self:
        """Set the response to a failure state with an error message."""
        return_code: int = returncode if returncode is not None else 1
        self.add(content=content, error=error, returncode=return_code, log_output=log_output, **kwargs)
        return self

    def _add_item(self, item: str, target_list: list[str]) -> None:
        """Append an item to the target list if not empty."""
        target_list.append(item) if item != "" else None

    def _add_to_list(self, items: str | list[str], target_list: list[str], name: str | None = None) -> None:
        """Append items to the target list with optional name prefix."""
        try:
            if isinstance(items, list):
                for item in items:
                    self._add_item(f"{name}: {item}" if name else item, target_list)
            elif isinstance(items, str):
                self._add_item(f"{name}: {items}" if name else items, target_list)
        except Exception as e:
            raise ValueError(f"Failed to add items: {e!s}") from e

    def _add_content(self, content: str | list[str], name: str | None = None) -> None:
        """Add content to the FunctionResponse content list."""
        return self._add_to_list(items=content, target_list=self.content, name=name)

    def _add_error(self, error: str | list[str], name: str | None = None) -> None:
        """Add error messages to the FunctionResponse error list."""
        return self._add_to_list(items=error, target_list=self.error, name=name)

    def _handle_function_response(self, func_response: FunctionResponse) -> None:
        """Handle a FunctionResponse object and update the current response."""
        if func_response.extra:
            self.extra.update(func_response.extra)
        self._add_content(func_response.content, name=func_response.name)
        self._add_error(func_response.error, name=func_response.name)

    def _handle_completed_process(self, result: CompletedProcess[str]) -> None:
        """Handle a CompletedProcess object and update the FunctionResponse."""
        self._add_content(result.stdout.strip())
        self._add_error(result.stderr.strip())
        self.returncode = result.returncode

    def _handle_content(self, content: list[str] | str | FunctionResponse | CompletedProcess | Any) -> None:
        """Handle different types of content and update the FunctionResponse."""
        if isinstance(content, FunctionResponse):
            self._handle_function_response(func_response=content)
        elif isinstance(content, CompletedProcess):
            self._handle_completed_process(result=content)
        elif isinstance(content, (str | list)):
            self._add_to_list(content, self.content)
        else:
            return
        self.number_of_tasks += 1

    @overload
    def add(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None = None,
        error: str | list[str] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
        extra: dict[str, Any] | None = None,
        *,
        to_dict: Literal[True],
    ) -> dict[str, Any]: ...

    @overload
    def add(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None = None,
        error: str | list[str] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
        extra: dict[str, Any] | None = None,
        *,
        to_dict: Literal[False] = False,
    ) -> Self: ...

    def add(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None = None,
        error: str | list[str] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
        extra: dict[str, Any] | None = None,
        *,
        to_dict: bool = False,
    ) -> Self | dict[str, Any]:
        """Append additional content to the existing content."""
        try:
            if content is not None:
                self._handle_content(content=content)
            if error is not None and isinstance(error, (str | list)):
                self._add_to_list(error, target_list=self.error)
            if isinstance(returncode, int):
                self.returncode = returncode
            if isinstance(extra, dict):
                self.extra.update(extra)
            if log_output and self.logger and (content or error):
                self._log_handling(content=content, error=error, logger=self.logger)
        except Exception as e:
            raise ValueError(f"Failed to add content: {e!s}") from e
        return self.done(to_dict=True) if to_dict else self

    def _log_handling(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None,
        error: str | list[str] | None,
        logger: LoggerProtocol | AsyncLoggerProtocol,
    ) -> None:
        """Log the content and error messages if they exist."""

        async def loop_logging(messages: list[str], func: Callable) -> None:
            for msg in messages:
                if msg == "":
                    continue
                if is_async_function(func):
                    await func(f"{msg}")
                else:
                    func(f"{msg}")

        async def _log_messages(
            content: str | list[str], error: str | list[str], info_func: Callable, error_func: Callable
        ) -> None:
            if isinstance(content, str):
                content = [content]
            if isinstance(error, str):
                error = [error]

            await loop_logging(messages=content, func=info_func)
            await loop_logging(messages=error, func=error_func)

        if isinstance(content, (FunctionResponse | CompletedProcess | None)):
            content = []
        if not isinstance(error, (list | str)):
            error = []
        if not content and not error:
            return
        res: AsyncResponseModel = create_async_task(
            _log_messages,
            content=content,
            error=error,
            info_func=logger.info,
            error_func=logger.error,
        )
        res.conditional_run()

    @overload
    def done(
        self,
        to_dict: Literal[True],
        suppress: list[str] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    def done(
        self,
        to_dict: Literal[False],
        suppress: list[str] | None = None,
        include: list[str] | None = None,
    ) -> Self: ...

    def done(
        self,
        to_dict: bool = False,
        suppress: list[str] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any] | Self:
        """Convert the FunctionResponse to a dictionary or return the instance itself.

        Args:
            to_dict (bool): If True, return a dictionary representation.
            If False, return the FunctionResponse instance.
            suppress (list[str] | None): List of keys to suppress in the output dictionary.
            include (list[str] | None): List of keys to include in the output dictionary.

        Returns:
            dict[str, Any] | Self: The dictionary representation or the FunctionResponse instance.
        """
        if not to_dict:
            return self

        if suppress is None:
            suppress = []

        if include is None:
            include = []

        result: dict[str, Any] = {}

        def add(k: str, v: Any, _bool: bool = True) -> None:
            if k not in suppress and _bool:
                result[k] = v

        def dict_include(_bool: bool = True) -> dict[str, Any]:
            result.update(self.extra)
            for k in include:
                if hasattr(self.attrs, k) and _bool:
                    result[k] = getattr(self.attrs, k)
            return result

        add("name", self.name, bool(self.name))
        add("content", self.content, bool(self.content))
        add("success", self.success, _bool=True)
        # depends on the error state
        add("error", self.error, self.error_state)
        add("returncode", self.returncode, self.error_state)
        add("number_of_tasks", self.number_of_tasks, self.error_state)

        return dict_include()


def success(
    content: str | list[str] | CompletedProcess[str] | FunctionResponse,
    error: str = "",
    log_output: bool = False,
    **kwargs,
) -> FunctionResponse:
    """Create a successful FunctionResponse."""
    res = FunctionResponse()
    return res.successful(content, error, 0, log_output, **kwargs)


def fail(
    content: str | list[str] | CompletedProcess[str] = "",
    error: str | list[str] = "",
    returncode: int | None = None,
    log_output: bool = False,
    **kwargs,
) -> FunctionResponse:
    """Create a failed FunctionResponse."""
    res = FunctionResponse()
    return res.fail(content, error, returncode, log_output, **kwargs)


if __name__ == "__main__":
    # For testing purposes, you can run this module directly.

    response = FunctionResponse(name="test_function")
    response.add(content=["This is a test content."], error=["No errors."], returncode=1, extra={"smelly": "value"})
    response.poop = "farts"
    print(response.done(to_dict=True))
