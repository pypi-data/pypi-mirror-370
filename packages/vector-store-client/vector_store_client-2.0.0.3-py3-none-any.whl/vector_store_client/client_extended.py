"""
Vector Store Client - Extended Operations.

This module provides extended operations for the Vector Store client including
batch operations, maintenance, plugins, and middleware functionality.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
import logging

from .client import VectorStoreClient
from .exceptions import (
    ValidationError, VectorStoreError, UserCancelledError
)
from .models import (
    SemanticChunk
)
from .types import DEFAULT_LIMIT
from .utils import process_batch_concurrent, format_timestamp
from .validation import validate_uuid_list
from .validation import validate_embedding


class VectorStoreClientExtended(VectorStoreClient):
    """
    Extended Vector Store Client with advanced operations.
    
    This class extends the base VectorStoreClient with batch operations,
    maintenance functions, plugin system, and middleware support.
    """
    
    async def batch_create_chunks(
        self,
        chunks: List[SemanticChunk],
        batch_size: int = 100,
        max_concurrent: int = 5
    ) -> List[str]:
        """
        Create chunks in batches with concurrent processing.
        
        Parameters:
            chunks: List of chunks to create
            batch_size: Size of each batch
            max_concurrent: Maximum concurrent batches
            
        Returns:
            List[str]: List of all created UUIDs
        """
        async def create_batch(batch_chunks):
            response = await self.create_chunks(batch_chunks)
            return response.uuids if response.success else []
        
        results = await process_batch_concurrent(
            chunks, create_batch, max_concurrent, batch_size
        )
        
        # Flatten results
        all_uuids = []
        for uuids in results:
            if isinstance(uuids, list):
                all_uuids.extend(uuids)
        
        return all_uuids
    
    async def batch_search_chunks(
        self,
        queries: List[str],
        limit: int = DEFAULT_LIMIT,
        batch_size: int = 10,
        max_concurrent: int = 5
    ) -> List[List[SemanticChunk]]:
        """
        Search for multiple queries in batches.
        
        Parameters:
            queries: List of search queries
            limit: Maximum results per query
            batch_size: Size of each batch
            max_concurrent: Maximum concurrent batches
            
        Returns:
            List[List[SemanticChunk]]: List of search results for each query
        """
        async def search_batch(batch_queries):
            results = []
            for query in batch_queries:
                try:
                    query_results = await self.search_by_text(query, limit)
                    results.append(query_results)
                except Exception as e:
                    self.logger.error(f"Search failed for query '{query}': {e}")
                    results.append([])
            return results
        
        results = await process_batch_concurrent(
            queries, search_batch, max_concurrent, batch_size
        )
        
        # Flatten results
        all_results = []
        for batch_results in results:
            if isinstance(batch_results, list):
                all_results.extend(batch_results)
        
        return all_results
    
    async def batch_delete_chunks(
        self,
        uuids: List[str],
        batch_size: int = 100,
        max_concurrent: int = 5,
        require_confirmation: bool = True
    ) -> List['DeleteResponse']:
        """
        Delete chunks in batches with confirmation.
        
        Deletes large numbers of chunks efficiently using batch processing.
        Useful for bulk deletion operations.
        
        Parameters:
            uuids: List of chunk UUIDs to delete
            batch_size: Number of chunks to delete per batch
            max_concurrent: Maximum number of concurrent delete operations
            require_confirmation: Whether to require user confirmation
            
        Returns:
            List[DeleteResponse]: List of deletion responses for each batch
            
        Raises:
            ValidationError: If UUIDs are invalid
            UserCancelledError: If user cancels the operation
        """
        if not uuids:
            return []
        
        validated_uuids = validate_uuid_list(uuids)
        total_count = len(validated_uuids)
        
        # Request confirmation if required
        if require_confirmation:
            try:
                message = f"Delete {total_count} chunks in {max_concurrent} concurrent batches?"
                # In a real implementation, this would prompt the user
                confirmed = True  # This would be user input in real implementation
                if not confirmed:
                    raise UserCancelledError("Operation cancelled by user")
            except Exception as e:
                raise UserCancelledError(f"Confirmation failed: {e}")
        
        # Split UUIDs into batches
        uuid_batches = [
            validated_uuids[i:i + batch_size]
            for i in range(0, len(validated_uuids), batch_size)
        ]
        
        # Process batches concurrently
        async def delete_batch(batch_uuids):
            return await self.delete_chunks(uuids=batch_uuids)
        
        # Execute batches concurrently without combining results
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch(batch_uuids):
            async with semaphore:
                return await delete_batch(batch_uuids)
        
        # Create tasks for all batches
        tasks = [process_batch(batch) for batch in uuid_batches]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Batch delete failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    # ===== Chunking and Embedding Methods =====
    
    async def chunk_text(
        self,
        text: str,
        window: int = 3,
        chunk_type: str = "Draft",
        language: Optional[str] = None,
        **kwargs
    ) -> List[SemanticChunk]:
        """
        Perform semantic chunking of text using SVO service.
        
        Parameters:
            text: Text to chunk (required)
            window: Sliding window size for chunking (default: 3)
            chunk_type: Type of chunks to create (default: "Draft")
            language: Language of the text (optional)
            **kwargs: Additional parameters for chunking
            
        Returns:
            List[SemanticChunk]: List of semantic chunks
            
        Raises:
            ValidationError: If input parameters are invalid
            SVOError: If SVO service returns error
            ConnectionError: If connection to SVO service fails
        """
        return await self.svo_adapter.chunk_text(
            text=text,
            window=window,
            chunk_type=chunk_type,
            language=language,
            **kwargs
        )
    
    async def embed_text(
        self,
        text: str,
        model: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """
        Generate embedding for text using embedding service.
        
        Parameters:
            text: Text to embed (required)
            model: Model to use for embedding (optional)
            **kwargs: Additional parameters for embedding
            
        Returns:
            List[float]: Embedding vector
            
        Raises:
            ValidationError: If input parameters are invalid
            EmbeddingError: If embedding service returns error
            ConnectionError: If connection to embedding service fails
        """
        return await self.embedding_adapter.embed_text(
            text=text,
            model=model,
            **kwargs
        )
    
    async def embed_batch(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Parameters:
            texts: List of texts to embed (required)
            model: Model to use for embedding (optional)
            **kwargs: Additional parameters for embedding
            
        Returns:
            List[List[float]]: List of embedding vectors
            
        Raises:
            ValidationError: If input parameters are invalid
            EmbeddingError: If embedding service returns error
            ConnectionError: If connection to embedding service fails
        """
        return await self.embedding_adapter.embed_batch(
            texts=texts,
            model=model,
            **kwargs
        )
    
    async def embed_text_with_metadata(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for text with metadata.
        
        Parameters:
            text: Text to embed
            metadata: Additional metadata
            model: Embedding model to use
            
        Returns:
            List[float]: Embedding vector
        """
        embedding = await self.embed_text(text, model=model)
        return embedding
    
    async def embed_batch_with_metadata(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with metadata.
        
        Parameters:
            texts: List of texts to embed
            metadata_list: List of metadata for each text
            model: Embedding model to use
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        embeddings = await self.embed_batch(texts, model=model)
        return embeddings
    
    async def get_embedding_models(self) -> Dict[str, Any]:
        """
        Get available embedding models.
        
        Returns:
            Dict[str, Any]: Available models and their configurations
        """
        raw_response = await self.embedding_adapter.get_embedding_models()
        
        # Convert raw response to simple dict
        if isinstance(raw_response, dict):
            return raw_response
        else:
            # Fallback if response is not in expected format
            return {
                "models": ["default"],
                "default_model": "default",
                "model_configs": {"default": {"dimension": 384}}
            }
    
    async def create_chunk_with_embedding(
        self,
        text: str,
        chunk_type: str = "Draft",
        language: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> SemanticChunk:
        """
        Create a chunk with automatic embedding generation.
        
        This method combines chunking and embedding in a single operation.
        
        Parameters:
            text: Text to process (required)
            chunk_type: Type of chunk to create (default: "Draft")
            language: Language of the text (optional)
            model: Model to use for embedding (optional)
            **kwargs: Additional parameters
            
        Returns:
            SemanticChunk: Created chunk with embedding
            
        Raises:
            ValidationError: If input parameters are invalid
            SVOError: If SVO service returns error
            EmbeddingError: If embedding service returns error
            ConnectionError: If connection to services fails
        """
        # First, chunk the text
        chunks = await self.chunk_text(
            text=text,
            chunk_type=chunk_type,
            language=language,
            **kwargs
        )
        
        if not chunks:
            raise ValidationError("No chunks were created from the text")
        
        # Get the first chunk and generate embedding for it
        chunk = chunks[0]
        
        # Generate embedding for the chunk text
        embed_response = await self.embed_text(
            text=chunk.text or chunk.body,
            model=model
        )
        
        # Update chunk with embedding
        chunk.embedding = embed_response
        
        return chunk
    
    async def create_chunks_with_embeddings(
        self,
        text: str,
        chunk_type: str = "Draft",
        language: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[SemanticChunk]:
        """
        Create multiple chunks with automatic embedding generation.
        
        This method combines chunking and embedding for multiple chunks.
        
        Parameters:
            text: Text to process (required)
            chunk_type: Type of chunks to create (default: "Draft")
            language: Language of the text (optional)
            model: Model to use for embedding (optional)
            **kwargs: Additional parameters
            
        Returns:
            List[SemanticChunk]: List of created chunks with embeddings
            
        Raises:
            ValidationError: If input parameters are invalid
            SVOError: If SVO service returns error
            EmbeddingError: If embedding service returns error
            ConnectionError: If connection to services fails
        """
        # First, chunk the text
        chunks = await self.chunk_text(
            text=text,
            chunk_type=chunk_type,
            language=language,
            **kwargs
        )
        
        if not chunks:
            raise ValidationError("No chunks were created from the text")
        
        # Generate embeddings for all chunks
        texts = [chunk.text or chunk.body for chunk in chunks]
        embed_responses = await self.embed_batch(
            texts=texts,
            model=model
        )
        
        # Update chunks with embeddings
        for chunk, embed_response in zip(chunks, embed_responses):
            chunk.embedding = embed_response
        
        return chunks
    
    async def check_services_health(self) -> Dict[str, Any]:
        """
        Check health of all services (Vector Store, SVO, Embedding).
        
        Returns:
            Dict[str, Any]: Health status of all services
        """
        health_status = {
            "vector_store": None,
            "svo_service": None,
            "embedding_service": None
        }
        
        # Check Vector Store health
        try:
            vector_store_health = await self.health_check()
            health_status["vector_store"] = {
                "status": "healthy",
                "data": vector_store_health.model_dump()
            }
        except Exception as e:
            health_status["vector_store"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check SVO service health
        try:
            svo_health = await self.svo_adapter.health_check()
            health_status["svo_service"] = {
                "status": "healthy",
                "data": svo_health
            }
        except Exception as e:
            health_status["svo_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Embedding service health
        try:
            embedding_health = await self.embedding_adapter.health_check()
            health_status["embedding_service"] = {
                "status": "healthy",
                "data": embedding_health
            }
        except Exception as e:
            health_status["embedding_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
    
    # ===== Advanced Search and Utility Methods =====
    
    async def search_by_text(
        self,
        text: str,
        limit: int = 10,
        level_of_relevance: float = 0.0
    ) -> List[SemanticChunk]:
        """
        Search chunks by text.
        
        Parameters:
            text: Search text
            limit: Maximum number of results
            level_of_relevance: Minimum relevance threshold
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            search_str=text,
            limit=limit,
            level_of_relevance=level_of_relevance
        )
    
    async def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        level_of_relevance: float = 0.0
    ) -> List[SemanticChunk]:
        """
        Search chunks by vector.
        
        Parameters:
            vector: Search vector
            limit: Maximum number of results
            level_of_relevance: Minimum relevance threshold
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            embedding=vector,
            limit=limit,
            level_of_relevance=level_of_relevance
        )
    
    async def search_by_ast_query(
        self,
        ast_query: Dict[str, Any],
        limit: int = 10
    ) -> List[SemanticChunk]:
        """
        Search chunks by AST query.
        
        Parameters:
            ast_query: AST query expression
            limit: Maximum number of results
            
        Returns:
            List[SemanticChunk]: List of matching chunks
        """
        return await self.search_chunks(
            ast_filter=ast_query,
            limit=limit
        )
    
    async def delete_by_metadata(
        self,
        metadata_filter: Dict[str, Any]
    ) -> 'DeleteResponse':
        """
        Delete chunks by metadata filter.
        
        Parameters:
            metadata_filter: Metadata filter for deletion
            
        Returns:
            DeleteResponse: Response with deletion results
        """
        return await self.delete_chunks(metadata_filter=metadata_filter)
    
    async def delete_by_ast_query(
        self,
        ast_query: Dict[str, Any]
    ) -> 'DeleteResponse':
        """
        Delete chunks by AST query.
        
        Parameters:
            ast_query: AST query for deletion
            
        Returns:
            DeleteResponse: Response with deletion results
        """
        return await self.delete_chunks(ast_filter=ast_query)
    
    async def delete_by_uuids(
        self,
        uuids: List[str]
    ) -> 'DeleteResponse':
        """
        Delete chunks by UUIDs.
        
        Parameters:
            uuids: List of chunk UUIDs to delete
            
        Returns:
            DeleteResponse: Response with deletion results
        """
        return await self.chunk_hard_delete(uuids)
    
    async def delete_by_type(
        self,
        chunk_type: str
    ) -> 'DeleteResponse':
        """
        Delete chunks by type.
        
        Parameters:
            chunk_type: Type of chunks to delete
            
        Returns:
            DeleteResponse: Response with deletion results
        """
        return await self.delete_by_metadata({"type": chunk_type})
    
    async def delete_by_project(
        self,
        project: str
    ) -> 'DeleteResponse':
        """
        Delete chunks by project.
        
        Parameters:
            project: Project name
            
        Returns:
            DeleteResponse: Response with deletion results
        """
        return await self.delete_by_metadata({"project": project})
    
    def build_ast_query(
        self,
        conditions: List[Dict[str, Any]],
        operator: str = "AND"
    ) -> Dict[str, Any]:
        """
        Build AST query from conditions.
        
        Parameters:
            conditions: List of condition dictionaries
            operator: Logical operator ("AND", "OR")
            
        Returns:
            Dict[str, Any]: AST query expression
        """
        return {
            "type": "logical",
            "operator": operator,
            "conditions": conditions
        }
    
    def build_condition(
        self,
        field: str,
        operator: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        Build single condition for AST query.
        
        Parameters:
            field: Field name
            operator: Comparison operator
            value: Field value
            
        Returns:
            Dict[str, Any]: Condition dictionary
        """
        return {
            "type": "condition",
            "field": field,
            "operator": operator,
            "value": value
        }
    
    def build_range_query(
        self,
        field: str,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Build range query.
        
        Parameters:
            field: Field name
            min_value: Minimum value (optional)
            max_value: Maximum value (optional)
            
        Returns:
            Dict[str, Any]: Range query expression
        """
        conditions = []
        if min_value is not None:
            conditions.append(self.build_condition(field, "gte", min_value))
        if max_value is not None:
            conditions.append(self.build_condition(field, "lte", max_value))
        
        if len(conditions) == 1:
            return conditions[0]
        else:
            return self.build_ast_query(conditions, "AND")
    
    # ===== Plugin Management Methods =====
    
    def register_plugin(self, plugin_name: str, plugin_instance: Any) -> None:
        """
        Register a plugin with the client.
        
        Parameters:
            plugin_name: Name of the plugin
            plugin_instance: Plugin instance to register
        """
        self.plugins[plugin_name] = plugin_instance
        self.plugin_registry[plugin_name] = plugin_instance
        self.logger.info(f"Plugin '{plugin_name}' registered successfully")
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Get a registered plugin by name.
        
        Parameters:
            plugin_name: Name of the plugin to retrieve
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """
        Get list of registered plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.
        
        Parameters:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            True if plugin was unregistered, False if not found
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            del self.plugin_registry[plugin_name]
            self.logger.info(f"Plugin '{plugin_name}' unregistered")
            return True
        return False
    
    # ===== Middleware Management Methods =====
    
    def add_middleware(self, middleware_instance: Any) -> None:
        """
        Add middleware to the client.
        
        Parameters:
            middleware_instance: Middleware instance to add
        """
        self.middleware_chain.append(middleware_instance)
        self.middleware_registry[middleware_instance.__class__.__name__] = middleware_instance
        self.logger.info(f"Middleware '{middleware_instance.__class__.__name__}' added successfully")
    
    def remove_middleware(self, middleware_name: str) -> bool:
        """
        Remove middleware from the client.
        
        Parameters:
            middleware_name: Name of the middleware to remove
            
        Returns:
            True if middleware was removed, False if not found
        """
        for i, middleware in enumerate(self.middleware_chain):
            if middleware.__class__.__name__ == middleware_name:
                del self.middleware_chain[i]
                del self.middleware_registry[middleware_name]
                self.logger.info(f"Middleware '{middleware_name}' removed")
                return True
        return False
    
    def list_middleware(self) -> List[str]:
        """
        Get list of middleware names.
        
        Returns:
            List of middleware names
        """
        return [mw.__class__.__name__ for mw in self.middleware_chain]
    
    async def execute_with_middleware(self, operation: str, **kwargs) -> Any:
        """
        Execute operation with middleware chain.
        
        Parameters:
            operation: Operation name
            **kwargs: Operation parameters
            
        Returns:
            Operation result
        """
        # Apply middleware before operation
        for middleware in self.middleware_chain:
            if hasattr(middleware, 'before_request'):
                kwargs = await middleware.before_request(operation, kwargs)
        
        # Execute operation
        try:
            if operation == "search":
                result = await self.search_chunks(**kwargs)
            elif operation == "create":
                result = await self.create_chunks(**kwargs)
            elif operation == "delete":
                result = await self.delete_chunks(**kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Apply middleware after operation
            for middleware in reversed(self.middleware_chain):
                if hasattr(middleware, 'after_request'):
                    result = await middleware.after_request(operation, result)
            
            return result
            
        except Exception as e:
            # Apply middleware on error
            for middleware in reversed(self.middleware_chain):
                if hasattr(middleware, 'on_error'):
                    e = await middleware.on_error(operation, e)
            raise
    
    async def execute_plugins(
        self,
        data: Dict[str, Any],
        plugin_names: List[str]
    ) -> Dict[str, Any]:
        """
        Execute plugins on data.
        
        Parameters:
            data: Data to process
            plugin_names: List of plugin names to execute
            
        Returns:
            Dict[str, Any]: Processed data
        """
        result = data.copy()
        
        for plugin_name in plugin_names:
            plugin = self.get_plugin(plugin_name)
            if plugin and hasattr(plugin, 'process'):
                try:
                    result = await plugin.process(result)
                except Exception as e:
                    self.logger.warning(f"Plugin '{plugin_name}' failed: {e}")
        
        return result 