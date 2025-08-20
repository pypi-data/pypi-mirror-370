from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable


class ResponseParser[T_Response](ABC):
    """Abstract base class for response parsers."""

    def __init__(self) -> None:
        self.response_transformers: dict[str, Callable] = {}

    @abstractmethod
    async def parse(self, raw_response: dict) -> T_Response:
        """Parse the raw response into the desired format."""

    @abstractmethod
    def get_default_response(self) -> T_Response:
        """Return a default response structure."""


class StandardHeaders(BaseModel):
    """Standard headers for AI requests."""

    content_type: str = Field(
        "application/json", description="Content type of the request", serialization_alias="Content-Type"
    )
    authorization: str | None = Field(
        None, description="Authorization token if required", serialization_alias="Authorization"
    )
