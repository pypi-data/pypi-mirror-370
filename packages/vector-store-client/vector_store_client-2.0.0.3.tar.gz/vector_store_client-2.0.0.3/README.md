# Vector Store Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/vector-store-client.svg)](https://badge.fury.io/py/vector-store-client)

Async client for Vector Store API with comprehensive JSON-RPC support. Provides high-level interface for all vector store operations including chunk creation, search, deletion, and system management.

## Features

- **Fully Async**: Built with `asyncio` and `httpx` for high-performance async operations
- **JSON-RPC 2.0**: Complete support for JSON-RPC 2.0 protocol
- **Type Safety**: Full type hints and Pydantic models for data validation
- **Comprehensive API**: Support for all Vector Store operations
- **Error Handling**: Detailed exception hierarchy with meaningful error messages
- **Batch Operations**: Efficient batch processing for large datasets
- **Connection Management**: Automatic connection pooling and retry logic
- **Logging**: Built-in logging for debugging and monitoring

## Installation

```bash
pip install vector-store-client
```

## Quick Start

```python
import asyncio
from vector_store_client import VectorStoreClient, SemanticChunk, ChunkType, LanguageEnum

async def main():
    # Create client
    client = await VectorStoreClient.create("http://localhost:8007")
    
    # Check server health
    health = await client.health_check()
    print(f"Server status: {health.status}")
    
    # Create a chunk
    chunk = SemanticChunk(
        body="Python is a high-level programming language.",
        text="Python is a high-level programming language.",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN,
        title="Python Introduction"
    )
    
    result = await client.create_chunks([chunk])
    print(f"Created chunk: {result.uuids[0]}")
    
    # Search chunks
    results = await client.search_chunks("programming language", limit=5)
    for chunk in results:
        print(f"Found: {chunk.title}")
    
    await client.close()

asyncio.run(main())
```

## Testing Scripts

The project includes comprehensive test scripts to verify all client functionality:

### 1. Comprehensive Test (`comprehensive_test_final.py`)

**Purpose**: Complete end-to-end testing of all client capabilities

**Features**:
- ✅ Health check verification
- ✅ Chunk creation from multiple text sources
- ✅ Semantic search testing
- ✅ BM25 search testing  
- ✅ Hybrid search testing
- ✅ Metadata filtering
- ✅ AST filtering with correct syntax
- ✅ Chunk deletion and verification
- ✅ Database count verification
- ✅ Compact vector embedding display

**Usage**:
```bash
python comprehensive_test_final.py
```

**Expected Output**: 10/10 tests passed with detailed logging

### 2. Deletion and AST Test (`test_deletion_and_ast.py`)

**Purpose**: Focused testing of deletion via curl and AST filtering

**Features**:
- ✅ Chunk creation for testing
- ✅ AST filtering with proper syntax validation
- ✅ Direct curl deletion commands
- ✅ Deletion verification
- ✅ Compact test execution

**Usage**:
```bash
python test_deletion_and_ast.py
```

**Expected Output**: 4/4 tests passed

### 3. CLI Testing (`vst-cli`)

**Purpose**: Command-line interface testing

**Features**:
- ✅ Health check: `vst-cli --url http://localhost:8008 health`
- ✅ Chunk creation: `vst-cli --url http://localhost:8008 chunk-create --text "Your text"`
- ✅ Search: `vst-cli --url http://localhost:8008 search --query "search term"`
- ✅ Deletion: `vst-cli --url http://localhost:8008 delete --uuids uuid1,uuid2`

## API Reference

### Client Creation

```python
# Factory method (recommended)
client = await VectorStoreClient.create("http://localhost:8007")

# Direct instantiation
client = VectorStoreClient("http://localhost:8007")
```

### Health and System

```python
# Check server health
health = await client.health_check()

# Get help information
help_info = await client.get_help()

# Get/set configuration
config = await client.get_config("server.version")
await client.set_config("search.limit", 50)
```

### Chunk Operations

