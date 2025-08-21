"""
Pytest configuration and fixtures for Vector Store Client tests.

This module provides common fixtures and configuration for all tests
in the Vector Store client test suite.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import List, Dict, Any

from vector_store_client.models import SemanticChunk
from vector_store_client.types import ChunkType, LanguageEnum


@pytest.fixture
def sample_chunk_data():
    """
    Sample chunk data for testing.
    
    Returns:
        Dict[str, Any]: Sample chunk data dictionary
    """
    return {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "source_id": "550e8400-e29b-41d4-a716-446655440001",
        "body": "This is a sample text content for testing purposes.",
        "text": "This is a sample text content for testing purposes.",
        "language": "en",
        "type": "doc_block",
        "sha256": "a1b2c3d4e5f6...",
        "created_at": "2024-01-01T00:00:00Z",
        "embedding": [0.1] * 384,  # 384-dimensional vector
        "summary": "Sample text content for testing",
        "title": "Sample Chunk",
        "category": "Test",
        "tags": ["test", "sample", "example"],
        "status": "active",
        "metadata": {"test_key": "test_value"}
    }


@pytest.fixture
def sample_chunk(sample_chunk_data):
    """
    Sample SemanticChunk instance for testing.
    
    Returns:
        SemanticChunk: Sample chunk instance
    """
    return SemanticChunk(**sample_chunk_data)


@pytest.fixture
def sample_chunks(sample_chunk):
    """
    List of sample chunks for testing.
    
    Returns:
        List[SemanticChunk]: List of sample chunks
    """
    return [sample_chunk]


@pytest.fixture
def multiple_chunks():
    """
    Multiple chunks with different content for testing.
    
    Returns:
        List[SemanticChunk]: List of different chunks
    """
    return [
        SemanticChunk(
            body="Python is a programming language.",
            text="Python is a programming language.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Python Language",
            category="Programming"
        ),
        SemanticChunk(
            body="Machine learning is a subset of AI.",
            text="Machine learning is a subset of AI.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Machine Learning",
            category="AI/ML"
        ),
        SemanticChunk(
            body="Vector databases store embeddings.",
            text="Vector databases store embeddings.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Vector Databases",
            category="Database"
        )
    ]


@pytest.fixture
def mock_http_response():
    """
    Mock HTTP response for testing.
    
    Returns:
        AsyncMock: Mock HTTP response
    """
    response = AsyncMock()
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_http_session():
    """
    Mock HTTP session for testing.
    
    Returns:
        AsyncMock: Mock HTTP session
    """
    session = AsyncMock()
    session.is_closed = False
    return session


@pytest.fixture
def health_response_data():
    """
    Sample health response data.
    
    Returns:
        Dict[str, Any]: Health response data
    """
    return {
        "status": "ok",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "uptime": 3600.0,
        "memory_usage": {"used": 1024, "total": 2048},
        "disk_usage": {"used": 5120, "total": 10240},
        "active_connections": 5,
        "total_chunks": 100,
        "metadata": {"server_info": "test"}
    }


@pytest.fixture
def help_response_data():
    """
    Sample help response data.
    
    Returns:
        Dict[str, Any]: Help response data
    """
    return {
        "commands": [
            {"name": "health", "description": "Health check"},
            {"name": "help", "description": "Get help"},
            {"name": "config", "description": "Configuration management"},
            {"name": "chunk_create", "description": "Create chunks"},
            {"name": "search", "description": "Search chunks"}
        ],
        "total_commands": 5,
        "server_info": {"version": "1.0.0"},
        "metadata": {"api_version": "2.0"}
    }


@pytest.fixture
def create_chunks_response_data():
    """
    Sample create chunks response data.
    
    Returns:
        Dict[str, Any]: Create chunks response data
    """
    return {
        "success": True,
        "uuids": [
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440001"
        ],
        "total_created": 2,
        "total_failed": 0,
        "errors": [],
        "processing_time": 0.1,
        "metadata": {"batch_size": 2}
    }


@pytest.fixture
def search_response_data():
    """
    Sample search response data.
    
    Returns:
        Dict[str, Any]: Search response data
    """
    return {
        "chunks": [
            {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "body": "Python is a programming language.",
                "text": "Python is a programming language.",
                "type": "doc_block",
                "language": "en",
                "title": "Python Language",
                "category": "Programming"
            }
        ]
    }


@pytest.fixture
def delete_response_data():
    """
    Sample delete response data.
    
    Returns:
        Dict[str, Any]: Delete response data
    """
    return {
        "success": True,
        "deleted_count": 5,
        "total_found": 5,
        "errors": [],
        "processing_time": 0.1,
        "metadata": {"filter_applied": "type=temporary"}
    }


@pytest.fixture
def duplicate_uuids_response_data():
    """
    Sample duplicate UUIDs response data.
    
    Returns:
        Dict[str, Any]: Duplicate UUIDs response data
    """
    return {
        "duplicates": [
            {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "count": 2,
                "chunks": ["chunk1", "chunk2"]
            }
        ],
        "total_duplicates": 2,
        "total_groups": 1,
        "processing_time": 0.1,
        "metadata": {"scan_complete": True}
    }


@pytest.fixture
def config_response_data():
    """
    Sample config response data.
    
    Returns:
        Dict[str, Any]: Config response data
    """
    return {
        "success": True,
        "path": "server.version",
        "value": "1.0.0",
        "old_value": "0.9.0",
        "message": "Configuration updated successfully",
        "metadata": {"config_type": "string"}
    }


@pytest.fixture
def json_rpc_request_data():
    """
    Sample JSON-RPC request data.
    
    Returns:
        Dict[str, Any]: JSON-RPC request data
    """
    return {
        "jsonrpc": "2.0",
        "method": "health",
        "params": None,
        "id": 1
    }


@pytest.fixture
def json_rpc_response_data():
    """
    Sample JSON-RPC response data.
    
    Returns:
        Dict[str, Any]: JSON-RPC response data
    """
    return {
        "jsonrpc": "2.0",
        "result": {"status": "ok"},
        "id": 1
    }


@pytest.fixture
def json_rpc_error_response_data():
    """
    Sample JSON-RPC error response data.
    
    Returns:
        Dict[str, Any]: JSON-RPC error response data
    """
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found",
            "data": {"method": "unknown_method"}
        },
        "id": 1
    }


@pytest.fixture
def metadata_filter():
    """
    Sample metadata filter for testing.
    
    Returns:
        Dict[str, Any]: Metadata filter
    """
    return {
        "type": "doc_block",
        "language": "en",
        "category": "Programming",
        "tags": ["python", "programming"]
    }


@pytest.fixture
def search_params():
    """
    Sample search parameters for testing.
    
    Returns:
        Dict[str, Any]: Search parameters
    """
    return {
        "search_str": "programming language",
        "metadata_filter": {"category": "Programming"},
        "limit": 10,
        "level_of_relevance": 0.5,
        "offset": 0
    }


@pytest.fixture
def test_urls():
    """
    Test URLs for validation testing.
    
    Returns:
        List[str]: List of test URLs
    """
    return [
        "http://localhost:8007",
        "https://api.example.com",
        "http://127.0.0.1:8007",
        "https://vector-store.example.com/v1"
    ]


@pytest.fixture
def invalid_urls():
    """
    Invalid URLs for validation testing.
    
    Returns:
        List[str]: List of invalid URLs
    """
    return [
        "",
        "not-a-url",
        "ftp://invalid-scheme.com",
        "http://",
        "https://"
    ]


@pytest.fixture
def test_embeddings():
    """
    Test embeddings for validation testing.
    
    Returns:
        List[List[float]]: List of test embeddings
    """
    return [
        [0.1] * 384,  # 384-dimensional
        [0.2] * 768,  # 768-dimensional
        [0.3] * 1536,  # 1536-dimensional
        [0.4] * 3072   # 3072-dimensional
    ]


@pytest.fixture
def invalid_embeddings():
    """
    Invalid embeddings for validation testing.
    
    Returns:
        List[List[float]]: List of invalid embeddings
    """
    return [
        [],  # Empty
        [0.1, 0.2, 0.3],  # Wrong dimension
        [0.1] * 1000,  # Wrong dimension
        ["not", "numbers"],  # Wrong type
        [float('nan'), 0.2, 0.3],  # NaN values
        [float('inf'), 0.2, 0.3]   # Infinite values
    ]


@pytest.fixture
def test_texts():
    """
    Test texts for validation testing.
    
    Returns:
        List[str]: List of test texts
    """
    return [
        "Short text",
        "This is a medium length text for testing purposes.",
        "A" * 1000,  # 1000 characters
        "A" * 10000  # Maximum allowed
    ]


@pytest.fixture
def invalid_texts():
    """
    Invalid texts for validation testing.
    
    Returns:
        List[str]: List of invalid texts
    """
    return [
        "",  # Empty
        "   ",  # Only whitespace
        "A" * 10001,  # Too long
        None,  # None
        123  # Wrong type
    ]


@pytest.fixture
def test_tags():
    """
    Test tags for validation testing.
    
    Returns:
        List[List[str]]: List of test tag lists
    """
    return [
        ["tag1", "tag2", "tag3"],
        ["single-tag"],
        ["a" * 100],  # Maximum length tag
        []  # Empty list
    ]


@pytest.fixture
def invalid_tags():
    """
    Invalid tags for validation testing.
    
    Returns:
        List[List[str]]: List of invalid tag lists
    """
    return [
        ["tag1"] * 33,  # Too many tags
        ["a" * 101],  # Tag too long
        ["", "valid-tag"],  # Empty tag
        ["tag1", None, "tag3"],  # None tag
        [123, "valid-tag"]  # Wrong type
    ]


@pytest.fixture
def mock_logger():
    """
    Mock logger for testing.
    
    Returns:
        MagicMock: Mock logger
    """
    return MagicMock()


@pytest.fixture(autouse=True)
def reset_event_loop():
    """
    Reset event loop before each test.
    
    This ensures that each test starts with a clean event loop state.
    """
    yield
    # Clean up any pending tasks
    try:
        loop = asyncio.get_running_loop()
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except RuntimeError:
        # Event loop is closed or not running
        pass 