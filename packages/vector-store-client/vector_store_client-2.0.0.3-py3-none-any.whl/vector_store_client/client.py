"""
Vector Store Client - Main Facade.

This module provides the main client facade that delegates to specialized
operation modules for different functionality areas.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
import logging

from .base_client import BaseVectorStoreClient
from .exceptions import (
    DuplicateError, NotFoundError, ValidationError, VectorStoreError,
    SVOError, EmbeddingError, UserCancelledError
)
from .models import (
    CreateChunksResponse, HealthResponse, SemanticChunk, ChunkQuery, SearchResult
)
from .types import (
    DEFAULT_LIMIT, DEFAULT_OFFSET, DEFAULT_RELEVANCE_THRESHOLD,
    DEFAULT_CHUNK_TYPE, DEFAULT_LANGUAGE, DEFAULT_STATUS
)
from .utils import (
    generate_uuid, generate_sha256_hash, format_timestamp, normalize_text,
    merge_metadata
)
from .validation import (
    validate_search_params, validate_uuid_list, validate_chunk_type,
    validate_language, validate_status, validate_embedding, validate_chunk_role,
    validate_block_type, validate_source_id, validate_tags, validate_metadata
)
from .adapters import SVOChunkerAdapter, EmbeddingAdapter
# Removed ChunkType and LanguageEnum imports - using string types now
from .operations import ChunkOperations, EmbeddingOperations


class VectorStoreClient(BaseVectorStoreClient):
    """
    Main client for Vector Store API.
    
    This class provides a facade for all Vector Store operations,
    delegating to specialized operation modules.
    
    Attributes:
        base_url (str): Base URL of the Vector Store server
        timeout (float): Request timeout in seconds
        session (httpx.AsyncClient): HTTP client session
        chunk_operations (ChunkOperations): Chunk-related operations
        embedding_operations (EmbeddingOperations): Embedding-related operations
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        session: Optional[Any] = None,
        svo_url: Optional[str] = None,
        embedding_url: Optional[str] = None
    ) -> None:
        """
        Initialize Vector Store client.
        
        Parameters:
            base_url: Base URL of the Vector Store server
            timeout: Request timeout in seconds
            session: Optional HTTP client session
            svo_url: Optional URL for SVO service (default: http://localhost:8009)
            embedding_url: Optional URL for embedding service (default: http://localhost:8001)
        """
        super().__init__(base_url, timeout, session)
        
        # Initialize adapters
        self.svo_adapter = SVOChunkerAdapter(
            base_url=svo_url or "http://localhost",
            port=8009  # SVO chunking service port
        )
        
        self.embedding_adapter = EmbeddingAdapter(
            base_url=embedding_url or "http://localhost",
            port=8001  # Embedding service port
        )
        
        # Initialize operation modules
        self.chunk_operations = ChunkOperations(self)
        self.embedding_operations = EmbeddingOperations(self)
        
        # Initialize plugin system
        self.plugins = {}
        self.plugin_registry = {}
        
        # Initialize middleware system
        self.middleware_chain = []
        self.middleware_registry = {}
    
    @classmethod
    async def create(
        cls,
        base_url: str,
        timeout: float = 30.0
    ) -> "VectorStoreClient":
        """
        Create and initialize Vector Store client.
        
        Factory method that creates a new client instance and validates
        the connection to the server.
        
        Parameters:
            base_url: Base URL of the Vector Store server
            timeout: Request timeout in seconds
            
        Returns:
            VectorStoreClient: Initialized client instance
            
        Raises:
            ValidationError: If base_url is invalid
            ConnectionError: If cannot connect to server
        """
        if not base_url or not isinstance(base_url, str):
            raise ValidationError("base_url must be a non-empty string")
        
        client = cls(base_url, timeout)
        
        # Test connection
        try:
            await client.health_check()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to server: {e}")
        
        return client
    
    # Delegate chunk operations
    async def create_chunks(self, chunks: List[SemanticChunk]) -> CreateChunksResponse:
        """Create multiple chunks in the vector store."""
        return await self.chunk_operations.create_chunks(chunks)
    
    async def create_text_chunk(self, text: str, **kwargs) -> CreateChunksResponse:
        """Create a chunk with automatic embedding generation."""
        return await self.chunk_operations.create_text_chunk_with_embedding(text, **kwargs)
    
    async def search_chunks(self, **kwargs) -> List[SemanticChunk]:
        """Search for chunks by various criteria."""
        return await self.chunk_operations.search_chunks(**kwargs)
    
    async def search_with_query(self, query: 'ChunkQuery') -> List['SearchResult']:
        """Search for chunks using ChunkQuery object."""
        return await self.chunk_operations.search_with_query(query)
    
    async def delete_chunks(self, uuids: List[str]) -> Dict[str, Any]:
        """Delete chunks by UUIDs."""
        return await self.chunk_operations.delete_chunks(uuids)
    
    async def search_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        limit: int = DEFAULT_LIMIT,
        level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
        offset: int = DEFAULT_OFFSET
    ) -> List[SemanticChunk]:
        """
        Search for chunks by metadata filter.
        
        Convenience method for metadata-based search that delegates to search_chunks.
        
        Parameters:
            metadata_filter: Filter by chunk metadata fields
            limit: Maximum number of results to return
            level_of_relevance: Minimum relevance threshold
            offset: Number of results to skip
            
        Returns:
            List[SemanticChunk]: List of matching chunks with metadata
        """
        return await self.search_chunks(
            metadata_filter=metadata_filter,
            limit=limit,
            level_of_relevance=level_of_relevance,
            offset=offset
        )
    
    async def search_by_text(
        self,
        search_str: str,
        limit: int = DEFAULT_LIMIT,
        level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
        offset: int = DEFAULT_OFFSET
    ) -> List[SemanticChunk]:
        """
        Search for chunks by text string.
        
        Convenience method for text-based search that delegates to search_chunks.
        
        Parameters:
            search_str: Text to search for
            limit: Maximum number of results to return
            level_of_relevance: Minimum relevance threshold
            offset: Number of results to skip
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            search_str=search_str,
            limit=limit,
            level_of_relevance=level_of_relevance,
            offset=offset
        )
    
    async def search_by_ast(
        self,
        ast_filter: Dict[str, Any],
        limit: int = DEFAULT_LIMIT,
        level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
        offset: int = DEFAULT_OFFSET
    ) -> List[SemanticChunk]:
        """
        Search for chunks by AST filter.
        
        Convenience method for AST-based search that delegates to search_chunks.
        
        Parameters:
            ast_filter: AST filter for search
            limit: Maximum number of results to return
            level_of_relevance: Minimum relevance threshold
            offset: Number of results to skip
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            ast_filter=ast_filter,
            limit=limit,
            level_of_relevance=level_of_relevance,
            offset=offset
        )
    
    async def search_by_vector(
        self,
        embedding: List[float],
        limit: int = DEFAULT_LIMIT,
        level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
        offset: int = DEFAULT_OFFSET
    ) -> List[SemanticChunk]:
        """
        Search for chunks by vector embedding.
        
        Convenience method for vector-based search that delegates to search_chunks.
        
        Parameters:
            embedding: Vector embedding to search with
            limit: Maximum number of results to return
            level_of_relevance: Minimum relevance threshold
            offset: Number of results to skip
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            embedding=embedding,
            limit=limit,
            level_of_relevance=level_of_relevance,
            offset=offset
        )
    
    async def count_chunks(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count chunks matching the filter.
        
        Parameters:
            metadata_filter: Filter by metadata
            ast_filter: AST-based filter
            
        Returns:
            int: Number of matching chunks
        """
        params = {}
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        if ast_filter:
            params["ast_filter"] = ast_filter
        
        response = await self._execute_command("count", params)
        return response.get("data", {}).get("count", 0)
    
    async def get_chunk_statistics(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get chunk statistics.
        
        Parameters:
            metadata_filter: Filter by metadata
            ast_filter: AST-based filter
            
        Returns:
            Dict[str, Any]: Statistics about chunks
        """
        params = {}
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        if ast_filter:
            params["ast_filter"] = ast_filter
        
        response = await self._execute_command("info", params)
        return response.get("data", {})
    
    async def count_chunks_by_type(
        self,
        chunk_type: str
    ) -> int:
        """
        Count chunks by type.
        
        Parameters:
            chunk_type: Type of chunks to count
            
        Returns:
            int: Number of chunks of specified type
        """
        return await self.count_chunks(metadata_filter={"type": chunk_type})
    
    async def count_chunks_by_language(
        self,
        language: str
    ) -> int:
        """
        Count chunks by language.
        
        Parameters:
            language: Language of chunks to count
            
        Returns:
            int: Number of chunks in specified language
        """
        return await self.count_chunks(metadata_filter={"language": language})
    
    async def delete_chunk(
        self,
        uuid: str
    ) -> Dict[str, Any]:
        """
        Delete a single chunk by UUID.
        
        Parameters:
            uuid: UUID of chunk to delete
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        return await self.delete_chunks(uuids=[uuid])
    
    async def delete_chunks_with_confirmation(
        self,
        uuids: List[str],
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Delete chunks with confirmation.
        
        Parameters:
            uuids: List of UUIDs to delete
            confirm: Confirmation flag
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        if not confirm:
            raise ValidationError("Deletion requires confirmation (confirm=True)")
        return await self.delete_chunks(uuids=uuids)
    
    async def hard_delete_chunks_with_confirmation(
        self,
        uuids: List[str],
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Hard delete chunks with confirmation.
        
        Parameters:
            uuids: List of UUIDs to hard delete
            confirm: Confirmation flag
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        return await self.chunk_hard_delete(uuids=uuids, confirm=confirm)
    
    async def maintenance_health_check(self) -> Dict[str, Any]:
        """
        Perform maintenance health check.
        
        Returns:
            Dict[str, Any]: Maintenance health status
        """
        # This is a placeholder - actual implementation would depend on server capabilities
        health = await self.get_health()
        return {
            "status": health.status,
            "maintenance_required": False,
            "orphaned_entries": 0,
            "duplicate_chunks": 0
        }
    
    async def perform_full_maintenance(self) -> Dict[str, Any]:
        """
        Perform full maintenance operations.
        
        Returns:
            Dict[str, Any]: Maintenance results
        """
        results = {}
        
        # Clean FAISS orphans
        try:
            faiss_result = await self.clean_faiss_orphans()
            results["faiss_cleanup"] = faiss_result.cleaned_count
        except Exception as e:
            results["faiss_cleanup"] = {"error": str(e)}
        
        # Reindex missing embeddings
        try:
            reindex_result = await self.reindex_missing_embeddings()
            results["reindex"] = reindex_result.reindexed_count
        except Exception as e:
            results["reindex"] = {"error": str(e)}
        
        # Clean deferred chunks
        try:
            cleanup_result = await self.chunk_deferred_cleanup()
            results["deferred_cleanup"] = cleanup_result.cleaned_count
        except Exception as e:
            results["deferred_cleanup"] = {"error": str(e)}
        
        return results
    
    async def cleanup_duplicates(
        self,
        dry_run: bool = True,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Clean up duplicate chunks.
        
        Parameters:
            dry_run: If True, only report duplicates without deleting
            metadata_filter: Filter for duplicates
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        # Find duplicates
        duplicates_response = await self.find_duplicate_uuids(metadata_filter=metadata_filter)
        
        if dry_run:
            return {
                "success": True,
                "duplicates_found": duplicates_response.total_duplicates,
                "duplicates": duplicates_response.duplicates,
                "dry_run": True,
                "total_duplicates": duplicates_response.total_duplicates
            }
        else:
            # Delete duplicates using force_delete_by_uuids
            deleted_count = 0
            for duplicate_group in duplicates_response.duplicates:
                if len(duplicate_group) > 1:
                    # Keep the first one, delete the rest
                    uuids_to_delete = duplicate_group[1:]
                    try:
                        delete_response = await self.force_delete_by_uuids(uuids_to_delete)
                        deleted_count += delete_response.deleted_count
                    except Exception as e:
                        # Log error but continue with other groups
                        print(f"Error deleting duplicates: {e}")
            
            return {
                "success": True,
                "duplicates_found": duplicates_response.total_duplicates,
                "duplicates_removed": deleted_count,
                "dry_run": False,
                "deleted_count": deleted_count
            }
    
    async def create_chunk_with_full_metadata(
        self,
        text: str,
        source_id: str,
        **kwargs
    ) -> SemanticChunk:
        """
        Create a chunk with full metadata.
        
        Parameters:
            text: Text content
            source_id: Source identifier
            **kwargs: Additional metadata
            
        Returns:
            SemanticChunk: Created chunk
        """
        chunk = SemanticChunk(
            body=text,
            text=text,
            source_id=source_id,
            **kwargs
        )
        response = await self.create_chunks([chunk])
        chunk.uuid = response.uuids[0]
        return chunk
    
    async def create_chunks_with_full_metadata(
        self,
        chunks_data: List[Dict[str, Any]]
    ) -> List[SemanticChunk]:
        """
        Create multiple chunks with full metadata.
        
        Parameters:
            chunks_data: List of chunk data dictionaries
            
        Returns:
            List[SemanticChunk]: Created chunks
        """
        chunks = []
        for data in chunks_data:
            chunk = SemanticChunk(**data)
            chunks.append(chunk)
        
        response = await self.create_chunks(chunks)
        
        # Update UUIDs
        for i, uuid in enumerate(response.uuids):
            chunks[i].uuid = uuid
        
        return chunks
    
    async def export_chunks(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None,
        format: str = "json"
    ) -> str:
        """
        Export chunks to string.
        
        Parameters:
            metadata_filter: Filter for chunks to export
            format: Export format (json, csv, etc.)
            
        Returns:
            str: Exported data
        """
        chunks = await self.search_chunks(metadata_filter=metadata_filter, limit=1000)
        
        if format == "json":
            import json
            return json.dumps([chunk.model_dump() for chunk in chunks], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_chunks(
        self,
        data: str,
        format: str = "json"
    ) -> CreateChunksResponse:
        """
        Import chunks from string.
        
        Parameters:
            data: Data to import
            format: Import format (json, csv, etc.)
            
        Returns:
            CreateChunksResponse: Import result
        """
        if format == "json":
            import json
            chunks_data = json.loads(data)
            chunks = [SemanticChunk(**chunk_data) for chunk_data in chunks_data]
            return await self.create_chunks(chunks)
        else:
            raise ValueError(f"Unsupported import format: {format}")
    
    async def export_chunks_to_file(
        self,
        filename: str,
        metadata_filter: Optional[Dict[str, Any]] = None,
        format: str = "json"
    ) -> None:
        """
        Export chunks to file.
        
        Parameters:
            filename: Output filename
            metadata_filter: Filter for chunks to export
            format: Export format
        """
        data = await self.export_chunks(metadata_filter=metadata_filter, format=format)
        with open(filename, 'w') as f:
            f.write(data)
    
    async def import_chunks_from_file(
        self,
        filename: str,
        format: str = "json"
    ) -> CreateChunksResponse:
        """
        Import chunks from file.
        
        Parameters:
            filename: Input filename
            format: Import format
            
        Returns:
            CreateChunksResponse: Import result
        """
        with open(filename, 'r') as f:
            data = f.read()
        return await self.import_chunks(data, format=format)
    
    async def delete_chunks(self, **kwargs) -> Dict[str, Any]:
        """Delete chunks by UUIDs or metadata filter."""
        return await self.chunk_operations.delete_chunks(**kwargs)
    
    async def find_duplicate_uuids(self, **kwargs) -> Dict[str, Any]:
        """Find duplicate UUIDs in the database."""
        return await self.chunk_operations.find_duplicate_uuids(**kwargs)
    
    async def reindex_missing_embeddings(self) -> Dict[str, Any]:
        """Reindex chunks with missing embeddings."""
        return await self.chunk_operations.reindex_missing_embeddings()
    
    async def clean_faiss_orphans(self) -> Dict[str, Any]:
        """Clean orphaned FAISS entries."""
        return await self.chunk_operations.clean_faiss_orphans()
    
    async def chunk_hard_delete(
        self,
        uuids: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        ast_filter: Optional[Dict[str, Any]] = None,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Hard delete chunks from the database."""
        return await self.chunk_operations.chunk_hard_delete(
            uuids=uuids,
            metadata_filter=metadata_filter,
            ast_filter=ast_filter,
            confirm=confirm
        )
    
    async def force_delete_by_uuids(
        self,
        uuids: List[str]
    ) -> Dict[str, Any]:
        """Force delete chunks by UUIDs."""
        return await self.chunk_operations.force_delete_by_uuids(
            uuids=uuids
        )
    
    async def chunk_deferred_cleanup(self) -> Dict[str, Any]:
        """Clean up deferred chunks."""
        return await self.chunk_operations.chunk_deferred_cleanup()
    
    # Delegate embedding operations
    async def embed_text(self, text: str, **kwargs) -> List[float]:
        """Generate embedding for text."""
        return await self.embedding_operations.embed_text(text, **kwargs)
    
    async def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return await self.embedding_operations.embed_batch(texts, **kwargs)
    
    async def get_embedding_models(self) -> Dict[str, Any]:
        """Get available embedding models."""
        return await self.embedding_operations.get_embedding_models()
    
    async def create_chunk_with_embedding(self, text: str, **kwargs) -> SemanticChunk:
        """Create a chunk with automatic embedding generation."""
        return await self.embedding_operations.create_chunk_with_embedding(text, **kwargs)
    
    async def create_chunks_with_embeddings(self, texts: List[str], **kwargs) -> List[SemanticChunk]:
        """Create multiple chunks with automatic embedding generation."""
        return await self.embedding_operations.create_chunks_with_embeddings(texts, **kwargs)
    
    async def chunk_text(self, text: str, **kwargs) -> List[SemanticChunk]:
        """Chunk text using SVO chunker."""
        return await self.svo_adapter.chunk_text(text)
    
    # Health and configuration methods
    async def get_health(self) -> HealthResponse:
        """Get server health status."""
        response = await self._execute_command("health")
        # Ensure required fields are present
        if "status" not in response:
            response["status"] = "ok"
        return HealthResponse(**response)

    async def health_check(self) -> HealthResponse:
        """Check server health status."""
        return await self.get_health()
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.
        
        Returns:
            Dict[str, Any]: Server information including version, uptime, etc.
        """
        return await self._execute_command("info")
    
    async def get_help(self, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Get help information.
        
        Parameters:
            command: Optional specific command to get help for
            
        Returns:
            Dict[str, Any]: Help information
        """
        params = {}
        if command:
            params["command"] = command
        
        return await self._execute_command("help", params)
    
    async def get_config(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration value."""
        params = {}
        if path:
            params["path"] = path
        
        return await self._execute_command("config", params)
    
    async def set_config(self, path: str, value: Any) -> Dict[str, Any]:
        """Set configuration value."""
        return await self._execute_command("config", {"path": path, "value": value})
    
    async def initialize_wal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize FAISS service with WAL replay.
        
        Parameters:
            params: WAL initialization parameters
            
        Returns:
            Dict[str, Any]: Initialization result
        """
        return await self._execute_command("initialize_wal", {"params": params})
    
    async def _execute_command(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a JSON-RPC command.
        
        Parameters:
            method: Command method name
            params: Command parameters
            
        Returns:
            Dict: Response data
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        return await super().execute_command(method, params)
    
    async def close(self) -> None:
        """Close HTTP client session."""
        await super().close()
        await self.svo_adapter.close()
        await self.embedding_adapter.close()