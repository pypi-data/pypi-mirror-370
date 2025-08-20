import pytest
import asyncio
from svo_client.chunker_client import (
    ChunkerClient, 
    SVOServerError, 
    SVOJSONRPCError, 
    SVOHTTPError, 
    SVOConnectionError, 
    SVOTimeoutError
)
from typing import List
import aiohttp
import sys
import types
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter import SemanticChunk

def make_valid_chunk(**overrides):
    # Генерируем валидный словарь для SemanticChunk
    fields = SemanticChunk.model_fields
    base = {}
    for k in fields:
        if k == "uuid":
            base[k] = str(uuid.uuid4())
        elif k == "type":
            base[k] = "DocBlock"
        elif k == "text":
            base[k] = "Hello, "
        elif k == "body":
            base[k] = "Hello, "
        elif k == "summary":
            base[k] = "summary"
        elif k == "sha256":
            base[k] = "a" * 64
        elif k == "language":
            base[k] = "en"
        elif k == "created_at":
            base[k] = datetime.now(timezone.utc).isoformat()
        elif k == "status":
            base[k] = "new"
        elif k == "start":
            base[k] = 0
        elif k == "end":
            base[k] = 6
        elif k == "metrics":
            base[k] = {}
        elif k == "links":
            base[k] = []
        elif k == "tags":
            base[k] = []
        elif k == "embedding":
            base[k] = [1.0]
        elif k == "role":
            base[k] = "user"
        elif k == "project":
            base[k] = "proj"
        elif k == "task_id":
            base[k] = str(uuid.uuid4())
        elif k == "subtask_id":
            base[k] = str(uuid.uuid4())
        elif k == "unit_id":
            base[k] = str(uuid.uuid4())
        elif k == "source_id":
            base[k] = str(uuid.uuid4())
        elif k == "source_path":
            base[k] = "/path"
        elif k == "source_lines":
            base[k] = [1, 2]
        elif k == "ordinal":
            base[k] = 0
        elif k == "chunking_version":
            base[k] = "1.0"
        else:
            base[k] = None
    base.update(overrides)
    obj, err = SemanticChunk.validate_and_fill(base)
    assert err is None, f"Test data is not valid: {err}"
    return obj

