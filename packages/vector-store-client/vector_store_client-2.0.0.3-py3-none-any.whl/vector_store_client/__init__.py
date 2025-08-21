"""
Vector Store Client Package.

This package provides an async client for interacting with Vector Store servers
using JSON-RPC 2.0 protocol. It supports all Vector Store operations including
chunk creation, search, deletion, and system management.

Main classes:
    - VectorStoreClient: Main client class
    - BaseVectorStoreClient: Base client for JSON-RPC communication
    - SemanticChunk: Chunk data model
    - SearchResult: Search result model

Example:
    >>> from vector_store_client import VectorStoreClient
    >>> client = await VectorStoreClient.create("http://localhost:8007")
    >>> health = await client.get_health()
    >>> print(f"Server status: {health.status}")

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0.0
"""

# Main client classes
from .client import VectorStoreClient
from .client_extended import VectorStoreClientExtended
from .base_client import BaseVectorStoreClient

# Adapters
from .adapters import BaseAdapter, SVOChunkerAdapter, EmbeddingAdapter

# Data models
from .models import (
    SemanticChunk, SearchResult, CreateChunksResponse, HealthResponse
)

# Type definitions
from .types import (
    SearchOrder,
    EmbeddingModel,
    # Type aliases
    ChunkId,
    Vector,
    MetadataDict,
    SearchResult as SearchResultType,
    JsonRpcId,
    JsonRpcResult,
    MetadataFilter,
    SearchParams
)

# Exceptions
from .exceptions import (
    VectorStoreError,
    ValidationError,
    ConnectionError,
    JsonRpcError,
    ServerError,
    NotFoundError,
    DuplicateError,
    SVOError,
    EmbeddingError,
    UserCancelledError,
    # Phase 6 exceptions
    PluginError,
    MiddlewareError,
    MonitoringError,
    BackupError,
    MigrationError,
    StreamingError
)

# Utility functions
from .utils import (
    generate_uuid,
    generate_sha256_hash,
    format_timestamp,
    normalize_text,
    merge_metadata,
    setup_logging,
    retry_with_backoff,
    chunk_list,
    process_batch_concurrent,
    safe_json_serialize,
    safe_json_deserialize,
    validate_and_clean_dict,
    extract_text_snippet,
    calculate_similarity_score,
    format_duration,
    get_memory_usage,
    create_progress_callback
)

# Validation functions
from .validation import (
    validate_url,
    validate_timeout,
    validate_chunk_id,
    validate_text_content,
    validate_embedding,
    validate_tags,
    validate_metadata,
    validate_search_params,
    validate_search_order,
    validate_embedding_model,
    validate_uuid_list,
    validate_json_rpc_response,
    validate_health_response,
    validate_create_response,
    validate_embedding_dimension,
    validate_chunk_metadata
)

# Constants
from .types import (
    # Validation constants
    MIN_CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    MIN_SEARCH_LIMIT,
    MAX_SEARCH_LIMIT,
    MIN_RELEVANCE_THRESHOLD,
    MAX_RELEVANCE_THRESHOLD,
    MIN_OFFSET,
    MAX_OFFSET,
    MIN_TIMEOUT,
    MAX_TIMEOUT,
    EMBEDDING_DIMENSION,
    UUID_LENGTH,
    SHA256_LENGTH,
    
    # Default values
    DEFAULT_TIMEOUT,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_RELEVANCE_THRESHOLD,
    DEFAULT_CHUNK_TYPE,
    DEFAULT_LANGUAGE,
    DEFAULT_STATUS,
    DEFAULT_SEARCH_ORDER,
    DEFAULT_EMBEDDING_MODEL,
    
    # JSON-RPC constants
    JSON_RPC_VERSION,
    DEFAULT_JSON_RPC_ID,
    
    # HTTP constants
    DEFAULT_HEADERS,
    
    # Retry constants
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_BACKOFF_FACTOR,
    
    # Batch processing constants
    DEFAULT_BATCH_SIZE,
    MAX_BATCH_SIZE,
    DEFAULT_CONCURRENT_REQUESTS,
    MAX_CONCURRENT_REQUESTS,
    
    # Logging constants
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_DATE_FORMAT,
    
    # Cache constants
    DEFAULT_CACHE_TTL,
    MAX_CACHE_TTL,
    DEFAULT_CACHE_SIZE,
    MAX_CACHE_SIZE
)

# CLI interface
from .vst_cli import cli

# Phase 6: Optimization and Expansion
from .plugins import (
    BasePlugin, PluginRegistry,
    TextPreprocessorPlugin, EmbeddingOptimizerPlugin,
    MetadataEnricherPlugin, QualityCheckerPlugin
)

from .middleware import (
    BaseMiddleware, MiddlewareChain,
    LoggingMiddleware, CachingMiddleware,
    RetryMiddleware, MetricsMiddleware
)

from .monitoring import (
    PerformanceMonitor, HealthChecker, MetricsCollector
)

