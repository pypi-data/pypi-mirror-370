import asyncio
from asyncio import AbstractEventLoop, Task
from collections.abc import Callable
from contextlib import suppress
import inspect
import time
from typing import Any

from pydantic import BaseModel, Field


def is_async_function(func: Callable) -> bool:
    """Check if a function is asynchronous.

    Args:
        func (Callable): The function/method to check.

    Returns:
        bool: True if the function is asynchronous, False otherwise.
    """
    return inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func) or inspect.isasyncgen(func)


class AsyncResponseModel(BaseModel):
    """A model to handle asynchronous operations with a function and its arguments."""

    loop: AbstractEventLoop | None = Field(default=None, description="The event loop to run the function in.")
    task: Task | None = Field(default=None, description="The task created for the asynchronous function.")
    before_loop: bool = Field(default=False, description="If the function was called from a running loop.")
    result: Any = Field(default=None, description="The result of the completed task.")

    model_config = {"arbitrary_types_allowed": True}

    @property
    def done(self) -> bool:
        """Check if the task is completed."""
        return self.task is not None and self.task.done()

    def get_result(self) -> Any:
        """Get the result of the completed task."""
        if not self.task:
            raise ValueError("No task available")
        if not self.task.done():
            raise ValueError("Task not completed yet")
        if self.result is None:
            self.result = self.task.result()
        return self.result

    def get_conditional_result(self, timeout: float = 10.0) -> Any:
        if self.loop and self.task and not self.before_loop:
            self.loop.run_until_complete(self.task)
        start_time: float = time.monotonic()
        while not self.done:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError("Task timed out")
            time.sleep(0.1)
        return self.get_result()

    def conditional_run(self) -> None:
        """Run the event loop until the task is complete if not in a running loop."""
        if self.loop and self.task and not self.before_loop:
            self.loop.run_until_complete(self.task)


def in_async_loop() -> bool:
    """Check if the current context is already in an async loop.

    Returns:
        bool: True if an async loop is running, False otherwise.
    """
    loop: AbstractEventLoop | None = None
    with suppress(RuntimeError):
        loop = asyncio.get_running_loop()
    return loop.is_running() if loop else False


def gimmie_async_loop() -> AbstractEventLoop:
    """Get the current event loop, creating one if it doesn't exist."""
    if in_async_loop():
        return asyncio.get_event_loop()
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def create_async_task(
    func: Callable,
    *args,
    **kwargs,
) -> AsyncResponseModel:
    """Create an asyncio task for a given function."""
    before_loop: bool = in_async_loop()
    loop: AbstractEventLoop = gimmie_async_loop()
    task = loop.create_task(func(*args, **kwargs))
    return AsyncResponseModel(loop=loop, task=task, before_loop=before_loop)