@pytest.mark.asyncio
async def test_chunk_text_and_reconstruct(monkeypatch):
    fake_chunks = [
        make_valid_chunk(text="Hello, ", ordinal=0, embedding=[1.0], sha256="a"*64),
        make_valid_chunk(text="world!", ordinal=1, embedding=[2.0], sha256="b"*64)
    ]
    class FakeResponse:
        def __init__(self, data): self._data = data
        async def json(self): return {"result": {"chunks": self._data}}
        def raise_for_status(self): pass
    class FakeSession:
        def __init__(self): self.last_url = None; self.last_json = None
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse(fake_chunks)
                async def __aexit__(self_, exc_type, exc, tb): pass
            self.last_url = url; self.last_json = json
            return _Ctx()
        def get(self, url, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse({"openapi": "3.0.2"})
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    # chunk_text
    err = None
    svoserver_error = None
    try:
        chunks = await client.chunk_text("Hello, world!")
    except SVOServerError as e:
        svoserver_error = e
    except Exception as e:
        err = e
    assert err is None, f"Exception occurred: {err}"
    assert svoserver_error is None, f"SVOServerError occurred: {svoserver_error}"
    assert chunks is not None, f"chunks is None"
    assert isinstance(chunks, list)
    assert all(isinstance(c, SemanticChunk) for c in chunks)
    assert chunks[0].text == "Hello, "
    assert chunks[1].text == "world!"
    # Проверка обязательных полей
    assert hasattr(chunks[0], "text")
    assert hasattr(chunks[1], "text")
    # reconstruct_text
    text = client.reconstruct_text(chunks)
    assert text == "Hello, world!"

@pytest.mark.asyncio
async def test_get_openapi_schema(monkeypatch):
    class FakeResponse:
        async def json(self): return {"openapi": "3.0.2"}
        def raise_for_status(self): pass
    class FakeSession:
        def get(self, url, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    schema = await client.get_openapi_schema()
    assert schema["openapi"] == "3.0.2"

@pytest.mark.asyncio
async def test_get_help(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"commands": {"chunk": {}}}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    help_info = await client.get_help()
    assert "commands" in help_info["result"]

@pytest.mark.asyncio
async def test_health(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"success": True}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    health = await client.health()
    assert health["result"]["success"] is True

# Интеграционный тест (если сервер доступен)
@pytest.mark.asyncio
async def test_chunk_text_integration():
    try:
        async with ChunkerClient() as client:
            try:
                chunks = await client.chunk_text("Integration test.")
                assert isinstance(chunks, list)
                assert all(isinstance(c, SemanticChunk) for c in chunks)
                if chunks:
                    assert hasattr(chunks[0], "text")
            except SVOServerError as e:
                # Acceptable: server returned a chunking error in the chunk
                assert hasattr(e, "code")
                assert hasattr(e, "message")
                assert hasattr(e, "chunk_error")
    except aiohttp.ClientConnectorError:
        pytest.skip("Chunker server not available for integration test.")

def test_parse_chunk_validation_error(monkeypatch):
    # Подделываем validate_and_fill, чтобы всегда возвращать ошибку
    from chunk_metadata_adapter import SemanticChunk
    def fake_validate_and_fill(data):
        return None, {'error': 'Fake validation error', 'fields': {}}
    monkeypatch.setattr(SemanticChunk, "validate_and_fill", staticmethod(fake_validate_and_fill))
    from svo_client.chunker_client import ChunkerClient  # импорт после monkeypatch!
    client = ChunkerClient()
    invalid_chunk = {"uuid": "not-a-uuid", "type": "DocBlock", "text": "bad", "sha256": "bad", "language": "en", "start": 0, "end": 1, "body": "bad", "summary": "bad"}
    try:
        client.parse_chunk(invalid_chunk)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Fake validation error" in str(e)

@pytest.mark.asyncio
async def test_chunk_text_server_error(monkeypatch):
    # Мокаем ответ сервера с ошибкой в chunks
    error_chunk = {"error": {"code": "sha256_mismatch", "message": "SHA256 mismatch: original=..., chunks=..."}}
    class FakeResponse:
        async def json(self): return {"result": {"chunks": [error_chunk]}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOServerError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert err.code == "sha256_mismatch"
    assert "SHA256 mismatch" in err.message
    assert isinstance(err.chunk_error, dict)

@pytest.mark.asyncio
async def test_chunk_text_jsonrpc_error(monkeypatch):
    # Мокаем JSON-RPC ошибку на уровне response
    class FakeResponse:
        async def json(self): return {"error": {"code": -32602, "message": "Invalid params"}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOJSONRPCError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert err.code == -32602
    assert "Invalid params" in err.message

@pytest.mark.asyncio
async def test_get_help_jsonrpc_error(monkeypatch):
    # Мокаем JSON-RPC ошибку для get_help
    class FakeResponse:
        async def json(self): return {"error": {"code": -32601, "message": "Method not found"}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOJSONRPCError) as excinfo:
        await client.get_help()
    err = excinfo.value
    assert err.code == -32601
    assert "Method not found" in err.message

@pytest.mark.asyncio
async def test_health_jsonrpc_error(monkeypatch):
    # Мокаем JSON-RPC ошибку для health
    class FakeResponse:
        async def json(self): return {"error": {"code": -32603, "message": "Internal error"}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOJSONRPCError) as excinfo:
        await client.health()
    err = excinfo.value
    assert err.code == -32603
    assert "Internal error" in err.message

@pytest.mark.asyncio
async def test_chunk_text_empty_result(monkeypatch):
    # Тест для случая, когда result пустой или None
    class FakeResponse:
        async def json(self): return {"result": None}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOServerError) as exc_info:
        await client.chunk_text("test")
    assert exc_info.value.code == "empty_result"
    assert "Empty result from server" in exc_info.value.message

@pytest.mark.asyncio
async def test_chunk_text_http_error(monkeypatch):
    # Тест HTTP ошибки
    class FakeResponse:
        status = 500
        def raise_for_status(self): 
            raise aiohttp.ClientResponseError(
                request_info=None, 
                history=None, 
                status=500, 
                message="Internal Server Error"
            )
        async def text(self): return "Server error details"
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOHTTPError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert err.status_code == 500
    assert "Internal Server Error" in err.message
    assert "Server error details" in err.response_text

@pytest.mark.asyncio
async def test_chunk_text_invalid_json(monkeypatch):
    # Тест некорректного JSON
    import json
    class FakeResponse:
        status = 200
        def raise_for_status(self): pass
        async def json(self): 
            raise json.JSONDecodeError("Invalid JSON", "invalid", 0)
        async def text(self): return "invalid json response"
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOHTTPError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert err.status_code == 200
    assert "Invalid JSON response" in err.message
    assert "invalid json response" in err.response_text

@pytest.mark.asyncio
async def test_get_openapi_schema_http_error(monkeypatch):
    # Тест HTTP ошибки для get_openapi_schema
    class FakeResponse:
        status = 404
        def raise_for_status(self): 
            raise aiohttp.ClientResponseError(
                request_info=None, 
                history=None, 
                status=404, 
                message="Not Found"
            )
        async def text(self): return "OpenAPI schema not found"
    class FakeSession:
        def get(self, url, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOHTTPError) as excinfo:
        await client.get_openapi_schema()
    err = excinfo.value
    assert err.status_code == 404
    assert "Not Found" in err.message
    assert "OpenAPI schema not found" in err.response_text

@pytest.mark.asyncio
async def test_chunk_text_timeout_error(monkeypatch):
    # Тест таймаута
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): 
                    raise asyncio.TimeoutError("Request timed out")
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOTimeoutError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert "Request timed out" in err.message
    assert err.timeout_value is not None

@pytest.mark.asyncio
async def test_chunk_text_connection_error(monkeypatch):
    # Тест ошибки соединения
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): 
                    # Создаем простое исключение, которое наследуется от ClientConnectorError
                    class MockClientConnectorError(aiohttp.ClientConnectorError):
                        def __init__(self, message):
                            self.message = message
                        def __str__(self):
                            return self.message
                    raise MockClientConnectorError("Connection refused")
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOConnectionError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert "Failed to connect to server" in err.message
    assert isinstance(err.original_error, aiohttp.ClientConnectorError)

@pytest.mark.asyncio
async def test_health_server_disconnected_error(monkeypatch):
    # Тест разрыва соединения
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): 
                    raise aiohttp.ServerDisconnectedError("Server disconnected")
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOConnectionError) as excinfo:
        await client.health()
    err = excinfo.value
    assert "Server disconnected" in err.message
    assert isinstance(err.original_error, aiohttp.ServerDisconnectedError)

