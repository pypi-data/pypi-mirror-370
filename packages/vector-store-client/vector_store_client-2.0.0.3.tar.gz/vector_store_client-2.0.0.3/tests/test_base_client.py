"""
Tests for vector_store_client.base_client module.

This module tests the BaseVectorStoreClient class which provides
core JSON-RPC communication with the Vector Store server.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any

import httpx

from vector_store_client.base_client import BaseVectorStoreClient
from vector_store_client.exceptions import (
    ConnectionError, JsonRpcError, ServerError, ValidationError
)
from vector_store_client.models import JsonRpcRequest, JsonRpcResponse
from vector_store_client.types import (
    DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY,
    DEFAULT_BACKOFF_FACTOR, DEFAULT_HEADERS, JSON_RPC_VERSION
)


class TestBaseVectorStoreClient:
    """Test BaseVectorStoreClient class."""
    
    @pytest.fixture
    def client(self):
        """Create test client instance."""
        return BaseVectorStoreClient("http://localhost:8007")
    
    @pytest.fixture
    def mock_session(self):
        """Create mock HTTP session."""
        session = AsyncMock(spec=httpx.AsyncClient)
        session.is_closed = False
        return session
    
    @pytest.fixture
    def client_with_mock_session(self, mock_session):
        """Create client with mock session."""
        return BaseVectorStoreClient(
            "http://localhost:8007",
            session=mock_session
        )
    
    def test_init(self, client):
        """Test client initialization."""
        assert client.base_url == "http://localhost:8007"
        assert client.timeout == DEFAULT_TIMEOUT
        assert client.session is not None
        assert client.logger is not None
    
    def test_init_with_session(self, mock_session):
        """Test client initialization with custom session."""
        client = BaseVectorStoreClient(
            "http://localhost:8007",
            session=mock_session
        )
        assert client.session == mock_session
    
    def test_init_invalid_url(self):
        """Test initialization with invalid URL."""
        with pytest.raises(ValidationError, match="Invalid URL"):
            BaseVectorStoreClient("invalid-url")
    
    def test_init_invalid_timeout(self):
        """Test initialization with invalid timeout."""
        with pytest.raises(ValidationError, match="Timeout must be"):
            BaseVectorStoreClient("http://localhost:8007", timeout=-1)
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager."""
        async with client as ctx_client:
            assert ctx_client == client
            assert ctx_client.session is not None
    
    @pytest.mark.asyncio
    async def test_close(self, client_with_mock_session, mock_session):
        """Test closing client session."""
        await client_with_mock_session.close()
        mock_session.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_already_closed(self, client_with_mock_session, mock_session):
        """Test closing already closed session."""
        mock_session.is_closed = True
        await client_with_mock_session.close()
        mock_session.aclose.assert_not_called()
    
    def test_prepare_request_basic(self, client):
        """Test preparing basic request."""
        request = client._prepare_request("test_method")
        
        assert request.jsonrpc == JSON_RPC_VERSION
        assert request.method == "test_method"
        assert request.id == 1
        assert request.params is None
    
    def test_prepare_request_with_params(self, client):
        """Test preparing request with parameters."""
        params = {"key": "value"}
        request = client._prepare_request("test_method", params)
        
        assert request.params == params
    
    def test_prepare_request_with_custom_id(self, client):
        """Test preparing request with custom ID."""
        request = client._prepare_request("test_method", request_id="custom-id")
        
        assert request.id == "custom-id"
    
    def test_prepare_request_empty_method(self, client):
        """Test preparing request with empty method."""
        with pytest.raises(ValidationError, match="Method must be a non-empty string"):
            client._prepare_request("")
    
    def test_prepare_request_none_method(self, client):
        """Test preparing request with None method."""
        with pytest.raises(ValidationError, match="Method must be a non-empty string"):
            client._prepare_request(None)
    
    def test_prepare_request_invalid_params_type(self, client):
        """Test preparing request with invalid params type."""
        with pytest.raises(ValidationError, match="Parameters must be a dictionary"):
            client._prepare_request("test_method", params="invalid")
    
    def test_prepare_request_strips_method(self, client):
        """Test that method is stripped of whitespace."""
        request = client._prepare_request("  test_method  ")
        
        assert request.method == "test_method"
    
    @pytest.mark.asyncio
    async def test_execute_request_success(self, client_with_mock_session, mock_session):
        """Test successful request execution."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        result = await client_with_mock_session._execute_request(request)
        
        assert result == {"status": "success"}
        mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_request_json_error(self, client_with_mock_session, mock_session):
        """Test request execution with JSON decode error."""
        # Mock response with JSON error
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(JsonRpcError, match="Invalid JSON response"):
            await client_with_mock_session._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_invalid_response_type(self, client_with_mock_session, mock_session):
        """Test request execution with invalid response type."""
        # Mock response with non-dict result
        mock_response = Mock()
        mock_response.json.return_value = "not a dict"
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(JsonRpcError, match="Response must be a dictionary"):
            await client_with_mock_session._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_json_rpc_error(self, client_with_mock_session, mock_session):
        """Test request execution with JSON-RPC error."""
        # Mock response with JSON-RPC error
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(JsonRpcError, match="JSON-RPC error -32601"):
            await client_with_mock_session._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_connection_error(self, client_with_mock_session, mock_session):
        """Test request execution with connection error."""
        # Mock connection error
        mock_session.post.side_effect = httpx.RequestError("Connection failed")
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(ConnectionError, match="Connection failed"):
            await client_with_mock_session._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_http_error(self, client_with_mock_session, mock_session):
        """Test request execution with HTTP error."""
        # Mock HTTP error
        mock_session.post.side_effect = httpx.HTTPStatusError(
            "Internal Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(ServerError, match="HTTP error 500"):
            await client_with_mock_session._execute_request(request, max_retries=1)
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self, client_with_mock_session, mock_session):
        """Test successful command execution."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute command
        result = await client_with_mock_session.execute_command("test_method")
        
        assert result == {"status": "success"}
    
    @pytest.mark.asyncio
    async def test_execute_command_with_params(self, client_with_mock_session, mock_session):
        """Test command execution with parameters."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute command with params
        params = {"key": "value"}
        result = await client_with_mock_session.execute_command("test_method", params)
        
        assert result == {"status": "success"}
        # Verify params were passed
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["params"] == params
    
    @pytest.mark.asyncio
    async def test_execute_command_with_custom_id(self, client_with_mock_session, mock_session):
        """Test command execution with custom request ID."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute command with custom ID
        result = await client_with_mock_session.execute_command(
            "test_method",
            request_id="custom-id"
        )
        
        assert result == {"status": "success"}
        # Verify custom ID was used
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["id"] == "custom-id"
    
    @pytest.mark.asyncio
    async def test_execute_command_error_logging(self, client_with_mock_session, mock_session):
        """Test command execution error logging."""
        # Mock connection error
        mock_session.post.side_effect = httpx.RequestError("Connection failed")
        
        # Execute command
        with pytest.raises(ConnectionError):
            await client_with_mock_session.execute_command("test_method")
    
    @pytest.mark.asyncio
    async def test_health_check(self, client_with_mock_session, mock_session):
        """Test health check command."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "healthy"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute health check
        result = await client_with_mock_session.health_check()
        
        assert result == {"status": "healthy"}
        # Verify health command was called
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "health"
    
    @pytest.mark.asyncio
    async def test_get_help_no_command(self, client_with_mock_session, mock_session):
        """Test get help without specific command."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"commands": ["help", "health"]}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get help
        result = await client_with_mock_session.get_help()
        
        assert result == {"commands": ["help", "health"]}
        # Verify help command was called without params
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "help"
        assert request_data.get("params") == {}
    
    @pytest.mark.asyncio
    async def test_get_help_with_command(self, client_with_mock_session, mock_session):
        """Test get help with specific command."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"description": "Health check"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get help with command
        result = await client_with_mock_session.get_help("health")
        
        assert result == {"description": "Health check"}
        # Verify help command was called with params
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "help"
        assert request_data["params"] == {"command": "health"}
    
    @pytest.mark.asyncio
    async def test_get_config_no_path(self, client_with_mock_session, mock_session):
        """Test get config without specific path."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"timeout": 30}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get config
        result = await client_with_mock_session.get_config()
        
        assert result == {"timeout": 30}
        # Verify config command was called without params
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "config"
        assert request_data.get("params") == {}
    
    @pytest.mark.asyncio
    async def test_get_config_with_path(self, client_with_mock_session, mock_session):
        """Test get config with specific path."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"value": "test"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get config with path
        result = await client_with_mock_session.get_config("timeout")
        
        assert result == {"value": "test"}
        # Verify config command was called with params
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "config"
        assert request_data["params"] == {"path": "timeout"}
    
    @pytest.mark.asyncio
    async def test_is_connected_success(self, client_with_mock_session, mock_session):
        """Test is_connected when server responds."""
        # Mock successful health check
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "healthy"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Test connection
        result = await client_with_mock_session.is_connected()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_connected_failure(self, client_with_mock_session, mock_session):
        """Test is_connected when server doesn't respond."""
        # Mock connection error
        mock_session.post.side_effect = httpx.RequestError("Connection failed")
        
        # Test connection
        result = await client_with_mock_session.is_connected()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_server_info(self, client_with_mock_session, mock_session):
        """Test get server info."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"version": "1.0.0"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get server info
        result = await client_with_mock_session.get_server_info()
        
        assert result == {"version": "1.0.0"}
        # Verify config command was called
        call_args = mock_session.post.call_args
        request_data = call_args[1]["json"]
        assert request_data["method"] == "config"
    
    @pytest.mark.asyncio
    async def test_ping_success(self, client_with_mock_session, mock_session):
        """Test ping when server responds."""
        # Mock successful health check
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "healthy"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Test ping
        result = await client_with_mock_session.ping()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, client_with_mock_session, mock_session):
        """Test ping when server doesn't respond."""
        # Mock connection error
        mock_session.post.side_effect = httpx.RequestError("Connection failed")
        
        # Test ping
        result = await client_with_mock_session.ping()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, client_with_mock_session, mock_session):
        """Test retry logic for transient failures."""
        # Mock first call fails, second succeeds
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
    
        mock_session.post.side_effect = [
            httpx.RequestError("Connection failed"),  # First call fails
            mock_response  # Second call succeeds
        ]
    
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
    
        # Execute request with retry
        result = await client_with_mock_session._execute_request(request, max_retries=2)
        
        assert result == {"status": "success"}
        assert mock_session.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_request_with_retry_backoff(self, client_with_mock_session, mock_session):
        """Test retry logic with exponential backoff."""
        # Mock multiple failures then success
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
    
        mock_session.post.side_effect = [
            httpx.RequestError("Connection failed"),  # First call fails
            httpx.RequestError("Connection failed"),  # Second call fails
            mock_response  # Third call succeeds
        ]
    
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
    
        # Execute request with retry
        result = await client_with_mock_session._execute_request(request, max_retries=3)
        
        assert result == {"status": "success"}
        assert mock_session.post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_request_max_retries_exceeded(self, client_with_mock_session, mock_session):
        """Test that max retries are respected."""
        # Mock all calls fail
        mock_session.post.side_effect = httpx.RequestError("Connection failed")
    
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
    
        # Execute request with retry
        with pytest.raises(ConnectionError, match="Connection failed"):
            await client_with_mock_session._execute_request(request, max_retries=2)
        
        # Verify exactly max_retries + 1 calls were made
        assert mock_session.post.call_count == 3  # 2 retries + 1 initial call
    
    def test_prepare_request_validates_jsonrpc_version(self, client):
        """Test that JSON-RPC version is correctly set."""
        request = client._prepare_request("test_method")
        
        assert request.jsonrpc == JSON_RPC_VERSION
    
    def test_prepare_request_validates_method_stripping(self, client):
        """Test that method names are properly stripped."""
        request = client._prepare_request("  test_method  ")
        
        assert request.method == "test_method"
    
    @pytest.mark.asyncio
    async def test_execute_request_validates_response_structure(self, client_with_mock_session, mock_session):
        """Test that response structure is validated."""
        # Mock response with non-dict result
        mock_response = Mock()
        mock_response.json.return_value = "not a dict"  # Not a dictionary
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        with pytest.raises(JsonRpcError, match="Response must be a dictionary"):
            await client_with_mock_session._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_handles_missing_result(self, client_with_mock_session, mock_session):
        """Test handling of response with missing result field."""
        # Mock response with empty result
        mock_response = Mock()
        mock_response.json.return_value = {"result": None}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Create request
        request = JsonRpcRequest(
            jsonrpc=JSON_RPC_VERSION,
            method="test_method",
            id=1
        )
        
        # Execute request
        result = await client_with_mock_session._execute_request(request)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_execute_command_with_retry(self, client_with_mock_session, mock_session):
        """Test command execution with retry logic."""
        # Mock first call fails, second succeeds
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"status": "success"}}
        mock_response.raise_for_status = MagicMock()
    
        mock_session.post.side_effect = [
            httpx.RequestError("Connection failed"),  # First call fails
            mock_response  # Second call succeeds
        ]
    
        # Execute command with retry
        result = await client_with_mock_session.execute_command("test_method", max_retries=2)
        
        assert result == {"status": "success"}
        assert mock_session.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_health_check_with_error(self, client_with_mock_session, mock_session):
        """Test health check when server returns error."""
        # Mock health check error
        mock_response = Mock()
        mock_response.json.return_value = {"error": {"code": -32601, "message": "Method not found"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute health check
        with pytest.raises(JsonRpcError, match="JSON-RPC error -32601"):
            await client_with_mock_session.health_check()
    
    @pytest.mark.asyncio
    async def test_get_help_with_error(self, client_with_mock_session, mock_session):
        """Test get help when server returns error."""
        # Mock help error
        mock_response = Mock()
        mock_response.json.return_value = {"error": {"code": -32601, "message": "Method not found"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get help
        with pytest.raises(JsonRpcError, match="JSON-RPC error -32601"):
            await client_with_mock_session.get_help()
    
    @pytest.mark.asyncio
    async def test_get_config_with_error(self, client_with_mock_session, mock_session):
        """Test get config when server returns error."""
        # Mock config error
        mock_response = Mock()
        mock_response.json.return_value = {"error": {"code": -32601, "message": "Method not found"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get config
        with pytest.raises(JsonRpcError, match="JSON-RPC error -32601"):
            await client_with_mock_session.get_config()
    
    @pytest.mark.asyncio
    async def test_get_server_info_with_error(self, client_with_mock_session, mock_session):
        """Test get server info when server returns error."""
        # Mock server info error
        mock_response = Mock()
        mock_response.json.return_value = {"error": {"code": -32601, "message": "Method not found"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute get server info
        with pytest.raises(JsonRpcError, match="JSON-RPC error -32601"):
            await client_with_mock_session.get_server_info()
    
    @pytest.mark.asyncio
    async def test_ping_with_error(self, client_with_mock_session, mock_session):
        """Test ping when server returns error."""
        # Mock ping error
        mock_response = Mock()
        mock_response.json.return_value = {"error": {"code": -32601, "message": "Method not found"}}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        
        # Execute ping
        result = await client_with_mock_session.ping()
        
        # Ping should return False on error, not raise exception
        assert result is False 