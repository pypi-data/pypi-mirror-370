"""Helper utilities for constructing AI endpoints with custom response parsing."""

from collections.abc import Callable

from ._common import PRODUCTION_MODE, TESTING_MODE, EnvironmentMode
from ._config import AIEndpointConfig
from ._parsers import (
    CommandResponseParser,
    JSONResponseParser,
    ModularAIEndpoint,
    PassthroughResponseParser,
    TypedResponseParser,
)
from ._types import ResponseParser


def create_endpoint[T_Response](
    config: AIEndpointConfig,
    response_parser: ResponseParser[T_Response],
    transformers: dict[str, Callable] | None = None,
    append_json: bool | None = None,
) -> ModularAIEndpoint[T_Response]:
    """Create a ModularAIEndpoint with the specified configuration and response parser."""
    if append_json is not None:
        config.append_json_suffix = append_json

    if transformers:
        response_parser.response_transformers.update(transformers)

    return ModularAIEndpoint(config=config, response_parser=response_parser)


__all__ = [
    "PRODUCTION_MODE",
    "TESTING_MODE",
    "AIEndpointConfig",
    "CommandResponseParser",
    "EnvironmentMode",
    "JSONResponseParser",
    "ModularAIEndpoint",
    "PassthroughResponseParser",
    "TypedResponseParser",
    "create_endpoint",
]