```python
# Create chunks
chunks = [
    SemanticChunk(
        body="Your text content here",
        text="Your text content here",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN
    )
]
result = await client.create_chunks(chunks)

# Search chunks
results = await client.search_chunks(
    search_str="your search query",
    metadata_filter={"category": "articles"},
    limit=10
)

# Delete chunks
await client.delete_chunks({"type": "temporary"})
```

### Utility Methods

```python
# Create single text chunk
uuid = await client.create_text_chunk(
    text="Simple text content",
    chunk_type=ChunkType.DOC_BLOCK
)

# Search by text (simplified interface)
results = await client.search_by_text("query", limit=5)

# Find duplicate UUIDs
duplicates = await client.find_duplicate_uuids()

# Force delete by UUIDs
await client.force_delete_by_uuids(["uuid1", "uuid2"])
```

## Data Models

### SemanticChunk

The main data model for chunks with comprehensive metadata:

```python
chunk = SemanticChunk(
    # Required fields
    body="Original text content",
    text="Normalized text for search",
    
    # Auto-generated fields
    uuid="auto-generated-uuid",
    source_id="auto-generated-source-id",
    language=LanguageEnum.EN,
    type=ChunkType.DOC_BLOCK,
    sha256="auto-generated-hash",
    created_at="auto-generated-timestamp",
    embedding=[0.1, 0.2, ...],  # 384-dimensional vector
    
    # Optional fields
    title="Chunk title",
    category="Business category",
    tags=["tag1", "tag2"],
    session_id="session-uuid",
    message_id="message-uuid",
    summary="Auto-generated summary",
    status=ChunkStatus.ACTIVE,
    metadata={"custom": "data"}
)
```

### SearchResult

Search results with relevance information:

```python
result = SearchResult(
    chunk=SemanticChunk(...),
    relevance_score=0.95,
    distance=0.05,
    rank=1,
    highlight="...highlighted text...",
    metadata={"search_metadata": "value"}
)
```

## Error Handling

The client provides a comprehensive exception hierarchy:

```python
from vector_store_client.exceptions import (
    VectorStoreError,      # Base exception
    ConnectionError,       # Network/connection issues
    ValidationError,       # Data validation failures
    JsonRpcError,         # JSON-RPC protocol errors
    ServerError,          # Server-side errors
    NotFoundError,        # Resource not found
    DuplicateError        # Duplicate resource errors
)

try:
    await client.create_chunks(chunks)
except ValidationError as e:
    print(f"Validation failed: {e.field_errors}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ServerError as e:
    print(f"Server error: {e.server_message}")
```

## Configuration

### Logging

```python
import logging
from vector_store_client.utils import setup_logging

# Setup logging
logger = setup_logging(
    level="INFO",
    format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file="vector_store.log"
)

# Use with client
client = VectorStoreClient("http://localhost:8007", logger=logger)
```

### Timeouts and Retries

```python
# Custom timeout
client = await VectorStoreClient.create(
    "http://localhost:8007",
    timeout=60.0
)

# Retry logic is built-in for connection errors
# Custom retry can be implemented using utils.retry_with_backoff
```

## Examples

See the `examples/` directory for usage examples:

- `simple_example.py` - Basic operations (recommended for beginners)
- `working_api_example.py` - Complete API demonstration with real methods
- `advanced_usage.py` - Advanced features and patterns
- `comprehensive_api_example.py` - Legacy example (may contain non-working methods)

## Development

### Installation

```bash
git clone https://github.com/vasilyvz/vector_store_client.git
cd vector_store_client
pip install -e .
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=vector_store_client

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black vector_store_client/

# Sort imports
isort vector_store_client/

# Type checking
mypy vector_store_client/

# Linting
flake8 vector_store_client/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Vasily Zdanovskiy**
- Email: vasilyvz@gmail.com
- GitHub: [@vasilyvz](https://github.com/vasilyvz)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- **Issues**: [GitHub Issues](https://github.com/vasilyvz/vector_store_client/issues)
- **Documentation**: [GitHub Wiki](https://github.com/vasilyvz/vector_store_client/wiki)
- **Email**: vasilyvz@gmail.com 