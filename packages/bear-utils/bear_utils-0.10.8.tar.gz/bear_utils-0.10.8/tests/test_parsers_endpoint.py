import json
import pytest
import httpx

from bear_utils.ai.ai_helpers._config import AIEndpointConfig
from bear_utils.ai.ai_helpers._parsers import JSONResponseParser, ModularAIEndpoint, TypedResponseParser
from bear_utils.constants import HTTPStatusCode
from .conftest import DummyLogger


def make_client(result: httpx.Response | Exception):
    class MockClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self) -> "MockClient":  # type: ignore[override]
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

        async def post(self, *args, **kwargs) -> httpx.Response:
            if isinstance(result, Exception):
                raise result
            return result

    return MockClient


@pytest.mark.asyncio
async def test_json_response_parser(logger: DummyLogger) -> None:
    parser = JSONResponseParser(required_fields=["foo"], response_transformers={"foo": str.upper})
    good = {"output": json.dumps({"foo": "bar"})}
    parsed = await parser.parse(good, logger)
    assert parsed == {"foo": "BAR"}

    missing = {"output": json.dumps({"bar": 1})}
    parsed_missing = await parser.parse(missing, logger)
    assert parsed_missing == {"error": "Failed to parse response"}

    bad_json = {"output": "not json"}
    parsed_bad = await parser.parse(bad_json, logger)
    assert parsed_bad == {"error": "Failed to parse response"}


@pytest.mark.asyncio
async def test_typed_response_parser(logger: DummyLogger) -> None:
    default = {"foo": "", "bar": 0}
    parser = TypedResponseParser(default_response=default, response_transformers={"foo": str.title})
    good = {"output": json.dumps({"foo": "hello", "bar": 1})}
    parsed = await parser.parse(good, logger)
    assert parsed == {"foo": "Hello", "bar": 1}

    missing = {"output": json.dumps({"foo": "only"})}
    parsed_missing = await parser.parse(missing, logger)
    assert parsed_missing == default


@pytest.fixture
def endpoint(logger: DummyLogger) -> ModularAIEndpoint[dict[str, str]]:
    config = AIEndpointConfig(
        project_name="test",
        bearer_token="token",
        prompt="prompt",
        testing_url="https://example.com/test",
        production_url="https://example.com/prod",
        append_json_suffix=False,
    )
    parser = JSONResponseParser(response_transformers={"foo": str.upper})
    return ModularAIEndpoint(config, logger, parser)


@pytest.mark.asyncio
async def test_modular_endpoint_success(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[dict[str, str]]
) -> None:
    response = httpx.Response(
        HTTPStatusCode.SERVER_OK,
        json={"output": json.dumps({"foo": "bar"})},
        request=httpx.Request("POST", endpoint.config.url),
    )
    monkeypatch.setattr("bear_utils.ai.ai_helpers._parsers.AsyncClient", make_client(response))
    result = await endpoint.send_message("hi")
    assert result == {"foo": "BAR"}


@pytest.mark.asyncio
async def test_modular_endpoint_http_error(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[dict[str, str]]
) -> None:
    response = httpx.Response(
        HTTPStatusCode.SERVER_ERROR,
        text="fail",
        request=httpx.Request("POST", endpoint.config.url),
    )
    monkeypatch.setattr("bear_utils.ai.ai_helpers._parsers.AsyncClient", make_client(response))
    result = await endpoint.send_message("hi")
    assert result == {"error": "Failed to parse response"}


@pytest.mark.asyncio
async def test_modular_endpoint_exception(
    monkeypatch: pytest.MonkeyPatch, endpoint: ModularAIEndpoint[dict[str, str]]
) -> None:
    monkeypatch.setattr(
        "bear_utils.ai.ai_helpers._parsers.AsyncClient",
        make_client(RuntimeError("boom")),
    )
    result = await endpoint.send_message("hi")
    assert result == {"error": "Failed to parse response"}
