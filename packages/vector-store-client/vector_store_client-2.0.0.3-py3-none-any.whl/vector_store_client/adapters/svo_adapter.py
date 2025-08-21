"""
SVO Chunker Adapter for Vector Store Client.

This module provides an adapter for the SVO semantic chunker service,
integrating it with the Vector Store client for automatic chunking and
embedding generation.

Key features:
- Automatic text chunking with semantic analysis
- BM25 token generation
- Embedding generation integration
- Support for chunk_metadata_adapter integration

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
import logging

from svo_client import ChunkerClient
from ..models import SemanticChunk
from ..exceptions import ChunkingError, EmbeddingError

logger = logging.getLogger(__name__)


class SVOChunkerAdapter:
    """
    Adapter for SVO semantic chunker service.
    
    Provides high-level interface for chunking text using the SVO service,
    with automatic embedding generation and BM25 token support.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost",
        port: int = 8009,
        timeout: float = 60.0,
        auto_embeddings: bool = True
    ):
        """
        Initialize SVO chunker adapter.
        
        Parameters:
            base_url: Base URL of the SVO chunker service
            port: Port of the SVO service
            timeout: Request timeout in seconds
            auto_embeddings: Whether to automatically generate embeddings
        """
        self.base_url = base_url
        self.port = port
        self.timeout = timeout
        self.auto_embeddings = auto_embeddings
        self.client: Optional[ChunkerClient] = None
        self._session_active = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self) -> None:
        """Connect to the SVO chunker service."""
        if self.client is None:
            self.client = ChunkerClient(
                url=self.base_url,
                port=self.port,
                timeout=self.timeout
            )
            await self.client.__aenter__()
            self._session_active = True
            logger.info(f"Connected to SVO chunker at {self.base_url}:{self.port}")
    
    async def close(self) -> None:
        """Close connection to the SVO chunker service."""
        if self.client and self._session_active:
            await self.client.__aexit__(None, None, None)
            self.client = None
            self._session_active = False
            logger.info("Disconnected from SVO chunker")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of the SVO chunker service.
        
        Returns:
            Dict containing health status information
            
        Raises:
            ChunkingError: If health check fails
        """
        try:
            await self.connect()
            response = await self.client.health()
            return response.get("result", {})
        except Exception as e:
            raise ChunkingError(f"Health check failed: {e}")
    
    async def get_commands(self) -> Dict[str, Any]:
        """
        Get available commands from the SVO chunker service.
        
        Returns:
            Dict containing available commands and their descriptions
            
        Raises:
            ChunkingError: If command retrieval fails
        """
        try:
            await self.connect()
            return await self.client.get_commands()
        except Exception as e:
            raise ChunkingError(f"Failed to get commands: {e}")
    
    async def chunk_text(
        self,
        text: str,
        chunk_type: str = "DocBlock",
        language: Optional[str] = None,
        window: int = 3,
        **params
    ) -> List[SemanticChunk]:
        """
        Chunk text using the SVO semantic chunker service.
        
        This method automatically generates chunks with embeddings and BM25 tokens
        using the SVO chunker service.
        
        Parameters:
            text: Text to chunk
            chunk_type: Type of chunking (DocBlock, CodeBlock, Message, etc.)
            language: Language of the text (auto-detected if not provided)
            window: Window size for sentence grouping (1-10)
            **params: Additional parameters for chunking
            
        Returns:
            List of SemanticChunk objects with embeddings and BM25 tokens
            
        Raises:
            ChunkingError: If chunking fails
            EmbeddingError: If embedding generation fails
        """
        try:
            await self.connect()
            
            # Prepare chunking parameters
            chunk_params = {
                "text": text,
                "type": chunk_type,
                "window": window,
                **params
            }
            
            if language:
                chunk_params["language"] = language
            
            # Perform chunking
            logger.info(f"Chunking text with type '{chunk_type}', window={window}")
            chunks = await self.client.chunk_text(**chunk_params)
            
            # Convert to our SemanticChunk format
            semantic_chunks = []
            for chunk in chunks:
                semantic_chunk = self._parse_chunk_data(chunk)
                semantic_chunks.append(semantic_chunk)
            
            logger.info(f"Successfully chunked text into {len(semantic_chunks)} chunks")
            return semantic_chunks
            
        except Exception as e:
            raise ChunkingError(f"Text chunking failed: {e}")
    
    async def chunk_text_with_embeddings(
        self,
        text: str,
        chunk_type: str = "DocBlock",
        language: Optional[str] = None,
        window: int = 3,
        **params
    ) -> List[SemanticChunk]:
        """
        Chunk text and automatically generate embeddings.
        
        This method chunks text and then generates embeddings for each chunk
        using the embedding service.
        
        Parameters:
            text: Text to chunk
            chunk_type: Type of chunking
            language: Language of the text
            window: Window size for sentence grouping
            **params: Additional parameters
            
        Returns:
            List of SemanticChunk objects with embeddings
            
        Raises:
            ChunkingError: If chunking fails
            EmbeddingError: If embedding generation fails
        """
        try:
            # First chunk the text
            chunks = await self.chunk_text(
                text=text,
                chunk_type=chunk_type,
                language=language,
                window=window,
                **params
            )
            
            # Then generate embeddings if enabled
            if self.auto_embeddings and chunks:
                logger.info(f"Generating embeddings for {len(chunks)} chunks")
                chunks_with_embeddings = await self.client.get_embeddings(chunks)
                
                # Update our chunks with embeddings
                for i, chunk_with_embedding in enumerate(chunks_with_embeddings):
                    if hasattr(chunk_with_embedding, 'embedding') and chunk_with_embedding.embedding:
                        chunks[i].embedding = chunk_with_embedding.embedding
                
                logger.info("Successfully generated embeddings for all chunks")
            
            return chunks
            
        except Exception as e:
            if "embedding" in str(e).lower():
                raise EmbeddingError(f"Embedding generation failed: {e}")
            else:
                raise ChunkingError(f"Chunking with embeddings failed: {e}")
    
    def _parse_chunk_data(self, chunk) -> SemanticChunk:
        """
        Parse chunk data from SVO client into our SemanticChunk format.
        
        Parameters:
            chunk: Chunk data from SVO client (can be dict or SemanticChunk)
            
        Returns:
            SemanticChunk object with parsed data
        """
        try:
            # If it's already a SemanticChunk from chunk_metadata_adapter
            if hasattr(chunk, 'model_dump'):
                chunk_dict = chunk.model_dump()
            elif hasattr(chunk, 'dict'):
                chunk_dict = chunk.dict()
            elif isinstance(chunk, dict):
                chunk_dict = chunk
            else:
                raise ValueError(f"Unsupported chunk type: {type(chunk)}")
            
            # Extract metrics for BM25 tokens
            metrics = chunk_dict.get('metrics', {})
            
            # Create our SemanticChunk
            semantic_chunk = SemanticChunk(
                body=chunk_dict.get('body', ''),
                text=chunk_dict.get('text', chunk_dict.get('body', '')),
                type=chunk_dict.get('type', 'DocBlock'),
                language=chunk_dict.get('language', 'en'),
                category=chunk_dict.get('category', ''),
                title=chunk_dict.get('title', ''),
                tags=chunk_dict.get('tags', []),
                uuid=chunk_dict.get('uuid'),
                source_id=chunk_dict.get('source_id'),
                project=chunk_dict.get('project', ''),
                task_id=chunk_dict.get('task_id'),
                subtask_id=chunk_dict.get('subtask_id'),
                unit_id=chunk_dict.get('unit_id'),
                role=chunk_dict.get('role'),
                summary=chunk_dict.get('summary', ''),
                ordinal=chunk_dict.get('ordinal'),
                sha256=chunk_dict.get('sha256'),
                created_at=chunk_dict.get('created_at'),
                status=chunk_dict.get('status'),
                source_path=chunk_dict.get('source_path', ''),
                quality_score=chunk_dict.get('quality_score'),
                coverage=chunk_dict.get('coverage'),
                cohesion=chunk_dict.get('cohesion'),
                boundary_prev=chunk_dict.get('boundary_prev'),
                boundary_next=chunk_dict.get('boundary_next'),
                used_in_generation=chunk_dict.get('used_in_generation', False),
                feedback_accepted=chunk_dict.get('feedback_accepted', 0),
                feedback_rejected=chunk_dict.get('feedback_rejected', 0),
                feedback_modifications=chunk_dict.get('feedback_modifications', 0),
                start=chunk_dict.get('start'),
                end=chunk_dict.get('end'),
                year=chunk_dict.get('year'),
                is_public=chunk_dict.get('is_public', False),
                is_deleted=chunk_dict.get('is_deleted', False),
                source=chunk_dict.get('source', ''),
                block_type=chunk_dict.get('block_type'),
                chunking_version=chunk_dict.get('chunking_version', ''),
                block_id=chunk_dict.get('block_id'),
                embedding=chunk_dict.get('embedding'),
                block_index=chunk_dict.get('block_index'),
                source_lines_start=chunk_dict.get('source_lines_start'),
                source_lines_end=chunk_dict.get('source_lines_end'),
                links=chunk_dict.get('links', []),
                block_meta=chunk_dict.get('block_meta', {}),
                tags_flat=chunk_dict.get('tags_flat', ''),
                link_related=chunk_dict.get('link_related', ''),
                link_parent=chunk_dict.get('link_parent', ''),
                is_code_chunk=chunk_dict.get('is_code_chunk', False),
                metrics=metrics
            )
            
            return semantic_chunk
            
        except Exception as e:
            logger.error(f"Failed to parse chunk data: {e}")
            logger.error(f"Chunk data: {chunk}")
            raise ChunkingError(f"Failed to parse chunk data: {e}")
    
    async def get_bm25_tokens(self, text: str, **params) -> List[str]:
        """
        Get BM25 tokens for text without full chunking.
        
        Parameters:
            text: Text to tokenize
            **params: Additional parameters for tokenization
            
        Returns:
            List of BM25 tokens
            
        Raises:
            ChunkingError: If tokenization fails
        """
        try:
            # Chunk text and extract BM25 tokens from first chunk
            chunks = await self.chunk_text(text, **params)
            if chunks:
                return chunks[0].get_bm25_tokens()
            return []
        except Exception as e:
            raise ChunkingError(f"BM25 tokenization failed: {e}")
    
    async def get_regular_tokens(self, text: str, **params) -> List[str]:
        """
        Get regular tokens for text without full chunking.
        
        Parameters:
            text: Text to tokenize
            **params: Additional parameters for tokenization
            
        Returns:
            List of regular tokens
            
        Raises:
            ChunkingError: If tokenization fails
        """
        try:
            # Chunk text and extract regular tokens from first chunk
            chunks = await self.chunk_text(text, **params)
            if chunks:
                return chunks[0].get_tokens()
            return []
        except Exception as e:
            raise ChunkingError(f"Regular tokenization failed: {e}")
    
    def reconstruct_text(self, chunks: List[SemanticChunk]) -> str:
        """
        Reconstruct original text from chunks.
        
        Parameters:
            chunks: List of SemanticChunk objects
            
        Returns:
            Reconstructed text
        """
        try:
            if not chunks:
                return ""
            
            # Sort chunks by ordinal if available
            sorted_chunks = sorted(
                chunks,
                key=lambda c: c.ordinal if c.ordinal is not None else chunks.index(c)
            )
            
            # Extract text from each chunk
            text_parts = []
            for chunk in sorted_chunks:
                chunk_text = chunk.text or chunk.body
                if chunk_text:
                    text_parts.append(chunk_text)
            
            return ''.join(text_parts)
            
        except Exception as e:
            logger.error(f"Failed to reconstruct text: {e}")
            return "" 