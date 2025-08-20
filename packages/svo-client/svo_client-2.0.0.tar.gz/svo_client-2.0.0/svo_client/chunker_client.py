"""Async client for SVO semantic chunker microservice."""

__version__ = "1.3.0"

import aiohttp
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
import json
import asyncio

class SVOServerError(Exception):
    """Raised when the SVO server returns an error in the chunk response."""
    def __init__(self, code: str, message: str, chunk_error: dict = None):
        self.code = code
        self.message = message
        self.chunk_error = chunk_error or {}
        super().__init__(f"SVO server error [{code}]: {message}")

class SVOJSONRPCError(Exception):
    """Raised when the SVO server returns a JSON-RPC error response."""
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"JSON-RPC error [{code}]: {message}")

class SVOHTTPError(Exception):
    """Raised when the SVO server returns an HTTP error or invalid response."""
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"HTTP error [{status_code}]: {message}")

class SVOConnectionError(Exception):
    """Raised when there are network/connection issues with the SVO server."""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class SVOTimeoutError(Exception):
    """Raised when request to SVO server times out."""
    def __init__(self, message: str, timeout_value: float = None):
        self.message = message
        self.timeout_value = timeout_value
        super().__init__(f"Timeout error: {message}")

class ChunkerClient:
    def __init__(self, url: str = "http://localhost", port: int = 8009, timeout: float = 60.0):
        """
        :param url: Base URL of the SVO chunker service
        :param port: Port of the service
        :param timeout: HTTP request timeout in seconds (default: 60.0)
        """
        self.base_url = f"{url.rstrip('/')}: {port}"
        self.base_url = f"{url.rstrip('/')}: {port}".replace(': ', ':')
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = timeout

    async def close(self):
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _check_jsonrpc_response(self, data: dict) -> Any:
        """
        Check JSON-RPC response for errors and return result.
        
        :param data: JSON-RPC response data
        :return: Result data if successful
        :raises SVOJSONRPCError: If JSON-RPC error is present
        """
        if "error" in data:
            error = data["error"]
            raise SVOJSONRPCError(
                code=error.get("code", -1),
                message=error.get("message", "Unknown JSON-RPC error"),
                data=error.get("data", {})
            )
        return data.get("result")

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict:
        """
        Handle HTTP response and parse JSON with error handling.
        
        :param response: aiohttp response object
        :return: Parsed JSON data
        :raises SVOHTTPError: If HTTP error or JSON parsing error occurs
        """
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            response_text = ""
            try:
                response_text = await response.text()
            except:
                pass
            raise SVOHTTPError(
                status_code=e.status,
                message=f"HTTP {e.status}: {e.message}",
                response_text=response_text
            )
        
        try:
            return await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            response_text = ""
            try:
                response_text = await response.text()
            except:
                pass
            raise SVOHTTPError(
                status_code=response.status,
                message=f"Invalid JSON response: {str(e)}",
                response_text=response_text
            )

    async def _make_request(self, method: str, url: str, timeout: Optional[float] = None, **kwargs) -> Any:
        """
        Make HTTP request to the SVO chunker service.
        
        :param method: HTTP method
        :param url: Request URL
        :param timeout: Request timeout
        :param kwargs: Additional arguments for aiohttp
        :return: Response data
        """
        req_timeout = aiohttp.ClientTimeout(total=timeout or self.timeout)
        
        # Create session if not exists
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.request(method, url, timeout=req_timeout, **kwargs) as resp:
                if resp.status >= 400:
                    error_text = await resp.text()
                    if resp.status >= 500:
                        raise SVOServerError(
                            code=f"http_{resp.status}",
                            message=f"Server error: {resp.status} - {error_text}"
                        )
                    else:
                        raise SVOHTTPError(
                            status_code=resp.status,
                            message=f"HTTP error: {resp.status} - {error_text}"
                        )
                
                try:
                    data = await resp.json()
                except Exception as e:
                    raise SVOJSONRPCError(f"Failed to parse JSON response: {e}")
                
                return data
                
        except asyncio.TimeoutError:
            raise SVOTimeoutError(f"Request timed out after {req_timeout.total}s")
        except aiohttp.ClientError as e:
            raise SVOConnectionError(f"Connection error: {e}")
        except Exception as e:
            raise SVOServerError(
                code="unexpected_error",
                message=f"Unexpected error during request: {e}"
            )

    async def get_openapi_schema(self, timeout: Optional[float] = None) -> Any:
        url = f"{self.base_url}/openapi.json"
        return await self._make_request('GET', url, timeout=timeout)

    def parse_chunk(self, chunk) -> 'SemanticChunk':
        from chunk_metadata_adapter import SemanticChunk, ChunkMetadataBuilder
        if isinstance(chunk, SemanticChunk):
            return chunk
        
        # Use the adapter's json_dict_to_semantic method for proper deserialization
        try:
            builder = ChunkMetadataBuilder()
            return builder.json_dict_to_semantic(chunk)
        except Exception as e:
            raise ValueError(f"Failed to deserialize chunk using chunk_metadata_adapter: {e}\nChunk: {chunk}")

    async def get_embeddings(self, chunks: List['SemanticChunk'], timeout: Optional[float] = None) -> List['SemanticChunk']:
        """
        Get embeddings for chunks using the embedding service.
        
        :param chunks: List of SemanticChunk objects
        :param timeout: Request timeout
        :return: List of SemanticChunk objects with embeddings
        """
        try:
            from embed_client.async_client import EmbeddingServiceAsyncClient
            
            # Create embedding client
            embed_client = EmbeddingServiceAsyncClient(
                base_url=self.base_url.replace('8009', '8001'),  # Assume embedding service on port 8001
                port=8001,
                timeout=timeout or self.timeout
            )
            
            # Extract texts from chunks
            texts = [chunk.body for chunk in chunks]
            
            # Get embeddings
            response = await embed_client.embed_texts(texts)
            
            # Extract embeddings from response
            embeddings = embed_client.extract_embeddings(response)
            
            # Update chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
                
            return chunks
            
        except ImportError:
            raise ImportError("embed_client package is required for embedding functionality. Install it with: pip install embed-client")
        except Exception as e:
            raise SVOServerError(
                code="embedding_error",
                message=f"Failed to get embeddings: {e}"
            )

    async def chunk_text(self, text: str, timeout: Optional[float] = None, **params) -> List['SemanticChunk']:
        """
        Chunk text using the SVO semantic chunker service.
        
        :param text: Text to chunk
        :param timeout: Request timeout
        :param params: Additional parameters:
            - window: Window size for sentence grouping (1-10, default: 3)
            - type: Chunking type (DocBlock, CodeBlock, Message, Draft, Task, Subtask, TZ, Comment, Log, Metric, default: Draft)
            - language: Language of the text (en, ru, uk, de, fr, es, zh, ja, etc., default: UNKNOWN for auto-detection)
        :return: List of SemanticChunk objects
        """
        url = f"{self.base_url}/cmd"
        payload = {
            "command": "chunk",
            "params": {
                "text": text,
                **params
            }
        }
        
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check if the result indicates success
        if not data or "result" not in data:
            raise SVOServerError(
                code="empty_result",
                message="Empty result from server"
            )
        
        result = data["result"]
        
        # Check for application-level errors (success=false)
        if not result.get("success", True):
            error = result.get("error", {})
            raise SVOServerError(
                code=error.get("code", "unknown_error"),
                message=error.get("message", "Server returned success=false"),
                chunk_error=error
            )
        
        chunks = result.get("chunks", [])
        parsed_chunks = []
        for chunk in chunks:
            if isinstance(chunk, dict) and "error" in chunk:
                err = chunk["error"]
                raise SVOServerError(
                    code=err.get("code", "unknown"),
                    message=err.get("message", str(err)),
                    chunk_error=err
                )
            parsed_chunks.append(self.parse_chunk(chunk))
        return parsed_chunks

    async def get_commands(self, timeout: Optional[float] = None) -> Any:
        """
        Get list of available commands from the SVO chunker service.
        
        :param timeout: Request timeout
        :return: List of available commands with their descriptions
        """
        url = f"{self.base_url}/api/commands"
        return await self._make_request('GET', url, timeout=timeout)

    async def get_help(self, cmdname: Optional[str] = None, timeout: Optional[float] = None) -> Any:
        """
        Get help information from the SVO chunker service.
        
        :param cmdname: Optional command name to get specific help
        :param timeout: Request timeout
        :return: Help information
        """
        url = f"{self.base_url}/cmd"
        payload = {
            "command": "help"
        }
        if cmdname:
            payload["params"] = {"cmdname": cmdname}
            
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check if the result indicates success
        if not data or "result" not in data:
            raise SVOServerError(
                code="empty_result",
                message="Empty result from server"
            )
        
        result = data["result"]
        
        # Check for application-level errors (success=false)
        if not result.get("success", True):
            error = result.get("error", {})
            raise SVOServerError(
                code=error.get("code", "unknown_error"),
                message=error.get("message", "Server returned success=false"),
                chunk_error=error
            )
        
        return {"result": result}

    async def health(self, timeout: Optional[float] = None) -> Any:
        """
        Get health status from the SVO chunker service.
        
        :param timeout: Request timeout
        :return: Health status information
        """
        url = f"{self.base_url}/cmd"
        payload = {
            "command": "health"
        }
        
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check if the result indicates success
        if not data or "result" not in data:
            raise SVOServerError(
                code="empty_result",
                message="Empty result from server"
            )
        
        result = data["result"]
        
        # Check for application-level errors (success=false)
        if not result.get("success", True):
            error = result.get("error", {})
            raise SVOServerError(
                code=error.get("code", "unknown_error"),
                message=error.get("message", "Server returned success=false"),
                chunk_error=error
            )
        
        return {"result": result}

    def reconstruct_text(self, chunks: List['SemanticChunk']) -> str:
        """
        Reconstruct the original text from a list of SemanticChunk objects.
        Склеивает текст из чанков в исходном порядке.
        """
        sorted_chunks = sorted(
            chunks,
            key=lambda c: c.ordinal if getattr(c, 'ordinal', None) is not None else chunks.index(c)
        )
        return ''.join(chunk.text for chunk in sorted_chunks if getattr(chunk, 'text', None)) 