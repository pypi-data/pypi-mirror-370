"""
Vector Store Client - Data models for Vector Store API.

This module defines Pydantic models for all data structures used in the
Vector Store client, including chunks, search results, and API responses.

Main models:
    - SemanticChunk: Chunk metadata model
    - CreateChunksResponse: Response for chunk creation
    - SearchResult: Search result model
    - HybridSearchConfig: Configuration for hybrid search

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid
import json

# Import from chunk_metadata_adapter for enhanced functionality
try:
    from chunk_metadata_adapter import (
        SemanticChunk as AdapterSemanticChunk,
        HybridSearchConfig as AdapterHybridSearchConfig,
        HybridSearchHelper,
        SearchResult as AdapterSearchResult,
        ChunkQuery,
        ChunkMetadataBuilder
    )
    CHUNK_METADATA_ADAPTER_AVAILABLE = True
except ImportError:
    CHUNK_METADATA_ADAPTER_AVAILABLE = False
    AdapterSemanticChunk = None
    AdapterHybridSearchConfig = None
    HybridSearchHelper = None
    AdapterSearchResult = None
    ChunkQuery = None
    ChunkMetadataBuilder = None


class SemanticChunk(BaseModel):
    """
    Semantic chunk model for Vector Store API.
    
    Represents a chunk of text with metadata, embeddings, and BM25 tokens.
    Supports both basic fields and advanced metadata from chunk_metadata_adapter.
    """
    
    # Required fields
    body: str = Field(..., description="Original chunk text (required)", min_length=1, max_length=10000)
    
    # Optional fields with defaults
    text: Optional[str] = Field(None, description="Normalized text for search (optional, defaults to body)")
    type: Optional[str] = Field("DocBlock", description="Chunk type (e.g., 'Draft', 'DocBlock')")
    language: Optional[str] = Field("en", description="Language code (e.g., 'en', 'ru', 'python')")
    category: Optional[str] = Field(None, description="Business category (e.g., 'science', 'programming')", max_length=64)
    title: Optional[str] = Field(None, description="Title or short name", max_length=256)
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags for classification")
    
    # Advanced fields from chunk_metadata_adapter
    uuid: Optional[str] = Field(None, description="Unique chunk identifier")
    source_id: Optional[str] = Field(None, description="Source document identifier")
    project: Optional[str] = Field(None, description="Project identifier")
    task_id: Optional[str] = Field(None, description="Task identifier")
    subtask_id: Optional[str] = Field(None, description="Subtask identifier")
    unit_id: Optional[str] = Field(None, description="Unit identifier")
    role: Optional[str] = Field(None, description="Chunk role (e.g., 'system', 'user')")
    summary: Optional[str] = Field(None, description="Chunk summary")
    ordinal: Optional[int] = Field(None, description="Chunk order in document")
    sha256: Optional[str] = Field(None, description="SHA256 hash of chunk content")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    status: Optional[str] = Field(None, description="Chunk status")
    source_path: Optional[str] = Field(None, description="Source file path")
    quality_score: Optional[float] = Field(None, description="Quality score")
    coverage: Optional[float] = Field(None, description="Coverage score")
    cohesion: Optional[float] = Field(None, description="Cohesion score")
    boundary_prev: Optional[float] = Field(None, description="Previous boundary score")
    boundary_next: Optional[float] = Field(None, description="Next boundary score")
    used_in_generation: Optional[bool] = Field(False, description="Used in generation flag")
    feedback_accepted: Optional[int] = Field(0, description="Number of accepted feedback")
    feedback_rejected: Optional[int] = Field(0, description="Number of rejected feedback")
    feedback_modifications: Optional[int] = Field(0, description="Number of modification feedback")
    start: Optional[int] = Field(None, description="Start position in source")
    end: Optional[int] = Field(None, description="End position in source")
    year: Optional[int] = Field(None, description="Year of creation")
    is_public: Optional[bool] = Field(False, description="Public flag")
    is_deleted: Optional[bool] = Field(False, description="Deleted flag")
    source: Optional[str] = Field(None, description="Source information")
    block_type: Optional[str] = Field(None, description="Block type")
    chunking_version: Optional[str] = Field(None, description="Chunking version")
    block_id: Optional[str] = Field(None, description="Block identifier")
    embedding: Optional[List[float]] = Field(None, description="384-dimensional embedding vector")
    block_index: Optional[int] = Field(None, description="Block index")
    source_lines_start: Optional[int] = Field(None, description="Start line in source")
    source_lines_end: Optional[int] = Field(None, description="End line in source")
    links: Optional[List[str]] = Field(default_factory=list, description="Related links")
    block_meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Block metadata")
    tags_flat: Optional[str] = Field(None, description="Flat tags string")
    link_related: Optional[str] = Field(None, description="Related link")
    link_parent: Optional[str] = Field(None, description="Parent link")
    is_code_chunk: Optional[bool] = Field(False, description="Code chunk flag")
    
    # Metrics and tokens
    metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Chunk metrics")
    
    @validator('text', pre=True, always=True)
    def set_text_default(cls, v, values):
        """Set text to body if not provided."""
        if v is None and 'body' in values:
            return values['body']
        return v
    
    @validator('uuid', pre=True, always=True)
    def set_uuid_default(cls, v):
        """Generate UUID if not provided."""
        if v is None:
            return str(uuid.uuid4())
        return v
    
    @validator('sha256', pre=True, always=True)
    def set_sha256_default(cls, v, values):
        """Generate SHA256 if not provided."""
        if v is None and 'body' in values:
            import hashlib
            return hashlib.sha256(values['body'].encode('utf-8')).hexdigest()
        return v
    
    @validator('created_at', pre=True, always=True)
    def set_created_at_default(cls, v):
        """Set creation timestamp if not provided."""
        if v is None:
            return datetime.utcnow()
        return v
    
    def get_bm25_tokens(self) -> List[str]:
        """Get BM25 tokens from metrics."""
        if self.metrics and 'bm25_tokens' in self.metrics:
            return self.metrics['bm25_tokens'] or []
        return []
    
    def get_tokens(self) -> List[str]:
        """Get regular tokens from metrics."""
        if self.metrics and 'tokens' in self.metrics:
            return self.metrics['tokens'] or []
        return []
    
    def to_adapter_chunk(self) -> Optional['AdapterSemanticChunk']:
        """Convert to chunk_metadata_adapter SemanticChunk if available."""
        if not CHUNK_METADATA_ADAPTER_AVAILABLE:
            return None
        
        try:
            builder = ChunkMetadataBuilder()
            return builder.json_dict_to_semantic(self.model_dump())
        except Exception:
            return None
    
    @classmethod
    def from_adapter_chunk(cls, adapter_chunk: 'AdapterSemanticChunk') -> 'SemanticChunk':
        """Create from chunk_metadata_adapter SemanticChunk."""
        if adapter_chunk is None:
            raise ValueError("Adapter chunk cannot be None")
        
        # Convert adapter chunk to dict and create our chunk
        chunk_dict = adapter_chunk.model_dump() if hasattr(adapter_chunk, 'model_dump') else adapter_chunk.dict()
        return cls(**chunk_dict)
    
    def model_dump_json_serializable(self) -> Dict[str, Any]:
        """
        Convert model to dict with JSON-serializable values.
        
        Handles datetime serialization and other non-JSON types.
        """
        data = self.model_dump(exclude_none=True)
        
        # Convert datetime objects to ISO format strings
        if 'created_at' in data and data['created_at'] is not None:
            if isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
        
        return data


class CreateChunksResponse(BaseModel):
    """
    Response model for chunk creation operation.
    
    Contains information about the success of the operation and created chunk UUIDs.
    """
    success: bool = Field(..., description="Operation success status")
    uuids: List[str] = Field(default_factory=list, description="List of created chunk UUIDs")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if operation failed")
    count: Optional[int] = Field(None, description="Number of chunks created")


class SearchResult(BaseModel):
    """
    Search result model.
    
    Represents a single search result with chunk data and relevance score.
    """
    chunk: SemanticChunk = Field(..., description="Found chunk")
    score: float = Field(..., description="Relevance score (0.0-1.0)")
    rank: Optional[int] = Field(None, description="Result rank")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class HybridSearchConfig(BaseModel):
    """
    Configuration for hybrid search combining BM25 and semantic search.
    
    Provides parameters for different fusion strategies and score weights.
    """
    bm25_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for BM25 scores")
    semantic_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for semantic scores")
    strategy: str = Field("weighted_sum", description="Fusion strategy")
    normalize_scores: bool = Field(True, description="Whether to normalize scores")
    min_score_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum score threshold")
    max_score_threshold: float = Field(1.0, ge=0.0, le=1.0, description="Maximum score threshold")
    
    @validator('semantic_weight')
    def validate_weights(cls, v, values):
        """Ensure weights sum to approximately 1.0."""
        bm25_weight = values.get('bm25_weight', 0.5)
        if abs(bm25_weight + v - 1.0) > 0.001:
            raise ValueError("BM25 and semantic weights must sum to 1.0")
        return v
    
    def to_adapter_config(self) -> Optional['AdapterHybridSearchConfig']:
        """Convert to chunk_metadata_adapter HybridSearchConfig if available."""
        if not CHUNK_METADATA_ADAPTER_AVAILABLE:
            return None
        
        try:
            from chunk_metadata_adapter import HybridStrategy
            strategy_map = {
                "weighted_sum": HybridStrategy.WEIGHTED_SUM,
                "reciprocal_rank": HybridStrategy.RECIPROCAL_RANK,
                "comb_sum": HybridStrategy.COMB_SUM,
                "comb_mnz": HybridStrategy.COMB_MNZ
            }
            strategy = strategy_map.get(self.strategy, HybridStrategy.WEIGHTED_SUM)
            
            return AdapterHybridSearchConfig(
                bm25_weight=self.bm25_weight,
                semantic_weight=self.semantic_weight,
                strategy=strategy,
                normalize_scores=self.normalize_scores,
                min_score_threshold=self.min_score_threshold,
                max_score_threshold=self.max_score_threshold
            )
        except Exception:
            return None


class ChunkQuery(BaseModel):
    """
    Enhanced query model for chunk search operations.
    
    Supports both simple field-based filtering and complex AST-based filtering,
    as well as BM25 and hybrid search capabilities.
    
    Features:
    - Simple field filtering (legacy compatibility)
    - Complex AST-based filtering with logical expressions
    - BM25 full-text search with configurable parameters
    - Hybrid search combining BM25 and semantic search
    - Type-safe field validation
    - Performance optimization
    
    Usage:
        >>> # Simple filtering
        >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
        
        >>> # BM25 search
        >>> query = ChunkQuery(search_query="machine learning", search_fields=["body", "text"])
        
        >>> # Hybrid search
        >>> query = ChunkQuery(
        ...     search_str="AI algorithms",
        ...     search_query="machine learning",
        ...     hybrid_search=True,
        ...     bm25_weight=0.6,
        ...     semantic_weight=0.4
        ... )
        
        >>> # Complex AST filtering
        >>> query = ChunkQuery(filter_expr="(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7")
    """
    
    # Simple field filters (legacy compatibility)
    uuid: Optional[str] = Field(default=None, description="Unique identifier (UUIDv4)")
    source_id: Optional[str] = Field(default=None, description="Source identifier (UUIDv4)")
    project: Optional[str] = Field(default=None, description="Project name")
    task_id: Optional[str] = Field(default=None, description="Task identifier (UUIDv4)")
    subtask_id: Optional[str] = Field(default=None, description="Subtask identifier (UUIDv4)")
    unit_id: Optional[str] = Field(default=None, description="Processing unit identifier (UUIDv4)")
    type: Optional[str] = Field(default=None, description="Chunk type")
    role: Optional[str] = Field(default=None, description="Role in the system")
    language: Optional[str] = Field(default=None, description="Language code")
    body: Optional[str] = Field(default=None, description="Original chunk text")
    text: Optional[str] = Field(default=None, description="Normalized text for search")
    summary: Optional[str] = Field(default=None, description="Short summary of the chunk")
    ordinal: Optional[int] = Field(default=None, description="Order of the chunk")
    sha256: Optional[str] = Field(default=None, description="SHA256 hash of the text")
    created_at: Optional[str] = Field(default=None, description="ISO8601 creation date")
    status: Optional[str] = Field(default=None, description="Processing status")
    source_path: Optional[str] = Field(default=None, description="Path to the source file")
    quality_score: Optional[float] = Field(default=None, description="Quality score [0,1]")
    coverage: Optional[float] = Field(default=None, description="Coverage [0,1]")
    cohesion: Optional[float] = Field(default=None, description="Cohesion [0,1]")
    boundary_prev: Optional[float] = Field(default=None, description="Boundary similarity with previous chunk")
    boundary_next: Optional[float] = Field(default=None, description="Boundary similarity with next chunk")
    used_in_generation: Optional[bool] = Field(default=None, description="Whether used in generation")
    feedback_accepted: Optional[int] = Field(default=None, description="How many times the chunk was accepted")
    feedback_rejected: Optional[int] = Field(default=None, description="How many times the chunk was rejected")
    start: Optional[int] = Field(default=None, description="Start offset")
    end: Optional[int] = Field(default=None, description="End offset")
    category: Optional[str] = Field(default=None, description="Business category")
    title: Optional[str] = Field(default=None, description="Title or short name")
    year: Optional[int] = Field(default=None, description="Year")
    is_public: Optional[bool] = Field(default=None, description="Public visibility")
    is_deleted: Optional[bool] = Field(default=None, description="Soft delete flag")
    source: Optional[str] = Field(default=None, description="Data source")
    block_type: Optional[str] = Field(default=None, description="Type of the source block")
    chunking_version: Optional[str] = Field(default=None, description="Version of the chunking algorithm")
    block_id: Optional[str] = Field(default=None, description="UUIDv4 of the source block")
    embedding: Optional[List[float]] = Field(default=None, description="Embedding vector(s)")
    block_index: Optional[int] = Field(default=None, description="Index of the block in the source document")
    source_lines_start: Optional[int] = Field(default=None, description="Start line in the source file")
    source_lines_end: Optional[int] = Field(default=None, description="End line in the source file")
    tags: Optional[List[str]] = Field(default=None, description="Categorical tags for the chunk")
    links: Optional[List[str]] = Field(default=None, description="References to other chunks")
    block_meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the block")
    tags_flat: Optional[str] = Field(default=None, description="Comma-separated tags for flat storage")
    link_related: Optional[str] = Field(default=None, description="Related chunk UUID")
    link_parent: Optional[str] = Field(default=None, description="Parent chunk UUID")
    
    # AST-based filtering
    filter_expr: Optional[str] = Field(default=None, description="Complex filter expression for AST parsing")
    
    # Semantic search
    search_str: Optional[str] = Field(default=None, description="Semantic search string for vector similarity")
    
    # BM25 full-text search fields
    search_query: Optional[str] = Field(
        default=None, 
        description="Full-text search query for BM25 search"
    )
    
    search_fields: Optional[List[str]] = Field(
        default_factory=lambda: ["body", "text", "summary", "title"],
        description="Fields to search in (body, text, summary, title)"
    )
    
    # BM25 parameters
    bm25_k1: Optional[float] = Field(
        default=1.2,
        ge=0.0, le=3.0,
        description="BM25 k1 parameter (term frequency saturation)"
    )
    
    bm25_b: Optional[float] = Field(
        default=0.75,
        ge=0.0, le=1.0,
        description="BM25 b parameter (length normalization)"
    )
    
    # Hybrid search parameters
    hybrid_search: Optional[bool] = Field(
        default=False,
        description="Enable hybrid search (BM25 + semantic)"
    )
    
    bm25_weight: Optional[float] = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Weight for BM25 score in hybrid search"
    )
    
    semantic_weight: Optional[float] = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Weight for semantic score in hybrid search"
    )
    
    # Result parameters
    min_score: Optional[float] = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Minimum score threshold for results"
    )
    
    max_results: Optional[int] = Field(
        default=100,
        ge=1, le=1000,
        description="Maximum number of results to return"
    )
    
    # Legacy parameters for compatibility
    limit: Optional[int] = Field(default=10, description="Maximum number of results (legacy)")
    level_of_relevance: Optional[float] = Field(default=0.0, description="Minimum relevance threshold (legacy)")
    offset: Optional[int] = Field(default=0, description="Number of results to skip (legacy)")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filter (legacy)")
    ast_filter: Optional[Dict[str, Any]] = Field(default=None, description="AST-based filter (legacy)")
    
    @validator('bm25_weight', 'semantic_weight')
    def validate_weights(cls, v, values):
        """Ensure weights sum to approximately 1.0 when both are set."""
        if v is not None and 'semantic_weight' in values and values['semantic_weight'] is not None:
            if abs(v + values['semantic_weight'] - 1.0) > 0.001:
                raise ValueError("BM25 and semantic weights must sum to 1.0")
        return v
    
    @validator('search_fields')
    def validate_search_fields(cls, v):
        """Validate search fields."""
        if v is not None:
            valid_fields = ["body", "text", "summary", "title", "category", "tags_flat"]
            for field in v:
                if field not in valid_fields:
                    raise ValueError(f"Invalid search field: {field}. Valid fields: {valid_fields}")
        return v
    
    def to_adapter_query(self) -> Optional['ChunkQuery']:
        """Convert to chunk_metadata_adapter ChunkQuery if available."""
        if not CHUNK_METADATA_ADAPTER_AVAILABLE:
            return None
        
        try:
            # Create adapter query with available fields
            query_data = self.model_dump(exclude_none=True)
            
            # Remove legacy fields that don't exist in adapter
            query_data.pop("limit", None)
            query_data.pop("level_of_relevance", None)
            query_data.pop("offset", None)
            query_data.pop("metadata_filter", None)
            query_data.pop("ast_filter", None)
            
            return ChunkQuery(**query_data)
        except Exception:
            return None
    
    def get_search_params(self) -> Dict[str, Any]:
        """
        Get search parameters for Vector Store API.
        
        Converts the query to the format expected by the Vector Store server.
        
        Returns:
            Dict containing search parameters
        """
        params = {}
        
        # Basic search parameters
        if self.search_str:
            params["search_str"] = self.search_str
        
        if self.search_query:
            params["search_query"] = self.search_query
        
        if self.search_fields:
            params["search_fields"] = self.search_fields
        
        # BM25 parameters
        if self.bm25_k1 is not None:
            params["bm25_k1"] = self.bm25_k1
        
        if self.bm25_b is not None:
            params["bm25_b"] = self.bm25_b
        
        # Hybrid search parameters
        if self.hybrid_search:
            params["hybrid_search"] = True
        
        if self.bm25_weight is not None:
            params["bm25_weight"] = self.bm25_weight
        
        if self.semantic_weight is not None:
            params["semantic_weight"] = self.semantic_weight
        
        # Result parameters
        if self.min_score is not None:
            params["min_score"] = self.min_score
        
        if self.max_results is not None:
            params["max_results"] = self.max_results
        
        # Legacy parameters
        if self.limit is not None:
            params["limit"] = self.limit
        
        if self.level_of_relevance is not None:
            params["level_of_relevance"] = self.level_of_relevance
        
        if self.offset is not None:
            params["offset"] = self.offset
        
        if self.metadata_filter is not None:
            params["metadata_filter"] = self.metadata_filter
        
        if self.ast_filter is not None:
            params["ast_filter"] = self.ast_filter
        
        return params


# Response models for API operations
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model: Optional[str] = Field(None, description="Model information")
    version: Optional[str] = Field(None, description="Service version")


class ConfigResponse(BaseModel):
    """Configuration response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Configuration data")
    error: Optional[str] = Field(None, description="Error message")


class HelpResponse(BaseModel):
    """Help response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Help data")
    error: Optional[str] = Field(None, description="Error message")


class ChunkResponse(BaseModel):
    """Chunk operation response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Chunk data")
    error: Optional[str] = Field(None, description="Error message")


class MaintenanceHealthResponse(BaseModel):
    """Maintenance health response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Health data")
    error: Optional[str] = Field(None, description="Error message")


class MaintenanceResultsResponse(BaseModel):
    """Maintenance results response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Results data")
    error: Optional[str] = Field(None, description="Error message")


class DuplicateCleanupResponse(BaseModel):
    """Duplicate cleanup response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Cleanup data")
    error: Optional[str] = Field(None, description="Error message")
