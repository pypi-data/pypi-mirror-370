"""
Base adapter for external service integration.

This module provides the base adapter class that defines the common
interface and functionality for all external service adapters.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from ..exceptions import VectorStoreError, ConnectionError


class BaseAdapter(ABC):
    """
    Base adapter for external service integration.
    
    Provides common functionality for all service adapters including
    connection management, error handling, and retry logic.
    
    Attributes:
        base_url (str): Base URL of the external service
        timeout (float): Request timeout in seconds
        _client: Underlying service client
        logger: Logger instance for this adapter
    """
    
    def __init__(
        self, 
        base_url: str, 
        timeout: float = 30.0
    ) -> None:
        """
        Initialize base adapter.
        
        Parameters:
            base_url: Base URL of the external service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def _create_client(self) -> None:
        """
        Create the underlying service client.
        
        This method must be implemented by subclasses to create
        the appropriate client for the specific service.
        """
        pass
    
    @abstractmethod
    async def _close_client(self) -> None:
        """
        Close the underlying service client.
        
        This method must be implemented by subclasses to properly
        close the service client and release resources.
        """
        pass
    
    async def __aenter__(self) -> "BaseAdapter":
        """Async context manager entry."""
        await self._create_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self._close_client()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Dict[str, Any]: Health check response from service
            
        Raises:
            VectorStoreError: If health check fails
        """
        if not self._client:
            raise VectorStoreError("Client not initialized")
        
        try:
            return await self._client.health()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            raise ConnectionError(f"Health check failed: {e}")
    
    async def get_help(self, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Get help information from service.
        
        Parameters:
            command: Optional command name to get help for
            
        Returns:
            Dict[str, Any]: Help information from service
            
        Raises:
            VectorStoreError: If help request fails
        """
        if not self._client:
            raise VectorStoreError("Client not initialized")
        
        try:
            return await self._client.get_help(command)
        except Exception as e:
            self.logger.error(f"Help request failed: {e}")
            raise ConnectionError(f"Help request failed: {e}")
    
    async def is_available(self) -> bool:
        """
        Check if service is available.
        
        Returns:
            bool: True if service is available, False otherwise
        """
        try:
            await self.health_check()
            return True
        except Exception:
            return False
    
    async def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information.
        
        Returns:
            Dict[str, Any]: Service information including version, status, etc.
        """
        try:
            health = await self.health_check()
            help_info = await self.get_help()
            
            return {
                "service_type": self.__class__.__name__,
                "base_url": self.base_url,
                "timeout": self.timeout,
                "health": health,
                "help": help_info
            }
        except Exception as e:
            self.logger.error(f"Failed to get service info: {e}")
            return {
                "service_type": self.__class__.__name__,
                "base_url": self.base_url,
                "timeout": self.timeout,
                "error": str(e)
            } 