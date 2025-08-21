# Стандарт стиля кода

## Докстринги

### Докстринг в начале файла
```python
"""
Vector Store Client - Async client for Vector Store API.

This module provides high-level interface for interacting with Vector Store
service using JSON-RPC 2.0 protocol. Supports all operations: create, search,
delete, health check, and configuration management.

Main classes:
    - VectorStoreClient: Main client class
    - SemanticChunk: Chunk metadata model
    - SearchResult: Search result model

Example:
    >>> from vector_store_client import VectorStoreClient
    >>> client = await VectorStoreClient.create("http://localhost:8007")
    >>> health = await client.health_check()
    >>> print(f"Server status: {health.status}")

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""
```

### Докстринг класса
```python
class VectorStoreClient:
    """
    Async client for Vector Store API.
    
    Provides high-level interface for interacting with Vector Store service
    using JSON-RPC 2.0 protocol. Supports all operations: create, search, 
    delete, health check, and configuration management.
    
    Attributes:
        base_url (str): Base URL of the Vector Store server
        timeout (float): Request timeout in seconds
        session (httpx.AsyncClient): HTTP client session
        
    Example:
        >>> client = await VectorStoreClient.create("http://localhost:8007")
        >>> health = await client.health_check()
        >>> print(f"Server status: {health.status}")
        
    Note:
        All methods are async and must be awaited. The client automatically
        handles connection management and JSON-RPC protocol details.
    """
```

### Докстринг метода
```python
async def create_chunks(
    self, 
    chunks: List[SemanticChunk]
) -> CreateChunksResponse:
    """
    Create multiple chunks in the vector store.
    
    Creates one or many chunk records with 384-dimensional embeddings.
    Each chunk is validated through SemanticChunk validation before storage.
    Operation is atomic - if any chunk fails validation, entire operation fails.
    
    Parameters:
        chunks (List[SemanticChunk], required): List of chunk metadata objects.
            Each chunk must have 'body' and 'text' fields (required).
            All other fields are optional or auto-generated.
            See SemanticChunk for complete field definitions.
    
    Returns:
        CreateChunksResponse: Response containing list of created UUIDs.
            - success (bool): True if operation succeeded
            - uuids (List[str]): List of created chunk UUIDs
            - error (Optional[Dict]): Error details if failed
    
    Raises:
        ValidationError: If any chunk fails validation
        ConnectionError: If connection to server fails
        ServerError: If server returns error response
        
    Example:
        >>> chunks = [
        ...     SemanticChunk(body="Text 1", text="Text 1", type=ChunkType.DOC_BLOCK),
        ...     SemanticChunk(body="Text 2", text="Text 2", type=ChunkType.DOC_BLOCK)
        ... ]
        >>> result = await client.create_chunks(chunks)
        >>> print(f"Created {len(result.uuids)} chunks")
        
    Note:
        This method automatically generates UUIDs, timestamps, and SHA256 hashes
        for chunks that don't have them. Embeddings must be provided as 384-dim vectors.
    """
```

## Типизация

### Явное указание типов и обязательности
```python
# Обязательные параметры
async def create_chunk(
    self,
    body: str,                    # required
    text: str,                    # required
    chunk_type: ChunkType,        # required
    embedding: List[float]        # required
) -> CreateChunkResponse:

# Опциональные параметры с дефолтом
async def search_chunks(
    self,
    search_str: Optional[str] = None,           # optional
    metadata_filter: Optional[Dict[str, Any]] = None,  # optional
    limit: int = 10,                            # optional with default
    level_of_relevance: float = 0.0,            # optional with default
    offset: int = 0                             # optional with default
) -> SearchResponse:

# Параметры с валидацией
async def create_chunks(
    self,
    chunks: List[SemanticChunk] = Field(min_length=1, max_length=100)  # with validation
) -> CreateChunksResponse:
```

### Явное указание типа значения
```python
# Простые типы
async def health_check(self) -> HealthResponse:
async def get_config(self, path: str) -> str:
async def is_connected(self) -> bool:
async def get_server_version(self) -> str:

# Списки
async def search_chunks(self, query: str) -> List[SemanticChunk]:
async def get_all_uuids(self) -> List[str]:
async def get_duplicate_uuids(self) -> List[str]:

# Опциональные значения
async def find_chunk(self, uuid: str) -> Optional[SemanticChunk]:
async def get_optional_config(self, path: str) -> Optional[str]:
async def get_chunk_metrics(self, uuid: str) -> Optional[ChunkMetrics]:

# Union типы
async def execute_command(
    self, 
    command: str
) -> Union[SuccessResponse, ErrorResponse]:

# Сложные типы
async def search_with_metadata(
    self,
    query: str,
    filter: MetadataFilter
) -> SearchResult:
```

## Возвращаемые значения - List[SemanticChunk]

