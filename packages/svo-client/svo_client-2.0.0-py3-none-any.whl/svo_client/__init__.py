"""SVO Client - Async client for SVO semantic chunker microservice."""

from .chunker_client import (
    ChunkerClient,
    SVOServerError,
    SVOJSONRPCError,
    SVOHTTPError,
    SVOConnectionError,
    SVOTimeoutError,
)

__all__ = [
    "ChunkerClient",
    "SVOServerError",
    "SVOJSONRPCError", 
    "SVOHTTPError",
    "SVOConnectionError",
    "SVOTimeoutError",
]

__version__ = "2.0.0"