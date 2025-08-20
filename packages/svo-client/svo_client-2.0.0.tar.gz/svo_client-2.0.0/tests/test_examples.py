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
from chunk_metadata_adapter import SemanticChunk
import sys
import types
import uuid

@pytest.mark.asyncio
async def test_example_usage(monkeypatch):
    # Мокаем методы клиента
    async def fake_chunk_text(self, text, **params):
        return [SemanticChunk(
            uuid="11111111-1111-4111-8111-111111111111",
            text="Hello, ",
            body="Hello, ",
            summary="summary",
            sha256="a"*64,
            ordinal=0,
            type="DocBlock",
            language="en",
            start=0,
            end=6,
            created_at="2024-01-01T00:00:00+00:00",
            status="new",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4())
        ),
        SemanticChunk(
            uuid="22222222-2222-4222-8222-222222222222",
            text="world!",
            body="world!",
            summary="summary",
            sha256="b"*64,
            ordinal=1,
            type="DocBlock",
            language="en",
            start=0,
            end=6,
            created_at="2024-01-01T00:00:00+00:00",
            status="new",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4())
        )]
    async def fake_health(self):
        return {"status": "ok"}
    async def fake_get_help(self, cmdname=None):
        return {"help": "info"}
    # Подмена методов
    monkeypatch.setattr(ChunkerClient, "chunk_text", fake_chunk_text)
    monkeypatch.setattr(ChunkerClient, "health", fake_health)
    monkeypatch.setattr(ChunkerClient, "get_help", fake_get_help)

    async with ChunkerClient() as client:
        chunks = await client.chunk_text("test")
        assert isinstance(chunks, list)
        assert all(isinstance(c, SemanticChunk) for c in chunks)
        text = client.reconstruct_text(chunks)
        assert text == "Hello, world!"
        health = await client.health()
        assert health["status"] == "ok"
        help_info = await client.get_help()
        assert help_info["help"] == "info"

def test_example_usage_handles_validation_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    from chunk_metadata_adapter import SemanticChunk
    def fake_validate_and_fill(data):
        return None, {'error': 'Fake validation error', 'fields': {}}
    monkeypatch.setattr(SemanticChunk, "validate_and_fill", staticmethod(fake_validate_and_fill))
    # Патчим chunk_text, чтобы выбрасывал ValueError
    async def fake_chunk_text(*args, **kwargs):
        raise ValueError("Chunk does not validate against chunk_metadata_adapter.SemanticChunk: Fake validation error")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self): return {"status": "ok"}
        async def get_help(self): return {"help": "info"}
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "Validation error:" in out 

def test_example_usage_handles_server_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    # Патчим chunk_text, чтобы выбрасывал SVOServerError
    async def fake_chunk_text(*args, **kwargs):
        raise SVOServerError("sha256_mismatch", "SHA256 mismatch: original=..., chunks=...", {"code": "sha256_mismatch", "message": "SHA256 mismatch: original=..., chunks=..."})
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self): return {"status": "ok"}
        async def get_help(self): return {"help": "info"}
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "SVO server error:" in out
    assert "sha256_mismatch" in out

def test_example_usage_handles_jsonrpc_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    # Патчим chunk_text, чтобы выбрасывал SVOJSONRPCError
    async def fake_chunk_text(*args, **kwargs):
        raise SVOJSONRPCError(-32602, "Invalid params", {"details": "test"})
    async def fake_health(*args, **kwargs):
        raise SVOJSONRPCError(-32603, "Internal error")
    async def fake_get_help(*args, **kwargs):
        raise SVOJSONRPCError(-32601, "Method not found")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self, *a, **k): return await fake_health()
        async def get_help(self, *a, **k): return await fake_get_help()
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "JSON-RPC error:" in out
    assert "Invalid params" in out
    assert "Health check JSON-RPC error:" in out
    assert "Internal error" in out
    assert "Help JSON-RPC error:" in out
    assert "Method not found" in out

def test_example_usage_handles_http_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    # Патчим методы, чтобы выбрасывали SVOHTTPError
    async def fake_chunk_text(*args, **kwargs):
        raise SVOHTTPError(500, "Internal Server Error", "Server details")
    async def fake_health(*args, **kwargs):
        raise SVOHTTPError(503, "Service Unavailable")
    async def fake_get_help(*args, **kwargs):
        raise SVOHTTPError(404, "Not Found")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self, *a, **k): return await fake_health()
        async def get_help(self, *a, **k): return await fake_get_help()
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "HTTP error:" in out
    assert "Internal Server Error" in out
    assert "Health check HTTP error:" in out
    assert "Service Unavailable" in out
    assert "Help HTTP error:" in out
    assert "Not Found" in out

def test_example_usage_handles_connection_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    # Патчим методы, чтобы выбрасывали SVOConnectionError
    async def fake_chunk_text(*args, **kwargs):
        raise SVOConnectionError("Connection refused", OSError("Connection refused"))
    async def fake_health(*args, **kwargs):
        raise SVOConnectionError("Network unreachable")
    async def fake_get_help(*args, **kwargs):
        raise SVOConnectionError("Server disconnected")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self, *a, **k): return await fake_health()
        async def get_help(self, *a, **k): return await fake_get_help()
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "Connection error:" in out
    assert "Connection refused" in out
    assert "Health check connection error:" in out
    assert "Network unreachable" in out
    assert "Help connection error:" in out
    assert "Server disconnected" in out

def test_example_usage_handles_timeout_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    # Патчим методы, чтобы выбрасывали SVOTimeoutError
    async def fake_chunk_text(*args, **kwargs):
        raise SVOTimeoutError("Request timed out after 60s", 60.0)
    async def fake_health(*args, **kwargs):
        raise SVOTimeoutError("Health check timed out", 30.0)
    async def fake_get_help(*args, **kwargs):
        raise SVOTimeoutError("Help request timed out", 15.0)
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self, *a, **k): return await fake_health()
        async def get_help(self, *a, **k): return await fake_get_help()
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "Timeout error:" in out
    assert "Request timed out after 60s" in out
    assert "Health check timeout error:" in out
    assert "Health check timed out" in out
    assert "Help timeout error:" in out
    assert "Help request timed out" in out 