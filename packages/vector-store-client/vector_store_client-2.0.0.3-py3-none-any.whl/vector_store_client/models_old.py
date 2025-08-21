"""
Vector Store Client Models.

This module defines Pydantic models for all data structures used in the
Vector Store client, including request/response models and data validation.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from .types import (
    SearchOrder, EmbeddingModel,
    DEFAULT_CHUNK_TYPE, DEFAULT_LANGUAGE, DEFAULT_STATUS, DEFAULT_SEARCH_ORDER,
    DEFAULT_EMBEDDING_MODEL, EMBEDDING_DIMENSION
)
# Import enums from chunk_metadata_adapter for better validation
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum, ChunkStatus, ChunkRole, BlockType


class SemanticChunk(BaseModel):
    """
    Semantic chunk model for storing text content with comprehensive metadata.
    
    This model represents a chunk of text content with associated metadata,
    embeddings, and semantic information. It integrates with chunk_metadata_adapter
    for enhanced metadata handling.
    
    Required fields for client:
        - body: Original text content (1-10000 chars)
        - text: Normalized text for search (optional, defaults to body)
    
    Auto-generated fields:
        - uuid: Unique chunk identifier
        - sha256: SHA256 хеш (автогенерируется)
        - created_at: ISO8601 дата (автогенерируется)
    """
    
    # Обязательные поля для клиента
    body: str = Field(..., min_length=1, max_length=10000, description="Original text content (1-10000 chars)")
    text: Optional[str] = Field(None, min_length=0, max_length=10000, description="Normalized text for search (optional, defaults to body)")
    
    # Автогенерируемые поля
    uuid: Optional[str] = Field(None, description="Unique chunk identifier")
    sha256: Optional[str] = Field(None, description="SHA256 хеш (автогенерируется)")
    created_at: Optional[str] = Field(None, description="ISO8601 дата (автогенерируется)")
    
    # Основные поля
    type: Optional[str] = Field(None, description="Chunk type (e.g., 'Draft', 'DocBlock')")
    language: Optional[str] = Field(None, description="Language code (e.g., 'en', 'ru', 'python')")
    category: Optional[str] = Field(None, max_length=64, description="Business category (e.g., 'science', 'programming')")
    title: Optional[str] = Field(None, max_length=256, description="Title or short name")
    tags: Optional[List[str]] = Field(None, description="List of tags for classification")
    
    # Embedding field (optional for creation, required for search results)
    embedding: Optional[List[float]] = Field(None, description="384-dimensional embedding vector")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate type field."""
        if v is None:
            return v
        valid_types = ["Draft", "DocBlock", "CodeBlock", "Message", "Section", "Other"]
        if v not in valid_types:
            return "DocBlock"  # Default value
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language field."""
        if v is None:
            return v
        # Common language codes
        valid_languages = ["en", "ru", "uk", "de", "fr", "es", "zh", "ja", "python", "javascript", "java", "cpp", "csharp"]
        if v not in valid_languages:
            return "en"  # Default value
        return v
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding field."""
        if v is None:
            return v
        if len(v) != 384:
            raise ValueError("Embedding must be exactly 384-dimensional")
        return v
    def validate_status(cls, v: ChunkStatus) -> ChunkStatus:
        """Validate status field using from_string method."""
        if isinstance(v, str):
            result = ChunkStatus.from_string(v)
            if result is not None:
                return result
            return ChunkStatus.default_value()
        return v
    
    status: ChunkStatus = Field(ChunkStatus.NEW, description="Статус обработки")
    
    # Бизнес-поля
    category: Optional[str] = Field(None, max_length=64, description="Бизнес-категория")
    title: Optional[str] = Field(None, max_length=256, description="Заголовок")
    project: Optional[str] = Field(None, max_length=128, description="Название проекта")
    year: Optional[int] = Field(None, ge=0, le=2100, description="Год")
    is_public: Optional[bool] = Field(None, description="Флаг публичности")
    source: Optional[str] = Field(None, max_length=64, description="Источник данных")
    
    # Структурные поля
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID задачи")
    subtask_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID подзадачи")
    unit_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID единицы")
    block_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID блока")
    ordinal: Optional[int] = Field(None, description="Порядок чанка")
    start: Optional[int] = Field(None, description="Начальная позиция")
    end: Optional[int] = Field(None, description="Конечная позиция")
    block_index: Optional[int] = Field(None, description="Индекс блока")
    source_lines_start: Optional[int] = Field(None, description="Начальная строка")
    source_lines_end: Optional[int] = Field(None, description="Конечная строка")
    source_path: Optional[str] = Field(None, max_length=512, description="Путь к файлу")
    
    @field_validator('block_type')
    @classmethod
    def validate_block_type(cls, v: BlockType) -> BlockType:
        """Validate block_type field using from_string method."""
        if v is None:
            return BlockType.default_value()
        if isinstance(v, str):
            result = BlockType.from_string(v)
            if result is not None:
                return result
            return BlockType.default_value()
        return v
    
    block_type: Optional[BlockType] = Field(BlockType.PARAGRAPH, description="Тип блока")
    chunking_version: Optional[str] = Field(None, max_length=32, description="Версия алгоритма")
    
    # Метрики качества
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Качество (0-1)")
    coverage: Optional[float] = Field(None, ge=0.0, le=1.0, description="Покрытие (0-1)")
    cohesion: Optional[float] = Field(None, ge=0.0, le=1.0, description="Связность (0-1)")
    boundary_prev: Optional[float] = Field(None, ge=0.0, le=1.0, description="Схожесть с предыдущим (0-1)")
    boundary_next: Optional[float] = Field(None, ge=0.0, le=1.0, description="Схожесть со следующим (0-1)")
    used_in_generation: Optional[bool] = Field(None, description="Использовался ли в генерации")
    
    # Обратная связь
    feedback_accepted: Optional[int] = Field(None, ge=0, description="Положительные отзывы")
    feedback_rejected: Optional[int] = Field(None, ge=0, description="Отрицательные отзывы")
    feedback_modifications: Optional[int] = Field(None, ge=0, description="Количество модификаций")
    
    # Коллекционные поля
    tags: Optional[List[str]] = Field(None, max_length=32, description="Теги (до 32 элементов)")
    links: Optional[List[str]] = Field(None, max_length=32, description="Связи (до 32 элементов)")
    block_meta: Optional[Dict] = Field(None, description="Дополнительные метаданные")
    metrics: Optional[Dict] = Field(None, description="Полный объект метрик")
    
    # Контекстные поля
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID сессии")
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID сообщения")
    
    # Вычисляемые поля
    is_code_chunk: Optional[bool] = Field(None, description="Содержит ли код")
    is_deleted: Optional[bool] = Field(None, description="Флаг удаления")
    
    @field_validator('uuid')
    @classmethod
    def validate_uuid(cls, v: Optional[str]) -> Optional[str]:
        """Validate UUID format."""
        if v is not None:
            try:
                UUID(v)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return v
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding dimensions."""
        if v is None:
            return v
        if len(v) != 384:
            raise ValueError("Embedding must have exactly 384 dimensions")
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Embedding must contain only numbers")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags list."""
        if v is not None:
            if len(v) > 32:
                raise ValueError("Maximum 32 tags allowed")
            if not all(isinstance(tag, str) and tag.strip() for tag in v):
                raise ValueError("Tags must be non-empty strings")
        return v
    
    @field_validator('links')
    @classmethod
    def validate_links(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate links list."""
        if v is not None:
            if len(v) > 32:
                raise ValueError("Maximum 32 links allowed")
            if not all(isinstance(link, str) and link.strip() for link in v):
                raise ValueError("Links must be non-empty strings")
        return v
    
    @model_validator(mode='after')
    def validate_content(self) -> 'SemanticChunk':
        """Validate content requirements."""
        if not self.body.strip():
            raise ValueError("Body cannot be empty")
        if len(self.body) > 10000:
            raise ValueError("Body cannot exceed 10000 characters")
        
        # Set text to body if not provided
        if self.text is None:
            self.text = self.body
        
        if len(self.text) > 10000:
            raise ValueError("Text cannot exceed 10000 characters")
        
        return self
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Custom model dump with proper handling of optional fields."""
        data = super().model_dump(**kwargs)
        # Remove None values for cleaner output
        return {k: v for k, v in data.items() if v is not None}


class SearchResult(BaseModel):
    """
    Search result model containing chunk and relevance information.
    
    This model represents a single search result with the chunk data
    and its relevance score for the search query.
    
    Attributes:
        chunk: The semantic chunk data
        relevance_score: Similarity score between query and chunk
        rank: Position in search results
    """
    
    chunk: SemanticChunk = Field(..., description="Chunk data")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    rank: Optional[int] = Field(None, description="Result rank")
    
    @field_validator('relevance_score')
    @classmethod
    def validate_relevance_score(cls, v: float) -> float:
        """Validate relevance score range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        return v


class JsonRpcRequest(BaseModel):
    """
    JSON-RPC 2.0 request model.
    
    This model represents a JSON-RPC request following the 2.0 specification.
    
    Attributes:
        jsonrpc: JSON-RPC version (always "2.0")
        method: Method name to call
        params: Method parameters (optional)
        id: Request identifier
    """
    
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")
    id: Union[str, int, None] = Field(1, description="Request identifier")
    
    @field_validator('jsonrpc')
    @classmethod
    def validate_jsonrpc_version(cls, v: str) -> str:
        """Validate JSON-RPC version."""
        if v != "2.0":
            raise ValueError("JSON-RPC version must be '2.0'")
        return v
    
    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate method name."""
        if not v.strip():
            raise ValueError("Method name cannot be empty")
        return v.strip()


class JsonRpcResponse(BaseModel):
    """
    JSON-RPC 2.0 response model.
    
    This model represents a JSON-RPC response following the 2.0 specification.
    
    Attributes:
        jsonrpc: JSON-RPC version (always "2.0")
        result: Response result (if successful)
        error: Error information (if failed)
        id: Request identifier
    """
    
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    result: Optional[Dict[str, Any]] = Field(None, description="Response result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    id: Union[str, int, None] = Field(..., description="Request identifier")
    
    @field_validator('jsonrpc')
    @classmethod
    def validate_jsonrpc_version(cls, v: str) -> str:
        """Validate JSON-RPC version."""
        if v != "2.0":
            raise ValueError("JSON-RPC version must be '2.0'")
        return v
    
    @model_validator(mode='after')
    def validate_response(self) -> 'JsonRpcResponse':
        """Validate response structure."""
        if self.result is not None and self.error is not None:
            raise ValueError("Response cannot have both result and error")
        if self.result is None and self.error is None:
            raise ValueError("Response must have either result or error")
        return self


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    This model represents the response from a health check operation.
    
    Attributes:
        status: Health status (healthy, unhealthy, degraded)
        timestamp: Response timestamp
        version: Server version
        uptime: Server uptime in seconds
        memory_usage: Memory usage information
        disk_usage: Disk usage information
    """
    
    status: str = Field(..., description="Health status")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    version: Optional[str] = Field(None, description="Server version")
    uptime: Optional[float] = Field(None, description="Server uptime in seconds")
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage")
    disk_usage: Optional[Dict[str, Any]] = Field(None, description="Disk usage")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate health status."""
        # Map server response to expected values
        status_mapping = {
            'ok': 'healthy',
            'healthy': 'healthy',
            'unhealthy': 'unhealthy', 
            'degraded': 'degraded'
        }
        
        if v in status_mapping:
            return status_mapping[v]
        
        valid_statuses = ['healthy', 'unhealthy', 'degraded']
        raise ValueError(f"Status must be one of: {valid_statuses} or 'ok'")


class CreateChunksResponse(BaseModel):
    """
    Response model for chunk creation operations.
    
    This model represents the response from creating chunks in the vector store.
    
    Attributes:
        success: Whether the operation was successful
        uuids: List of created chunk UUIDs
        error: Error information if failed
        created_count: Number of chunks created
    """
    
    success: bool = Field(..., description="Whether the operation was successful")
    uuids: Optional[List[str]] = Field(None, description="List of created chunk UUIDs")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")
    created_count: Optional[int] = Field(None, description="Number of chunks created")
    failed_count: Optional[int] = Field(None, description="Number of chunks that failed")
    
    @field_validator('uuids')
    @classmethod
    def validate_uuids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate UUID list."""
        if v is not None:
            for uuid_str in v:
                try:
                    UUID(uuid_str)
                except ValueError:
                    raise ValueError(f"Invalid UUID in list: {uuid_str}")
        return v
    
    @model_validator(mode='after')
    def validate_response(self) -> 'CreateChunksResponse':
        """Validate response consistency."""
        if self.success:
            if self.uuids is None:
                raise ValueError("Successful response must include UUIDs")
        else:
            if self.error is None:
                raise ValueError("Failed response must include error information")
        return self


class SearchResponse(BaseModel):
    """
    Response model for search operations.
    
    This model represents the response from searching chunks in the vector store.
    
    Attributes:
        results: List of search results
        total_count: Total number of matching chunks
        query_time: Time taken for the search in seconds
        search_params: Parameters used for the search
    """
    
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    total_count: int = Field(0, description="Total number of matching chunks")
    query_time: Optional[float] = Field(None, description="Search time in seconds")
    search_params: Optional[Dict[str, Any]] = Field(None, description="Search parameters")
    
    @field_validator('total_count')
    @classmethod
    def validate_total_count(cls, v: int) -> int:
        """Validate total count."""
        if v < 0:
            raise ValueError("Total count cannot be negative")
        return v
    
    @field_validator('query_time')
    @classmethod
    def validate_query_time(cls, v: Optional[float]) -> Optional[float]:
        """Validate query time."""
        if v is not None and v < 0:
            raise ValueError("Query time cannot be negative")
        return v


class DeleteResponse(BaseModel):
    """
    Response model for delete operations.
    
    This model represents the response from deleting chunks from the vector store.
    
    Attributes:
        success: Whether the operation was successful
        deleted_count: Number of chunks deleted
        error: Error information if failed
        deleted_uuids: List of deleted chunk UUIDs
    """
    
    success: bool = Field(..., description="Operation success status")
    deleted_count: Optional[int] = Field(None, description="Number of chunks deleted")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    deleted_uuids: Optional[List[str]] = Field(None, description="Deleted chunk UUIDs")
    
    @field_validator('deleted_count')
    @classmethod
    def validate_deleted_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate deleted count."""
        if v is not None and v < 0:
            raise ValueError("Deleted count cannot be negative")
        return v
    
    @field_validator('deleted_uuids')
    @classmethod
    def validate_deleted_uuids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate deleted UUIDs list."""
        if v is not None:
            for uuid_str in v:
                try:
                    UUID(uuid_str)
                except ValueError:
                    raise ValueError(f"Invalid UUID in deleted list: {uuid_str}")
        return v


class HelpResponse(BaseModel):
    """
    Response model for help operations.
    
    This model represents the response from help-related operations.
    
    Attributes:
        success: Whether the operation was successful
        help_data: Help information
        error: Error information if failed
    """
    
    success: Optional[bool] = Field(True, description="Operation success status")
    help_data: Optional[Dict[str, Any]] = Field(None, description="Help information")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    
    @field_validator('help_data')
    @classmethod
    def validate_help_data(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate help data structure."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("help_data must be a dictionary")
        return v


class ConfigResponse(BaseModel):
    """
    Response model for configuration operations.
    
    This model represents the response from configuration-related operations.
    
    Attributes:
        success: Whether the operation was successful
        config: Configuration data
        error: Error information if failed
        path: Configuration path (optional)
        value: Configuration value (optional)
        old_value: Previous configuration value (optional)
    """
    
    success: Optional[bool] = Field(True, description="Operation success status")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    path: Optional[str] = Field(None, description="Configuration path")
    value: Optional[Any] = Field(None, description="Configuration value")
    old_value: Optional[Any] = Field(None, description="Previous configuration value")
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate configuration path."""
        if v is not None and not isinstance(v, str):
            raise ValueError("path must be a string")
        return v


class DuplicateUuidsResponse(BaseModel):
    """
    Response model for duplicate UUIDs detection.
    
    This model represents the response from finding duplicate UUIDs in the vector store.
    
    Attributes:
        success: Whether the operation was successful
        duplicates: List of duplicate UUID groups (each group is a list of UUIDs)
        total_duplicates: Total number of duplicate chunks
        error: Error information if failed
    """
    success: Optional[bool] = Field(True, description="Operation success status")
    duplicates: Optional[List[List[str]]] = Field(None, description="Duplicate UUID groups")
    total_duplicates: Optional[int] = Field(None, description="Total duplicate count")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    
    @field_validator('duplicates')
    @classmethod
    def validate_duplicates(cls, v: Optional[List[List[str]]]) -> Optional[List[List[str]]]:
        """Validate duplicates structure."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("duplicates must be a list")
            for group in v:
                if not isinstance(group, list):
                    raise ValueError("Each duplicate group must be a list of UUIDs")
                for uuid_str in group:
                    if not isinstance(uuid_str, str):
                        raise ValueError("Each UUID must be a string")
        return v
    
    @field_validator('total_duplicates')
    @classmethod
    def validate_total_duplicates(cls, v: Optional[int]) -> Optional[int]:
        """Validate total duplicates count."""
        if v is not None and v < 0:
            raise ValueError("total_duplicates must be non-negative")
        return v
    
    @model_validator(mode='after')
    def validate_response(self) -> 'DuplicateUuidsResponse':
        """Validate response consistency."""
        if self.success and self.error:
            raise ValueError("Cannot have both success=True and error")
        if not self.success and not self.error:
            raise ValueError("Must have error when success=False")
        return self


class EmbedResponse(BaseModel):
    """
    Response model for embedding operations.
    
    This model represents the response from embedding service operations,
    including generated embeddings and model information.
    
    Attributes:
        embedding: Generated embedding vector
        model: Model used for embedding
        dimension: Vector dimension
        metadata: Additional metadata
    """
    
    embedding: List[float] = Field(..., description="Generated embedding vector")
    model: str = Field(..., description="Model used for embedding")
    dimension: int = Field(..., description="Vector dimension")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v: List[float]) -> List[float]:
        """Validate embedding dimensions."""
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Embedding must contain only numbers")
        return v
    
    @field_validator('dimension')
    @classmethod
    def validate_dimension(cls, v: int) -> int:
        """Validate dimension value."""
        if v <= 0:
            raise ValueError("Dimension must be positive")
        return v


class ModelsResponse(BaseModel):
    """
    Response model for available models.
    
    This model represents the response from model listing operations,
    including available models and their configurations.
    
    Attributes:
        models: Available model names
        default_model: Default model name
        model_configs: Model configurations
    """
    
    models: List[str] = Field(..., description="Available model names")
    default_model: str = Field(..., description="Default model name")
    model_configs: Dict[str, Dict[str, Any]] = Field(..., description="Model configurations")
    
    @field_validator('models')
    @classmethod
    def validate_models(cls, v: List[str]) -> List[str]:
        """Validate models list."""
        if not v:
            # Return empty list if no models available
            return []
        if not all(isinstance(model, str) and model.strip() for model in v):
            raise ValueError("Models must be non-empty strings")
        return v
    
    @field_validator('default_model')
    @classmethod
    def validate_default_model(cls, v: str) -> str:
        """Validate default model."""
        if not v or not v.strip():
            # Return default if no model specified
            return "default"
        return v.strip()


class ChunkResponse(BaseModel):
    """
    Response model for chunking operations.
    
    This model represents the response from chunking service operations,
    including generated chunks and metadata.
    
    Attributes:
        chunks: Generated chunks
        total_chunks: Total number of chunks
        chunking_metadata: Chunking metadata
    """
    
    chunks: List[SemanticChunk] = Field(..., description="Generated chunks")
    total_chunks: int = Field(..., description="Total number of chunks")
    chunking_metadata: Optional[Dict[str, Any]] = Field(None, description="Chunking metadata")
    
    @field_validator('total_chunks')
    @classmethod
    def validate_total_chunks(cls, v: int) -> int:
        """Validate total chunks count."""
        if v < 0:
            raise ValueError("Total chunks cannot be negative")
        return v
    
    @model_validator(mode='after')
    def validate_chunks_consistency(self) -> 'ChunkResponse':
        """Validate consistency between chunks list and total count."""
        if len(self.chunks) != self.total_chunks:
            raise ValueError("Chunks list length must match total_chunks")
        return self 


class CleanupResponse(BaseModel):
    """
    Response model for cleanup operations.
    
    This model represents the response from cleanup operations.
    
    Attributes:
        success: Whether the operation was successful
        cleaned_count: Number of items cleaned up
        total_processed: Total number of items processed
        dry_run: Whether this was a dry run
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    cleaned_count: Optional[int] = Field(None, description="Number of items cleaned")
    total_processed: Optional[int] = Field(None, description="Total number of items processed")
    dry_run: Optional[bool] = Field(None, description="Whether this was a dry run")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    
    @field_validator('cleaned_count')
    @classmethod
    def validate_cleaned_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate cleaned count."""
        if v is not None and v < 0:
            raise ValueError("Cleaned count cannot be negative")
        return v
    
    @field_validator('total_processed')
    @classmethod
    def validate_total_processed(cls, v: Optional[int]) -> Optional[int]:
        """Validate total processed count."""
        if v is not None and v < 0:
            raise ValueError("Total processed count cannot be negative")
        return v


class ReindexResponse(BaseModel):
    """
    Response model for reindex operations.
    
    This model represents the response from reindexing operations.
    
    Attributes:
        success: Whether the operation was successful
        reindexed_count: Number of items reindexed
        total_count: Total number of items processed
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    reindexed_count: Optional[int] = Field(None, description="Number of items reindexed")
    total_count: Optional[int] = Field(None, description="Total number of items processed")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    
    @field_validator('reindexed_count')
    @classmethod
    def validate_reindexed_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate reindexed count."""
        if v is not None and v < 0:
            raise ValueError("Reindexed count must be non-negative")
        return v
    
    @field_validator('total_count')
    @classmethod
    def validate_total_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate total count."""
        if v is not None and v < 0:
            raise ValueError("Total count must be non-negative")
        return v


class MaintenanceHealthResponse(BaseModel):
    """
    Response model for maintenance health check.
    
    This model represents the response from maintenance health check operations.
    
    Attributes:
        duplicates: Duplicate detection health information
        orphans: Orphan detection health information
        deleted: Deleted chunks health information
        embeddings: Embeddings health information
    """
    
    duplicates: Dict[str, Any] = Field(..., description="Duplicate detection health")
    orphans: Dict[str, Any] = Field(..., description="Orphan detection health")
    deleted: Dict[str, Any] = Field(..., description="Deleted chunks health")
    embeddings: Dict[str, Any] = Field(..., description="Embeddings health")
    
    @field_validator('duplicates', 'orphans', 'deleted', 'embeddings')
    @classmethod
    def validate_health_info(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate health information."""
        if not isinstance(v, dict):
            raise ValueError("Health information must be a dictionary")
        return v


class MaintenanceResultsResponse(BaseModel):
    """
    Response model for full maintenance cycle.
    
    This model represents the response from full maintenance cycle operations.
    
    Attributes:
        duplicates: Duplicate detection results
        orphans: Orphan cleanup results
        deferred_cleanup: Deferred cleanup results
        reindex: Reindexing results
    """
    
    duplicates: Dict[str, Any] = Field(..., description="Duplicate detection results")
    orphans: Dict[str, Any] = Field(..., description="Orphan cleanup results")
    deferred_cleanup: Dict[str, Any] = Field(..., description="Deferred cleanup results")
    reindex: Dict[str, Any] = Field(..., description="Reindexing results")
    
    @field_validator('duplicates', 'orphans', 'deferred_cleanup', 'reindex')
    @classmethod
    def validate_maintenance_results(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate maintenance results."""
        if not isinstance(v, dict):
            raise ValueError("Maintenance results must be a dictionary")
        return v


class DuplicateCleanupResponse(BaseModel):
    """
    Response model for duplicate cleanup operation.
    
    This model represents the response from duplicate cleanup operations.
    
    Attributes:
        success: Whether the operation was successful
        dry_run: Whether this was a dry run
        total_duplicates: Total number of duplicates found
        deleted_uuids: List of deleted UUIDs
        deleted_count: Number of deleted chunks
        error: Error message if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    total_duplicates: int = Field(..., description="Total number of duplicates found")
    deleted_uuids: List[str] = Field(default_factory=list, description="Deleted UUIDs")
    deleted_count: int = Field(..., description="Number of deleted chunks")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    @field_validator('total_duplicates')
    @classmethod
    def validate_total_duplicates(cls, v: int) -> int:
        """Validate total duplicates count."""
        if v < 0:
            raise ValueError("Total duplicates count must be non-negative")
        return v
    
    @field_validator('deleted_count')
    @classmethod
    def validate_deleted_count(cls, v: int) -> int:
        """Validate deleted count."""
        if v < 0:
            raise ValueError("Deleted count must be non-negative")
        return v
    
    @field_validator('deleted_uuids')
    @classmethod
    def validate_deleted_uuids(cls, v: List[str]) -> List[str]:
        """Validate deleted UUIDs."""
        for uuid_str in v:
            try:
                UUID(uuid_str)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {uuid_str}")
        return v
    
    @model_validator(mode='after')
    def validate_consistency(self) -> 'DuplicateCleanupResponse':
        """Validate consistency between deleted_uuids and deleted_count."""
        if len(self.deleted_uuids) != self.deleted_count:
            raise ValueError("Deleted UUIDs count must match deleted_count")
        return self 