# Стандарт именования переменных, классов, методов и параметров

## Общие принципы

- **snake_case** для переменных, функций, методов, параметров
- **PascalCase** для классов, типов, исключений
- **UPPER_SNAKE_CASE** для констант
- **camelCase** не используется
- Все имена должны быть описательными и понятными

## Классы

### Именование классов
```python
class VectorStoreClient:          # ✅ Правильно
class JsonRpcRequest:             # ✅ Правильно
class SemanticChunk:              # ✅ Правильно
class ValidationError:            # ✅ Правильно

class vector_store_client:        # ❌ Неправильно
class jsonRpcRequest:             # ❌ Неправильно
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
    """
```

## Методы

### Именование методов
```python
async def create_chunks(self, chunks: List[SemanticChunk]) -> CreateChunksResponse:  # ✅
async def search_by_text(self, query: str, limit: int = 10) -> List[SearchResult]:  # ✅
async def health_check(self) -> HealthResponse:  # ✅

async def createChunks(self, chunks):  # ❌ Неправильно
async def searchByText(self, query):   # ❌ Неправильно
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
    """
```

## Параметры методов

### Именование параметров
```python
async def search_chunks(
    self,
    search_str: Optional[str] = None,           # ✅
    metadata_filter: Optional[Dict] = None,     # ✅
    limit: int = 10,                            # ✅
    level_of_relevance: float = 0.0,            # ✅
    offset: int = 0                             # ✅
) -> SearchResponse:

async def search_chunks(
    self,
    searchStr: Optional[str] = None,            # ❌ Неправильно
    metadataFilter: Optional[Dict] = None,      # ❌ Неправильно
    limit: int = 10                             # ❌ Неправильно
) -> SearchResponse:
```

### Типизация параметров
```python
# Обязательные параметры
def method(self, required_param: str) -> None:

# Опциональные параметры с дефолтом
def method(self, optional_param: Optional[str] = None) -> None:

# Параметры с ограничениями
def method(self, limit: int = Field(ge=1, le=100)) -> None:

# Сложные типы
def method(self, chunks: List[SemanticChunk]) -> None:
def method(self, filter: Dict[str, Any]) -> None:
def method(self, response: Union[SuccessResponse, ErrorResponse]) -> None:
```

## Переменные

### Именование переменных
```python
# Локальные переменные
base_url = "http://localhost:8007"              # ✅
chunk_list = [chunk1, chunk2, chunk3]           # ✅
search_results = await client.search_chunks()   # ✅

# Константы
DEFAULT_TIMEOUT = 30.0                          # ✅
MAX_CHUNK_SIZE = 10000                          # ✅
EMBEDDING_DIMENSION = 384                       # ✅

# Неправильно
baseUrl = "http://localhost:8007"               # ❌
chunkList = [chunk1, chunk2, chunk3]            # ❌
defaultTimeout = 30.0                           # ❌
```

### Типизация переменных
```python
# Простые типы
client: VectorStoreClient
base_url: str = "http://localhost:8007"
timeout: float = 30.0
is_connected: bool = False

# Сложные типы
chunks: List[SemanticChunk] = []
search_filter: Dict[str, Any] = {}
response: Optional[SearchResponse] = None

# Типы из typing
from typing import List, Dict, Optional, Union, Any

# Аннотации типов для сложных структур
MetadataFilter = Dict[str, Union[str, int, float, bool, List[str]]]
SearchParams = Dict[str, Union[str, int, float, MetadataFilter]]
```

## Исключения

### Именование исключений
```python
class VectorStoreError(Exception):              # ✅
class ValidationError(VectorStoreError):        # ✅
class ConnectionError(VectorStoreError):        # ✅
class JsonRpcError(VectorStoreError):           # ✅

class vector_store_error(Exception):            # ❌ Неправильно
class validationError(VectorStoreError):        # ❌ Неправильно
```

### Докстринг исключений
```python
class ValidationError(VectorStoreError):
    """
    Raised when data validation fails.
    
    This exception is raised when input data does not meet validation
    requirements, such as missing required fields, invalid data types,
    or constraint violations.
    
    Attributes:
        message (str): Human-readable error message
        field_errors (Dict[str, List[str]]): Field-specific validation errors
        data (Any): Original data that failed validation
    """
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, List[str]]] = None,
        data: Optional[Any] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field_errors = field_errors or {}
        self.data = data
```

## Типы данных

### Именование типов
```python
# Type aliases
ChunkId = str
Vector = List[float]
MetadataDict = Dict[str, Any]
SearchResult = List[SemanticChunk]

# Generic types
ResponseType = TypeVar('ResponseType')
RequestType = TypeVar('RequestType')

# Union types
JsonRpcId = Union[str, int, None]
JsonRpcResult = Union[Dict, List, str, bool, None]
```

## Файлы

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

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
import httpx
import asyncio
```

## Возвращаемые значения

### Типизация возвращаемых значений
```python
# Простые типы
async def health_check(self) -> HealthResponse:
async def get_config(self, path: str) -> str:
async def is_connected(self) -> bool:

# Списки
async def search_chunks(self, query: str) -> List[SemanticChunk]:
async def get_all_uuids(self) -> List[str]:

# Опциональные значения
async def find_chunk(self, uuid: str) -> Optional[SemanticChunk]:
async def get_optional_config(self, path: str) -> Optional[str]:

# Union типы
async def execute_command(self, command: str) -> Union[SuccessResponse, ErrorResponse]:
```

### Документирование возвращаемых значений
```python
async def search_chunks(
    self,
    search_str: Optional[str] = None,
    limit: int = 10
) -> List[SemanticChunk]:
    """
    Search for chunks by semantic string and/or metadata filter.
    
    Parameters:
        search_str: Semantic search string (will be embedded as 384-dim vector)
        limit: Maximum number of results to return
        
    Returns:
        List[SemanticChunk]: List of matching chunks with metadata.
            Each chunk contains:
            - uuid (str): Unique chunk identifier
            - body (str): Original text content
            - text (str): Normalized text for search
            - embedding (List[float]): 384-dimensional vector
            - metadata (Dict): Additional chunk metadata
            
    Raises:
        ValidationError: If search parameters are invalid
        ConnectionError: If connection to server fails
    """
``` 