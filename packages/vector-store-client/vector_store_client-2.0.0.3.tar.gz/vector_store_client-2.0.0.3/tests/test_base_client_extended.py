"""
Extended tests for BaseVectorStoreClient.

This module contains comprehensive tests for the base client class
to achieve maximum code coverage.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any

import httpx

from vector_store_client.base_client import BaseVectorStoreClient
from vector_store_client.exceptions import (
    ValidationError, ConnectionError, JsonRpcError, ServerError
)
from vector_store_client.models import JsonRpcRequest


class TestBaseClientExtended:
    """Extended tests for BaseVectorStoreClient."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = BaseVectorStoreClient("http://localhost:8007")
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_prepare_request_with_params(self, client):
        """Test request preparation with parameters."""
        request = client._prepare_request(
            method="test_method",
            params={"key": "value"},
            request_id="test_id"
        )
        
        assert isinstance(request, JsonRpcRequest)
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.id == "test_id"
        assert request.jsonrpc == "2.0"
    
    @pytest.mark.asyncio
    async def test_prepare_request_without_params(self, client):
        """Test request preparation without parameters."""
        request = client._prepare_request(
            method="test_method",
            request_id=123
        )
        
        assert isinstance(request, JsonRpcRequest)
        assert request.method == "test_method"
        assert request.params is None
        assert request.id == 123
    
    @pytest.mark.asyncio
    async def test_prepare_request_invalid_method(self, client):
        """Test request preparation with invalid method."""
        with pytest.raises(ValidationError, match="Method must be a non-empty string"):
            client._prepare_request(method="")
        
        with pytest.raises(ValidationError, match="Method must be a non-empty string"):
            client._prepare_request(method=None)
        
        with pytest.raises(ValidationError, match="Method must be a non-empty string"):
            client._prepare_request(method=123)
    
    @pytest.mark.asyncio
    async def test_prepare_request_invalid_params(self, client):
        """Test request preparation with invalid parameters."""
        with pytest.raises(ValidationError, match="Parameters must be a dictionary"):
            client._prepare_request(method="test", params="invalid")
        
        with pytest.raises(ValidationError, match="Parameters must be a dictionary"):
            client._prepare_request(method="test", params=123)
    
    @pytest.mark.asyncio
    async def test_prepare_request_method_stripping(self, client):
        """Test that method name is stripped of whitespace."""
        request = client._prepare_request(method="  test_method  ")
        assert request.method == "test_method"
    
    @pytest.mark.asyncio
    async def test_execute_request_success(self, client):
        """Test successful request execution."""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"result": {"status": "success"}})
        mock_response.raise_for_status = AsyncMock(return_value=None)
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            result = await client._execute_request(request)
            
            assert result == {"status": "success"}
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_request_json_decode_error(self, client):
        """Test request execution with JSON decode error."""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        mock_response.raise_for_status = AsyncMock(return_value=None)
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            with pytest.raises(JsonRpcError, match="Invalid JSON response"):
                await client._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_invalid_response_type(self, client):
        """Test request execution with invalid response type."""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value="not a dict")
        mock_response.raise_for_status = AsyncMock(return_value=None)
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            with pytest.raises(JsonRpcError, match="Response must be a dictionary"):
                await client._execute_request(request)
    
    @pytest.mark.asyncio
    async def test_execute_request_json_rpc_error(self, client):
        """Test request execution with JSON-RPC error."""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        })
        mock_response.raise_for_status = AsyncMock(return_value=None)
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            with pytest.raises(JsonRpcError) as exc_info:
                await client._execute_request(request)
            
            assert "JSON-RPC error -32601: Method not found" in str(exc_info.value)
            assert exc_info.value.code == -32601
            assert exc_info.value.method == "test_method"
            assert exc_info.value.request_id == 1
    
    @pytest.mark.asyncio
    async def test_execute_request_connection_error(self, client):
        """Test request execution with connection error."""
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            with pytest.raises(ConnectionError) as exc_info:
                await client._execute_request(request)
            
            assert "Connection failed" in str(exc_info.value)
            assert exc_info.value.url == "http://localhost:8007"
            assert exc_info.value.timeout == 30.0
    
    @pytest.mark.asyncio
    async def test_execute_request_http_status_error(self, client):
        """Test request execution with HTTP status error."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.json = MagicMock(return_value={"error": {"message": "Server error", "code": 500}})
        mock_response.raise_for_status = AsyncMock(side_effect=httpx.HTTPStatusError(
            "Internal Server Error",
            request=MagicMock(),
            response=mock_response
        ))
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            with pytest.raises(JsonRpcError) as exc_info:
                await client._execute_request(request)
            
            assert "JSON-RPC error 500" in str(exc_info.value)
            assert "Server error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_request_with_retry(self, client):
        """Test request execution with retry logic."""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"result": {"status": "success"}})
        mock_response.raise_for_status = AsyncMock(return_value=None)
        
        with patch.object(client.session, 'post', new_callable=AsyncMock) as mock_post:
            # First call fails, second succeeds
            mock_post.side_effect = [
                httpx.RequestError("Connection failed"),
                mock_response
            ]
            
            request = JsonRpcRequest(
                jsonrpc="2.0",
                method="test_method",
                id=1
            )
            
            result = await client._execute_request(request, max_retries=2)
            
            assert result == {"status": "success"}
            assert mock_post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self, client):
        """Test successful command execution."""
        with patch.object(client, '_prepare_request') as mock_prepare, \
             patch.object(client, '_execute_request') as mock_execute:
            
            mock_request = MagicMock()
            mock_prepare.return_value = mock_request
            mock_execute.return_value = {"status": "success"}
            
            result = await client.execute_command(
                method="test_method",
                params={"key": "value"},
                request_id="test_id",
                max_retries=3
            )
            
            assert result == {"status": "success"}
            mock_prepare.assert_called_once_with("test_method", {"key": "value"}, "test_id")
            mock_execute.assert_called_once_with(mock_request, 3)
    
    @pytest.mark.asyncio
    async def test_execute_command_with_exception(self, client):
        """Test command execution with exception."""
        with patch.object(client, '_prepare_request') as mock_prepare, \
             patch.object(client, '_execute_request') as mock_execute:
            
            mock_request = MagicMock()
            mock_prepare.return_value = mock_request
            mock_execute.side_effect = ConnectionError("Connection failed")
            
            with pytest.raises(ConnectionError):
                await client.execute_command("test_method")
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check command."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"status": "healthy"}
            
            result = await client.health_check()
            
            assert result == {"status": "healthy"}
            mock_execute.assert_called_once_with("health", {})
    
    @pytest.mark.asyncio
    async def test_get_help_with_command(self, client):
        """Test get help with specific command."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"help": "command help"}
            
            result = await client.get_help("test_command")
            
            assert result == {"help": "command help"}
            mock_execute.assert_called_once_with("help", {"command": "test_command"})
    
    @pytest.mark.asyncio
    async def test_get_help_without_command(self, client):
        """Test get help without specific command."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"help": "general help"}
            
            result = await client.get_help()
            
            assert result == {"help": "general help"}
            mock_execute.assert_called_once_with("help", {})
    
    @pytest.mark.asyncio
    async def test_get_config_with_path(self, client):
        """Test get config with specific path."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"config": "path config"}
            
            result = await client.get_config("test.path")
            
            assert result == {"config": "path config"}
            mock_execute.assert_called_once_with("config", {"path": "test.path"})
    
    @pytest.mark.asyncio
    async def test_get_config_without_path(self, client):
        """Test get config without specific path."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"config": "full config"}
            
            result = await client.get_config()
            
            assert result == {"config": "full config"}
            mock_execute.assert_called_once_with("config", {})
    
    @pytest.mark.asyncio
    async def test_is_connected_success(self, client):
        """Test is_connected when server is available."""
        with patch.object(client, 'health_check') as mock_health:
            mock_health.return_value = {"status": "healthy"}
            
            result = await client.is_connected()
            
            assert result is True
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_connected_failure(self, client):
        """Test is_connected when server is not available."""
        with patch.object(client, 'health_check') as mock_health:
            mock_health.side_effect = ConnectionError("Connection failed")
            
            result = await client.is_connected()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_server_info(self, client):
        """Test get server info."""
        with patch.object(client, 'execute_command') as mock_execute:
            mock_execute.return_value = {"server": "info"}
            
            result = await client.get_server_info()
            
            assert result == {"server": "info"}
            mock_execute.assert_called_once_with("config")
    
    @pytest.mark.asyncio
    async def test_ping_success(self, client):
        """Test ping when server responds."""
        with patch.object(client, 'health_check') as mock_health:
            mock_health.return_value = {"status": "healthy"}
            
            result = await client.ping()
            
            assert result is True
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, client):
        """Test ping when server does not respond."""
        with patch.object(client, 'health_check') as mock_health:
            mock_health.side_effect = ConnectionError("Connection failed")
            
            result = await client.ping()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager."""
        with patch.object(client, 'close') as mock_close:
            async with client as ctx_client:
                assert ctx_client is client
            
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_session_already_closed(self, client):
        """Test closing already closed session."""
        # Mock session as already closed
        with patch('httpx.AsyncClient.is_closed', True):
            with patch.object(client.session, 'aclose') as mock_aclose:
                await client.close()
                mock_aclose.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_close_session_not_closed(self, client):
        """Test closing not closed session."""
        # Mock session as not closed
        with patch('httpx.AsyncClient.is_closed', False):
            with patch.object(client.session, 'aclose') as mock_aclose:
                await client.close()
                mock_aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_init_with_custom_session(self, client):
        """Test initialization with custom session."""
        custom_session = httpx.AsyncClient(timeout=60.0)
        client_with_session = BaseVectorStoreClient(
            base_url="http://localhost:8008",
            timeout=60.0,
            session=custom_session
        )
        
        assert client_with_session.session is custom_session
        assert client_with_session.timeout == 60.0
        assert client_with_session.base_url == "http://localhost:8008"
        
        await client_with_session.close() 