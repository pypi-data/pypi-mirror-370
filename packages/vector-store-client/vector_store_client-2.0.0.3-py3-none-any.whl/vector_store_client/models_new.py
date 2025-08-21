"""
Vector Store Client Models - Updated Version.

This module defines Pydantic models for all data structures used in the
Vector Store client, including request/response models and data validation.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SemanticChunk(BaseModel):
    """
    Semantic chunk model for storing text content with comprehensive metadata.
    
    This model represents a chunk of text content with associated metadata,
    embeddings, and semantic information.
    
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
        failed_count: Number of chunks that failed
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


class DuplicateUuidsResponse(BaseModel):
    """
    Response model for duplicate UUID detection.
    
    This model represents the response from finding duplicate UUIDs.
    
    Attributes:
        success: Whether the operation was successful
        duplicate_uuids: List of duplicate UUIDs found
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    duplicate_uuids: Optional[List[str]] = Field(None, description="Duplicate UUIDs found")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


class CleanupResponse(BaseModel):
    """
    Response model for cleanup operations.
    
    This model represents the response from cleanup operations.
    
    Attributes:
        success: Whether the operation was successful
        cleaned_count: Number of items cleaned up
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    cleaned_count: Optional[int] = Field(None, description="Number of items cleaned up")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


class ReindexResponse(BaseModel):
    """
    Response model for reindex operations.
    
    This model represents the response from reindexing operations.
    
    Attributes:
        success: Whether the operation was successful
        reindexed_count: Number of items reindexed
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    reindexed_count: Optional[int] = Field(None, description="Number of items reindexed")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


class EmbedResponse(BaseModel):
    """
    Response model for embedding operations.
    
    This model represents the response from embedding generation.
    
    Attributes:
        success: Whether the operation was successful
        embeddings: List of generated embeddings
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    embeddings: Optional[List[List[float]]] = Field(None, description="Generated embeddings")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


class ModelsResponse(BaseModel):
    """
    Response model for model information.
    
    This model represents the response from model information requests.
    
    Attributes:
        success: Whether the operation was successful
        models: List of available models
        error: Error information if failed
    """
    
    success: bool = Field(..., description="Operation success status")
    models: Optional[List[Dict[str, Any]]] = Field(None, description="Available models")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
