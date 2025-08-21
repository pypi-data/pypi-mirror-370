"""
Chunk Operations for Vector Store Client.

This module provides high-level operations for chunk management,
including creation, search, and hybrid search capabilities.

Key features:
- Chunk creation with automatic embedding generation
- Semantic search with vector similarity
- BM25 search with keyword matching
- Hybrid search combining both methods
- Integration with chunk_metadata_adapter

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
import logging

from .base_operations import BaseOperations
from ..models import (
    SemanticChunk, CreateChunksResponse, SearchResult,
    HybridSearchConfig, ChunkQuery
)
from ..adapters.embedding_adapter import EmbeddingAdapter
from ..exceptions import (
    ValidationError, ConnectionError, ServerError,
    ChunkingError, EmbeddingError
)

logger = logging.getLogger(__name__)


class ChunkOperations(BaseOperations):
    """
    High-level operations for chunk management.
    
    Provides methods for creating, searching, and managing chunks
    with support for hybrid search and advanced features.
    """
    
    def __init__(self, client):
        """
        Initialize chunk operations.
        
        Parameters:
            client: Vector Store client instance
        """
        super().__init__(client)
        self.embedding_adapter = EmbeddingAdapter()
    
    async def create_chunks(
        self,
        chunks: List[SemanticChunk]
    ) -> CreateChunksResponse:
        """
        Create multiple chunks in the vector store.
        
        Creates one or many chunk records with automatic embedding generation
        if embeddings are not provided.
        
        Parameters:
            chunks: List of chunk metadata objects.
                Each chunk must have 'body' field (required).
                All other fields are optional or auto-generated.
        
        Returns:
            CreateChunksResponse: Response containing list of created UUIDs.
        
        Raises:
            ValidationError: If any chunk fails validation
            ConnectionError: If connection to server fails
            ServerError: If server returns error response
        """
        if not chunks:
            raise ValidationError("Chunks list cannot be empty")
        
        # Validate and prepare chunks
        chunk_data = []
        for chunk in chunks:
            # Validate required fields
            if not chunk.body or not chunk.body.strip():
                raise ValidationError(f"Chunk {chunk.uuid} missing required 'body' field")
            
            # Ensure text field is set
            if not chunk.text:
                chunk.text = chunk.body
            
            # Convert to dict for API with JSON serialization
            chunk_dict = chunk.model_dump_json_serializable()
            chunk_data.append(chunk_dict)
        
        # Execute command
        logger.info(f"Sending chunk_create command with {len(chunk_data)} chunks")
        if chunk_data:
            first_chunk = chunk_data[0]
            embedding_info = "no embedding"
            if first_chunk.get("embedding"):
                embedding_len = len(first_chunk["embedding"])
                is_non_zero = any(abs(val) > 1e-10 for val in first_chunk["embedding"])
                embedding_info = f"embedding: dim={embedding_len}, non_zero={is_non_zero}"
            logger.info(f"First chunk: body='{first_chunk.get('body', '')[:50]}...', {embedding_info}")
        
        response = await self.client._execute_command(
            "chunk_create",
            {"chunks": chunk_data}
        )
        logger.info(f"Server response: success={response.get('success')}, created_count={response.get('data', {}).get('created_count', 0)}")
        
        # Parse response
        if response.get("success"):
            # Extract UUIDs from data.uuids if available, otherwise from root
            data = response.get("data", {})
            uuids = data.get("uuids", []) if data else response.get("uuids", [])
            count = len(uuids)
            
            return CreateChunksResponse(
                success=True,
                uuids=uuids,
                count=count
            )
        else:
            raise ServerError(f"Failed to create chunks: {response.get('error')}")
    
    async def create_text_chunk_with_embedding(
        self,
        text: str,
        chunk_type: str = "DocBlock",
        language: str = "en",
        category: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> CreateChunksResponse:
        """
        Create a single text chunk with automatic embedding generation.
        
        This method creates a chunk from text and automatically generates
        embeddings using the embedding service.
        
        Parameters:
            text: Text content for the chunk
            chunk_type: Type of chunk (DocBlock, CodeBlock, etc.)
            language: Language of the text
            category: Business category
            title: Title or short name
            tags: List of tags
            **kwargs: Additional chunk metadata
        
        Returns:
            CreateChunksResponse: Response with created chunk UUID
        
        Raises:
            ValidationError: If text is invalid
            EmbeddingError: If embedding generation fails
            ServerError: If chunk creation fails
        """
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty")
        
        try:
            # Generate embedding
            logger.info("Generating embedding for text chunk")
            embedding = await self.embedding_adapter.embed_text(text)
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            
            # Create chunk
            chunk = SemanticChunk(
                body=text,
                text=text,
                type=chunk_type,
                language=language,
                category=category,
                title=title,
                tags=tags or [],
                embedding=embedding,
                **kwargs
            )
            logger.info(f"Created chunk with UUID: {chunk.uuid}")
            
            # Create chunk in store
            result = await self.create_chunks([chunk])
            logger.info(f"Store result: {result}")
            return result
            
        except Exception as e:
            if "embedding" in str(e).lower():
                raise EmbeddingError(f"Failed to generate embedding: {e}")
            else:
                raise ServerError(f"Failed to create text chunk: {e}")
    
    async def search_chunks(
        self,
        search_str: Optional[str] = None,
        search_query: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        level_of_relevance: float = 0.0,
        offset: int = 0,
        hybrid_search: bool = False,
        hybrid_config: Optional[HybridSearchConfig] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Search for chunks using semantic and/or BM25 search.
        
        Supports both semantic search (vector similarity) and BM25 search
        (keyword matching), as well as hybrid search combining both methods.
        
        Parameters:
            search_str: Semantic search string (vector similarity)
            search_query: BM25 search query (keyword matching)
            search_fields: Fields for BM25 search (e.g., ['text', 'body'])
            metadata_filter: Metadata filter for results
            ast_filter: AST-based filter expression
            limit: Maximum number of results (1-1000)
            level_of_relevance: Minimum relevance threshold (0.0-1.0)
            offset: Number of results to skip
            hybrid_search: Enable hybrid search combining BM25 and semantic
            hybrid_config: Configuration for hybrid search
            **kwargs: Additional search parameters
        
        Returns:
            List[SearchResult]: List of search results with chunks and scores
        
        Raises:
            ValidationError: If search parameters are invalid
            ConnectionError: If connection to server fails
            ServerError: If server returns error response
        """
        # Validate parameters
        if not search_str and not search_query and not metadata_filter and not ast_filter:
            raise ValidationError("At least one search parameter must be provided")
        
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        if level_of_relevance < 0.0 or level_of_relevance > 1.0:
            raise ValidationError("Level of relevance must be between 0.0 and 1.0")
        
        # Prepare search parameters
        search_params = {
            "limit": limit,
            "level_of_relevance": level_of_relevance,
            "offset": offset,
            **kwargs
        }
        
        if search_str:
            search_params["search_str"] = search_str
        
        if search_query:
            search_params["search_query"] = search_query
        
        if search_fields:
            search_params["search_fields"] = search_fields
        
        if metadata_filter:
            search_params["metadata_filter"] = metadata_filter
        
        if ast_filter:
            search_params["ast_filter"] = ast_filter
        
        if hybrid_search:
            search_params["hybrid_search"] = True
            if hybrid_config:
                # Convert hybrid config to server format
                config_dict = hybrid_config.model_dump()
                search_params.update({
                    "bm25_weight": config_dict.get("bm25_weight", 0.5),
                    "semantic_weight": config_dict.get("semantic_weight", 0.5),
                    "bm25_k1": config_dict.get("bm25_k1", 1.2),
                    "bm25_b": config_dict.get("bm25_b", 0.75),
                    "min_score": config_dict.get("min_score_threshold", 0.0),
                    "max_results": config_dict.get("max_score_threshold", 1.0)
                })
        
        # Execute search
        response = await self.client._execute_command("search", search_params)
        
        # Parse results
        if response.get("success"):
            chunks_data = response.get("chunks", [])
            results = []
            
            for i, chunk_data in enumerate(chunks_data):
                # Create SemanticChunk from data
                chunk = SemanticChunk(**chunk_data)
                
                # Create SearchResult
                result = SearchResult(
                    chunk=chunk,
                    score=chunk_data.get("score", 0.0),
                    rank=i + 1,
                    metadata=chunk_data.get("metadata", {})
                )
                results.append(result)
            
            return results
        else:
            raise ServerError(f"Search failed: {response.get('error')}")
    
    async def search_with_query(
        self,
        query: ChunkQuery
    ) -> List[SearchResult]:
        """
        Search using a ChunkQuery object.
        
        This method provides a more structured way to perform searches
        using the ChunkQuery model with support for BM25 and hybrid search.
        
        Parameters:
            query: ChunkQuery object with search parameters
        
        Returns:
            List[SearchResult]: List of search results
        
        Raises:
            ValidationError: If query is invalid
            ServerError: If search fails
        """
        if not query:
            raise ValidationError("Query cannot be None")
        
        # Get search parameters from query
        search_params = query.get_search_params()
        logger.info(f"Search with query params: {search_params}")
        
        # Execute search
        response = await self.client._execute_command("search", search_params)
        logger.info(f"Search with query response: {response}")
        
        # Parse results
        if response.get("success"):
            # Extract chunks from data.chunks if available, otherwise from root
            data = response.get("data", {})
            chunks_data = data.get("chunks", []) if data else response.get("chunks", [])
            results = []
            
            for i, chunk_data in enumerate(chunks_data):
                chunk = SemanticChunk(**chunk_data)
                result = SearchResult(
                    chunk=chunk,
                    score=chunk_data.get("score", 0.0),
                    rank=i + 1,
                    metadata=chunk_data.get("metadata", {})
                )
                results.append(result)
            
            return results
        else:
            raise ServerError(f"Search failed: {response.get('error')}")
    
    async def delete_chunks(self, uuids: List[str]) -> Dict[str, Any]:
        """
        Delete chunks by UUIDs.
        
        Parameters:
            uuids: List of chunk UUIDs to delete
            
        Returns:
            Dict: Response with deletion status
            
        Raises:
            ValidationError: If UUIDs list is empty
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        if not uuids:
            raise ValidationError("UUIDs list cannot be empty")
        
        # Execute command
        response = await self.client._execute_command(
            "chunk_delete",
            {"uuids": uuids}
        )
        
        return response
    
    async def hybrid_search(
        self,
        semantic_query: str,
        bm25_query: str,
        search_fields: Optional[List[str]] = None,
        bm25_weight: float = 0.5,
        semantic_weight: float = 0.5,
        limit: int = 10,
        level_of_relevance: float = 0.0,
        **kwargs
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and BM25 search.
        
        This method combines vector similarity search with keyword-based
        BM25 search for better results.
        
        Parameters:
            semantic_query: Semantic search string for vector similarity
            bm25_query: BM25 search string for keyword matching
            search_fields: Fields for BM25 search
            bm25_weight: Weight for BM25 scores (0.0-1.0)
            semantic_weight: Weight for semantic scores (0.0-1.0)
            limit: Maximum number of results
            level_of_relevance: Minimum relevance threshold
            **kwargs: Additional search parameters
        
        Returns:
            List[SearchResult]: List of hybrid search results
        
        Raises:
            ValidationError: If parameters are invalid
            ServerError: If search fails
        """
        if not semantic_query or not bm25_query:
            raise ValidationError("Both semantic_query and bm25_query must be provided")
        
        if abs(bm25_weight + semantic_weight - 1.0) > 0.001:
            raise ValidationError("BM25 and semantic weights must sum to 1.0")
        
        # Create hybrid search configuration
        hybrid_config = HybridSearchConfig(
            bm25_weight=bm25_weight,
            semantic_weight=semantic_weight,
            strategy="weighted_sum"
        )
        
        # Perform hybrid search
        return await self.search_chunks(
            search_str=semantic_query,
            search_query=bm25_query,
            search_fields=search_fields,
            limit=limit,
            level_of_relevance=level_of_relevance,
            hybrid_search=True,
            hybrid_config=hybrid_config,
            **kwargs
        ) 