# Package metadata
__version__ = "2.0.0.3"
__author__ = "Vasily Zdanovskiy"
__email__ = "vasilyvz@gmail.com"
__license__ = "MIT"

# Public API
__all__ = [
    # Main classes
    "VectorStoreClient",
    "VectorStoreClientExtended",
    "BaseVectorStoreClient",
    
    # Adapters
    "BaseAdapter",
    "SVOChunkerAdapter",
    "EmbeddingAdapter",
    
    # Data models
    "SemanticChunk",
    "SearchResult",
    "CreateChunksResponse",
    "HealthResponse",
    
    # Type definitions
    "ChunkType",
    "LanguageEnum",
    "ChunkStatus",
    "SearchOrder",
    "EmbeddingModel",
    "ChunkRole",
    "BlockType",
    "ChunkId",
    "Vector",
    "MetadataDict",
    "SearchResultType",
    "JsonRpcId",
    "JsonRpcResult",
    "MetadataFilter",
    "SearchParams",
    
    # Exceptions
    "VectorStoreError",
    "ValidationError",
    "ConnectionError",
    "JsonRpcError",
    "ServerError",
    "NotFoundError",
    "DuplicateError",
    "SVOError",
    "EmbeddingError",
    "UserCancelledError",
    "PluginError",
    "MiddlewareError",
    "MonitoringError",
    "BackupError",
    "MigrationError",
    "StreamingError",
    
    # Utility functions
    "generate_uuid",
    "generate_sha256_hash",
    "format_timestamp",
    "normalize_text",
    "merge_metadata",
    "setup_logging",
    "retry_with_backoff",
    "chunk_list",
    "process_batch_concurrent",
    "safe_json_serialize",
    "safe_json_deserialize",
    "validate_and_clean_dict",
    "extract_text_snippet",
    "calculate_similarity_score",
    "format_duration",
    "get_memory_usage",
    "create_progress_callback",
    
    # Validation functions
    "validate_url",
    "validate_timeout",
    "validate_chunk_id",
    "validate_text_content",
    "validate_embedding",
    "validate_tags",
    "validate_metadata",
    "validate_search_params",
    "validate_chunk_type",
    "validate_language",
    "validate_status",
    "validate_search_order",
    "validate_embedding_model",
    "validate_uuid_list",
    "validate_json_rpc_response",
    "validate_health_response",
    "validate_create_response",
    "validate_source_id",
    "validate_embedding_dimension",
    "validate_chunk_metadata",
    "validate_chunk_role",
    "validate_block_type",
    
    # Constants
    "MIN_CHUNK_SIZE",
    "MAX_CHUNK_SIZE",
    "MIN_SEARCH_LIMIT",
    "MAX_SEARCH_LIMIT",
    "MIN_RELEVANCE_THRESHOLD",
    "MAX_RELEVANCE_THRESHOLD",
    "MIN_OFFSET",
    "MAX_OFFSET",
    "MIN_TIMEOUT",
    "MAX_TIMEOUT",
    "EMBEDDING_DIMENSION",
    "UUID_LENGTH",
    "SHA256_LENGTH",
    "DEFAULT_TIMEOUT",
    "DEFAULT_LIMIT",
    "DEFAULT_OFFSET",
    "DEFAULT_RELEVANCE_THRESHOLD",
    "DEFAULT_CHUNK_TYPE",
    "DEFAULT_LANGUAGE",
    "DEFAULT_STATUS",
    "DEFAULT_SEARCH_ORDER",
    "DEFAULT_EMBEDDING_MODEL",
    "JSON_RPC_VERSION",
    "DEFAULT_JSON_RPC_ID",
    "DEFAULT_HEADERS",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_BACKOFF_FACTOR",
    "DEFAULT_BATCH_SIZE",
    "MAX_BATCH_SIZE",
    "DEFAULT_CONCURRENT_REQUESTS",
    "MAX_CONCURRENT_REQUESTS",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_DATE_FORMAT",
    "DEFAULT_CACHE_TTL",
    "MAX_CACHE_TTL",
    "DEFAULT_CACHE_SIZE",
    "MAX_CACHE_SIZE",
    
    # CLI interface
    "cli",
    
    # Phase 6: Optimization and Expansion
    # Plugins
    "BasePlugin",
    "PluginRegistry",
    "TextPreprocessorPlugin",
    "EmbeddingOptimizerPlugin",
    "MetadataEnricherPlugin",
    "QualityCheckerPlugin",
    
    # Middleware
    "BaseMiddleware",
    "MiddlewareChain",
    "LoggingMiddleware",
    "CachingMiddleware",
    "RetryMiddleware",
    "MetricsMiddleware",
    
    # Monitoring
    "PerformanceMonitor",
    "HealthChecker",
    "MetricsCollector",
    
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Maintenance operations
    "find_duplicate_uuids",
    "force_delete_by_uuids",
    "chunk_hard_delete",
    "chunk_deferred_cleanup",
    "clean_faiss_orphans",
    "reindex_missing_embeddings",
    "maintenance_health_check",
    "perform_full_maintenance",
    "cleanup_duplicates"
] 