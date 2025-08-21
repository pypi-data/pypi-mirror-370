"""
Base operations for Vector Store Client.

This module provides the base class for all operation modules.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from ..exceptions import (
    VectorStoreError, ConnectionError, ValidationError, ServerError
)


class BaseOperations:
    """
    Base class for all operation modules.
    
    Provides common functionality and error handling for all operations.
    """
    
    def __init__(self, client):
        """
        Initialize base operations.
        
        Parameters:
            client: VectorStoreClient instance
        """
        self.client = client
    
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
        return await self.client._execute_command(method, params) 