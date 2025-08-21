"""
Vector Store Base Client.

This module provides the base client class that handles core JSON-RPC
communication with the Vector Store server.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union

import httpx

from .exceptions import (
    ConnectionError, JsonRpcError, ServerError, ValidationError
)
from .types import (
    DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY,
    DEFAULT_BACKOFF_FACTOR, DEFAULT_HEADERS, JSON_RPC_VERSION
)
from .utils import retry_with_backoff
from .validation import validate_url, validate_timeout


class BaseVectorStoreClient:
    """
    Base client for Vector Store API communication.
    
    This class provides the foundational JSON-RPC communication layer
    for interacting with the Vector Store server. It handles request
    preparation, execution, response parsing, and error handling.
    
    Attributes:
        base_url (str): Base URL of the Vector Store server
        timeout (float): Request timeout in seconds
        session (httpx.AsyncClient): HTTP client session
        logger (logging.Logger): Logger instance
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[httpx.AsyncClient] = None
    ) -> None:
        """
        Initialize base Vector Store client.
        
        Parameters:
            base_url: Base URL of the Vector Store server
            timeout: Request timeout in seconds
            session: Optional HTTP client session
        """
        self.base_url = validate_url(base_url)
        self.timeout = validate_timeout(timeout)
        self.session = session or httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self) -> "BaseVectorStoreClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close HTTP client session."""
        if self.session and not self.session.is_closed:
            await self.session.aclose()
    
    def _prepare_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Union[str, int, None] = 1
    ) -> Dict[str, Any]:
        """
        Prepare JSON-RPC request.
        
        Parameters:
            method: JSON-RPC method name
            params: Method parameters
            request_id: Request identifier
            
        Returns:
            Dict: Prepared request data
        """
        if not method or not isinstance(method, str):
            raise ValidationError("Method must be a non-empty string")
        
        request_data = {
            "jsonrpc": JSON_RPC_VERSION,
            "method": method,
            "id": request_id
        }
        
        if params is not None:
            request_data["params"] = params
        
        return request_data
    
    async def _execute_request(
        self,
        request: Dict[str, Any],
        max_retries: int = DEFAULT_MAX_RETRIES
    ) -> Dict[str, Any]:
        """
        Execute JSON-RPC request with retry logic.
        
        Parameters:
            request: JSON-RPC request to execute
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            ConnectionError: If connection fails
            JsonRpcError: If JSON-RPC error occurs
            ServerError: If server returns error
        """
        async def _make_request():
            try:
                # Prepare request data
                request_data = request
                
                # Make HTTP request
                response = await self.session.post(
                    f"{self.base_url}/cmd",
                    json=request_data,
                    headers=DEFAULT_HEADERS
                )
                
                # Check HTTP status
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e:
                    raise JsonRpcError(f"Invalid JSON response: {e}")
                
                # Validate response structure
                if not isinstance(response_data, dict):
                    raise JsonRpcError("Response must be a dictionary")
                
                # Check for JSON-RPC error
                if "error" in response_data:
                    error_info = response_data["error"]
                    error_message = error_info.get("message", "Unknown error")
                    error_code = error_info.get("code", -1)
                    raise JsonRpcError(
                        f"JSON-RPC error {error_code}: {error_message}",
                        code=error_code,
                        method=request["method"],
                        request_id=request["id"]
                    )
                
                # Return result
                return response_data.get("result", {})
                
            except httpx.RequestError as e:
                raise ConnectionError(
                    f"Connection failed: {e}",
                    url=self.base_url,
                    timeout=self.timeout
                )
            except httpx.HTTPStatusError as e:
                raise ServerError(
                    f"HTTP error {e.response.status_code}: {e}",
                    status_code=e.response.status_code,
                    response_data={"status_code": e.response.status_code},
                    request_data=request
                )
        
        # Execute with retry logic
        return await retry_with_backoff(
            _make_request,
            max_retries=max_retries,
            base_delay=DEFAULT_RETRY_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            exceptions=(ConnectionError, ServerError)
        )
    
    async def execute_command(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        request_id: Union[str, int, None] = 1,
        max_retries: int = DEFAULT_MAX_RETRIES
    ) -> Dict[str, Any]:
        """
        Execute JSON-RPC command.
        
        Parameters:
            method: JSON-RPC method name
            params: Method parameters
            request_id: Request identifier
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            ValidationError: If parameters are invalid
            ConnectionError: If connection fails
            JsonRpcError: If JSON-RPC error occurs
            ServerError: If server returns error
        """
        # Prepare request - ensure params is always a dict
        if params is None:
            params = {}
        request = self._prepare_request(method, params, request_id)
        
        # Execute request
        try:
            result = await self._execute_request(request, max_retries)
            return result
        except Exception as e:
            self.logger.error(f"Command {method} failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check server health status.
        
        Returns:
            Dict[str, Any]: Health status information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        return await self.execute_command("health", {})
    
    async def get_help(self, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Get help information.
        
        Parameters:
            command: Optional command name for specific help
            
        Returns:
            Dict[str, Any]: Help information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        params = {}
        if command:
            params["command"] = command
        
        return await self.execute_command("help", params if params else {})
    
    async def get_config(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get server configuration.
        
        Parameters:
            path: Optional configuration path
            
        Returns:
            Dict[str, Any]: Configuration data
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        params = {}
        if path:
            params["path"] = path
        
        return await self.execute_command("config", params if params else {})
    
    async def is_connected(self) -> bool:
        """
        Check if client is connected to server.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            await self.health_check()
            return True
        except Exception:
            return False
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.
        
        Returns:
            Dict[str, Any]: Server information
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        return await self.execute_command("config")
    
    async def ping(self) -> bool:
        """
        Ping server to check connectivity.
        
        Returns:
            bool: True if server responds, False otherwise
        """
        try:
            await self.health_check()
            return True
        except Exception:
            return False
    
    async def get_openapi_schema(self) -> Dict[str, Any]:
        """
        Get OpenAPI schema from server.
        
        Returns:
            Dict[str, Any]: OpenAPI schema
            
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns error
        """
        try:
            # Try to get schema via HTTP GET request to /openapi.json
            response = await self.session.get(f"{self.base_url}/openapi.json")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Failed to fetch OpenAPI schema: {e}",
                url=f"{self.base_url}/openapi.json",
                timeout=self.timeout
            )
        except httpx.HTTPStatusError as e:
            raise ServerError(
                f"HTTP error {e.response.status_code} fetching OpenAPI schema: {e}",
                status_code=e.response.status_code,
                response_data={"status_code": e.response.status_code}
            )
        except json.JSONDecodeError as e:
            raise ServerError(
                f"Invalid JSON in OpenAPI schema response: {e}",
                status_code=200,
                response_data={"error": "Invalid JSON"}
            ) 