@pytest.mark.asyncio
async def test_get_help_network_error(monkeypatch):
    # Тест сетевой ошибки
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): 
                    raise aiohttp.ClientOSError("Network is unreachable")
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOConnectionError) as excinfo:
        await client.get_help()
    err = excinfo.value
    assert "Connection error" in err.message  # Изменено с "Network error" на "Connection error"
    assert isinstance(err.original_error, aiohttp.ClientOSError)

@pytest.mark.asyncio
async def test_unexpected_error_wrapped(monkeypatch):
    # Тест неожиданной ошибки
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): 
                    raise RuntimeError("Unexpected runtime error")
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    with pytest.raises(SVOConnectionError) as excinfo:
        await client.chunk_text("test")
    err = excinfo.value
    assert "Unexpected error during request" in err.message
    assert isinstance(err.original_error, RuntimeError)

@pytest.mark.asyncio
async def test_chunk_text_success_false(monkeypatch):
    """Test chunk_text when server returns success=false"""
    class FakeResponse:
        async def json(self): 
            return {
                "result": {
                    "success": False,
                    "error": {
                        "code": "validation_error",
                        "message": "Text validation failed",
                        "data": {"field": "text", "reason": "too_short"}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.chunk_text("test")
    
    assert exc_info.value.code == "validation_error"
    assert "Text validation failed" in exc_info.value.message
    assert exc_info.value.chunk_error is not None
    assert exc_info.value.chunk_error["code"] == "validation_error"

@pytest.mark.asyncio
async def test_get_help_success_false(monkeypatch):
    """Test get_help when server returns success=false"""
    class FakeResponse:
        async def json(self): 
            return {
                "result": {
                    "success": False,
                    "error": {
                        "code": "command_not_found",
                        "message": "Command not found",
                        "data": {"command": "unknown_cmd"}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.get_help("unknown_cmd")
    
    assert exc_info.value.code == "command_not_found"
    assert "Command not found" in exc_info.value.message
    assert exc_info.value.chunk_error is not None

@pytest.mark.asyncio
async def test_health_success_false(monkeypatch):
    """Test health when server returns success=false"""
    class FakeResponse:
        async def json(self): 
            return {
                "result": {
                    "success": False,
                    "error": {
                        "code": "service_unavailable",
                        "message": "Service is temporarily unavailable",
                        "data": {"status": "degraded"}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.health()
    
    assert exc_info.value.code == "service_unavailable"
    assert "Service is temporarily unavailable" in exc_info.value.message
    assert exc_info.value.chunk_error is not None

@pytest.mark.asyncio
async def test_chunk_text_success_false_no_error_details(monkeypatch):
    """Test chunk_text when server returns success=false without error details"""
    class FakeResponse:
        async def json(self): 
            return {
                "result": {
                    "success": False
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.chunk_text("test")
    
    assert exc_info.value.code == "unknown_error"
    assert "Server returned success=false" in exc_info.value.message
    assert exc_info.value.chunk_error == {}

@pytest.mark.asyncio
async def test_chunk_text_empty_result_error(monkeypatch):
    """Test chunk_text when server returns empty result"""
    class FakeResponse:
        async def json(self): 
            return {"result": None}
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.chunk_text("test")
    
    assert exc_info.value.code == "empty_result"
    assert "Empty result from server" in exc_info.value.message 

@pytest.mark.asyncio
async def test_chunk_text_invalid_params_error(monkeypatch):
    """Test chunk_text when server returns JSON-RPC InvalidParamsError (-32602)"""
    class FakeResponse:
        async def json(self): 
            return {
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {
                        "code": "text_too_short",
                        "message": "Text is too short for chunking",
                        "details": {"min_length": 10, "actual_length": 2}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOJSONRPCError) as exc_info:
        await client.chunk_text("Hi")
    
    assert exc_info.value.code == -32602
    assert "Invalid params" in exc_info.value.message
    assert exc_info.value.data is not None
    assert exc_info.value.data.get("code") == "text_too_short"

@pytest.mark.asyncio
async def test_chunk_text_missing_text_parameter(monkeypatch):
    """Test chunk_text when server returns missing_text_parameter error"""
    class FakeResponse:
        async def json(self): 
            return {
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {
                        "code": "missing_text_parameter",
                        "message": "Text parameter is required",
                        "details": {}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOJSONRPCError) as exc_info:
        await client.chunk_text("")
    
    assert exc_info.value.code == -32602
    assert "Invalid params" in exc_info.value.message
    assert exc_info.value.data.get("code") == "missing_text_parameter"

@pytest.mark.asyncio
async def test_chunk_text_no_valid_chunks_error(monkeypatch):
    """Test chunk_text when server returns no_valid_chunks as application error"""
    class FakeResponse:
        async def json(self): 
            return {
                "result": {
                    "success": False,
                    "error": {
                        "code": "no_valid_chunks",
                        "message": "No valid chunks after normalization",
                        "data": {"filtered_count": 5, "reason": "all_chunks_too_small"}
                    }
                }
            }
        def raise_for_status(self): pass
    
    class FakeSession:
        def post(self, url, json, *args, **kwargs):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    
    client = ChunkerClient()
    client.session = FakeSession()
    
    with pytest.raises(SVOServerError) as exc_info:
        await client.chunk_text("Some text that results in no valid chunks")
    
    assert exc_info.value.code == "no_valid_chunks"
    assert "No valid chunks after normalization" in exc_info.value.message
    assert exc_info.value.chunk_error is not None
    assert exc_info.value.chunk_error.get("data", {}).get("filtered_count") == 5 