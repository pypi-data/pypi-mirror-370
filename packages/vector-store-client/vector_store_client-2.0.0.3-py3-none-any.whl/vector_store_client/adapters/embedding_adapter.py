"""
Embedding adapter for Vector Store Client.

Provides interface to embedding service using embed_client library.
"""

import logging
from typing import List, Optional, Dict, Any
from embed_client.async_client import EmbeddingServiceAsyncClient

from ..models import SemanticChunk
from ..exceptions import VectorStoreError, ConnectionError, ServerError

logger = logging.getLogger(__name__)


class EmbeddingAdapter:
    """
    Adapter for embedding service using embed_client library.
    
    Provides interface to embedding service for generating vector embeddings
    and retrieving model information.
    """
    
    def __init__(self, base_url: str = "http://localhost", port: int = 8001):
        """
        Initialize embedding adapter.
        
        Parameters:
            base_url: Base URL of embedding service
            port: Port of embedding service
        """
        self.base_url = base_url
        self.port = port
        self.client: Optional[EmbeddingServiceAsyncClient] = None
    
    async def _create_client(self) -> None:
        """Create and initialize embedding client."""
        if not self.client:
            self.client = EmbeddingServiceAsyncClient(
                base_url=self.base_url,
                port=self.port
            )
            await self.client.__aenter__()
    
    async def _close_client(self) -> None:
        """Close embedding client."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Parameters:
            text: Text to embed
            
        Returns:
            List[float]: 384-dimensional embedding vector
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            # Call embedding service using new API
            result = await self.client.cmd("embed", {"texts": [text]})
            
            # Extract embedding using new client methods
            embeddings = self.client.extract_embeddings(result)
            
            if not embeddings or len(embeddings) == 0:
                raise ServerError("No embeddings returned")
            
            return embeddings[0]
            
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise ConnectionError(f"Failed to generate embedding: {e}")
        finally:
            await self._close_client()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Parameters:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of 384-dimensional embedding vectors
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            # Call embedding service using new API
            result = await self.client.cmd("embed", {"texts": texts})
            
            # Extract embeddings using new client methods
            embeddings = self.client.extract_embeddings(result)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise ConnectionError(f"Failed to generate batch embeddings: {e}")
        finally:
            await self._close_client()
    
    async def get_embedding_models(self) -> Dict[str, Any]:
        """
        Get available embedding models.
        
        Returns:
            Dict[str, Any]: Model information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.cmd("models")
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in models response")
                
        except Exception as e:
            logger.error(f"Models error: {e}")
            raise ConnectionError(f"Failed to get models: {e}")
        finally:
            await self._close_client()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check embedding service health.
        
        Returns:
            Dict[str, Any]: Health status
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.cmd("health")
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in health response")
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            raise ConnectionError(f"Failed to check health: {e}")
        finally:
            await self._close_client()
    
    async def get_help(self) -> Dict[str, Any]:
        """
        Get embedding service help.
        
        Returns:
            Dict[str, Any]: Help information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.cmd("help")
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in help response")
                
        except Exception as e:
            logger.error(f"Help error: {e}")
            raise ConnectionError(f"Failed to get help: {e}")
        finally:
            await self._close_client()
    
    async def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get embedding service information.
        
        Returns:
            Dict[str, Any]: Service information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            await self._create_client()
            
            result = await self.client.cmd("info")
            
            if "result" in result:
                return result["result"]
            else:
                raise ServerError("No result in info response")
                
        except Exception as e:
            logger.error(f"Info error: {e}")
            raise ConnectionError(f"Failed to get info: {e}")
        finally:
            await self._close_client()
    
    async def close(self) -> None:
        """Close the adapter and release resources."""
        await self._close_client() 