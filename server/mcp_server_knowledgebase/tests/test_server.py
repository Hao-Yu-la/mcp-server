import asyncio
import logging
import os

import pytest
from mcp.server.mcpserver.exceptions import ToolError

os.environ.setdefault("VIKING_API_KEY", "test-api-key")

from mcp_server_knowledgebase import server


def test_call_kb_returns_response_data(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_request(path: str, params: dict[str, object]) -> dict[str, object]:
        assert path == "/test/path"
        assert params == {"project": "test-project"}
        return {"code": 0, "message": "success", "data": {"value": 1}}

    monkeypatch.setattr(server, "_request_knowledgebase", fake_request)

    result = asyncio.run(
        server._call_kb("/test/path", {"project": "test-project"}, "test_tool")
    )

    assert result == {"value": 1}


@pytest.mark.parametrize(
    ("response", "expected_message"),
    [
        ({"code": 1001, "message": "permission denied", "data": None}, "permission denied"),
        (
            {"code": 0, "message": "success", "data": None},
            "get_collection returned no data",
        ),
    ],
)
def test_call_kb_reports_failures_with_the_calling_tool_name(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    response: dict[str, object],
    expected_message: str,
) -> None:
    async def fake_request(path: str, params: dict[str, object]) -> dict[str, object]:
        return response

    monkeypatch.setattr(server, "_request_knowledgebase", fake_request)

    with caplog.at_level(logging.ERROR, logger=server.__name__):
        with pytest.raises(ToolError, match=expected_message):
            asyncio.run(server._call_kb("/test/path", {}, "get_collection"))

    assert "Error in get_collection:" in caplog.text


def test_call_kb_wraps_request_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_request(path: str, params: dict[str, object]) -> dict[str, object]:
        raise TimeoutError("upstream timed out")

    monkeypatch.setattr(server, "_request_knowledgebase", fake_request)

    with pytest.raises(ToolError, match="upstream timed out"):
        asyncio.run(server._call_kb("/test/path", {}, "list_docs"))


def test_call_kb_preserves_tool_errors_from_the_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_request(path: str, params: dict[str, object]) -> dict[str, object]:
        raise ToolError("request rejected")

    monkeypatch.setattr(server, "_request_knowledgebase", fake_request)

    with pytest.raises(ToolError, match="request rejected"):
        asyncio.run(server._call_kb("/test/path", {}, "get_doc"))


def test_get_collection_identifies_itself_to_the_shared_call_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_call(
        path: str, params: dict[str, object], tool_name: str
    ) -> dict[str, object]:
        assert path == server.get_collections_path
        assert params == {"name": "product-docs", "project": server.config.project}
        assert tool_name == "get_collection"
        return {
            "collection_name": "product-docs",
            "description": "Product documentation",
            "pipeline_list": [{"index_list": [{"status": 1}]}],
        }

    monkeypatch.setattr(server, "_call_kb", fake_call)

    result = asyncio.run(server.get_collection("product-docs"))

    assert result.collection_name == "product-docs"
    assert result.status == 1