### Примеры методов, возвращающих List[SemanticChunk]
```python
async def search_chunks(
    self,
    search_str: Optional[str] = None,
    metadata_filter: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    level_of_relevance: float = 0.0
) -> List[SemanticChunk]:
    """
    Search for chunks by semantic string and/or metadata filter.
    
    Parameters:
        search_str: Semantic search string (will be embedded as 384-dim vector)
        metadata_filter: Filter by chunk metadata fields
        limit: Maximum number of results to return
        level_of_relevance: Minimum relevance threshold
        
    Returns:
        List[SemanticChunk]: List of matching chunks with metadata.
            Each chunk contains:
            - uuid (str): Unique chunk identifier
            - body (str): Original text content
            - text (str): Normalized text for search
            - embedding (List[float]): 384-dimensional vector
            - metadata (Dict): Additional chunk metadata
    """

async def get_chunks_by_uuids(
    self,
    uuids: List[str]
) -> List[SemanticChunk]:
    """
    Retrieve chunks by their UUIDs.
    
    Parameters:
        uuids: List of chunk UUIDs to retrieve
        
    Returns:
        List[SemanticChunk]: List of found chunks.
            Chunks not found are excluded from the result.
    """

async def get_chunks_by_type(
    self,
    chunk_type: ChunkType,
    limit: int = 100
) -> List[SemanticChunk]:
    """
    Get chunks by their type.
    
    Parameters:
        chunk_type: Type of chunks to retrieve
        limit: Maximum number of results
        
    Returns:
        List[SemanticChunk]: List of chunks of specified type.
    """

async def get_chunks_by_language(
    self,
    language: LanguageEnum,
    limit: int = 100
) -> List[SemanticChunk]:
    """
    Get chunks by language.
    
    Parameters:
        language: Language of chunks to retrieve
        limit: Maximum number of results
        
    Returns:
        List[SemanticChunk]: List of chunks in specified language.
    """
```

## Структура кода

### Импорты
```python
# Стандартная библиотека
import asyncio
import json
import logging
from typing import List, Dict, Optional, Union, Any, TypeVar
from datetime import datetime, timezone

# Сторонние библиотеки
import httpx
from pydantic import BaseModel, Field, ValidationError

# Локальные импорты
from .exceptions import VectorStoreError, ValidationError, ConnectionError
from .models import SemanticChunk, SearchResult, CreateChunksResponse
from .types import ChunkType, LanguageEnum, MetadataFilter
```

### Константы
```python
# API константы
DEFAULT_TIMEOUT = 30.0
DEFAULT_LIMIT = 10
EMBEDDING_DIMENSION = 384
MAX_CHUNK_SIZE = 10000

# JSON-RPC константы
JSON_RPC_VERSION = "2.0"
DEFAULT_JSON_RPC_ID = 1

# HTTP константы
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

### Классы
```python
class VectorStoreClient:
    """
    Async client for Vector Store API.
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[httpx.AsyncClient] = None
    ) -> None:
        """
        Initialize Vector Store client.
        
        Parameters:
            base_url: Base URL of the Vector Store server
            timeout: Request timeout in seconds
            session: Optional HTTP client session
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = session or httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self) -> "VectorStoreClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close HTTP client session."""
        await self.session.aclose()
```

### Методы
```python
async def create_chunks(
    self,
    chunks: List[SemanticChunk]
) -> CreateChunksResponse:
    """
    Create multiple chunks in the vector store.
    
    Parameters:
        chunks: List of chunk metadata objects
        
    Returns:
        CreateChunksResponse: Response with created UUIDs
        
    Raises:
        ValidationError: If any chunk fails validation
        ConnectionError: If connection fails
    """
    # Валидация входных данных
    if not chunks:
        raise ValidationError("Chunks list cannot be empty")
    
    # Подготовка данных
    chunk_data = []
    for chunk in chunks:
        # Валидация каждого чанка
        if not chunk.body or not chunk.text:
            raise ValidationError(f"Chunk {chunk.uuid} missing required fields")
        
        # Преобразование в формат API
        chunk_dict = chunk.model_dump()
        chunk_data.append(chunk_dict)
    
    # Выполнение запроса
    response = await self._execute_command(
        "chunk_create",
        {"chunks": chunk_data}
    )
    
    # Обработка ответа
    if response.get("success"):
        return CreateChunksResponse(
            success=True,
            uuids=response.get("uuids", [])
        )
    else:
        raise ServerError(f"Failed to create chunks: {response.get('error')}")
```

## Обработка ошибок

### Иерархия исключений
```python
class VectorStoreError(Exception):
    """Base exception for Vector Store client."""
    pass

class ValidationError(VectorStoreError):
    """Raised when data validation fails."""
    pass

class ConnectionError(VectorStoreError):
    """Raised when connection to server fails."""
    pass

class ServerError(VectorStoreError):
    """Raised when server returns error response."""
    pass

class JsonRpcError(VectorStoreError):
    """Raised when JSON-RPC protocol error occurs."""
    pass
```

### Обработка в методах
```python
async def _execute_command(
    self,
    method: str,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute JSON-RPC command.
    
    Parameters:
        method: Command method name
        params: Command parameters
        
    Returns:
        Dict: Response data
        
    Raises:
        ConnectionError: If connection fails
        JsonRpcError: If JSON-RPC error occurs
        ServerError: If server returns error
    """
    try:
        # Подготовка запроса
        request_data = {
            "jsonrpc": JSON_RPC_VERSION,
            "method": method,
            "id": DEFAULT_JSON_RPC_ID
        }
        if params:
            request_data["params"] = params
        
        # Выполнение запроса
        response = await self.session.post(
            f"{self.base_url}/cmd",
            json=request_data,
            headers=DEFAULT_HEADERS
        )
        response.raise_for_status()
        
        # Обработка ответа
        data = response.json()
        
        if "error" in data:
            raise JsonRpcError(f"JSON-RPC error: {data['error']}")
        
        return data.get("result", {})
        
    except httpx.RequestError as e:
        raise ConnectionError(f"Connection failed: {e}")
    except httpx.HTTPStatusError as e:
        raise ServerError(f"HTTP error {e.response.status_code}: {e}")
    except json.JSONDecodeError as e:
        raise JsonRpcError(f"Invalid JSON response: {e}")
``` 