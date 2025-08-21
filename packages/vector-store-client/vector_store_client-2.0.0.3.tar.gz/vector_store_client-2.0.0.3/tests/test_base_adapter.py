"""
Tests for BaseAdapter.

This module contains tests for the base adapter functionality
including connection management, error handling, and retry logic.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from vector_store_client.adapters.base_adapter import BaseAdapter
from vector_store_client.exceptions import VectorStoreError, ConnectionError


class MockAdapter(BaseAdapter):
    """Mock adapter for testing BaseAdapter functionality."""
    
    async def _create_client(self) -> None:
        """Create mock client."""
        self._client = MagicMock()
        self._client.health = AsyncMock()
        self._client.get_help = AsyncMock()
    
    async def _close_client(self) -> None:
        """Close mock client."""
        if self._client:
            self._client = None


class TestBaseAdapter:
    """Test BaseAdapter functionality."""
    
    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockAdapter("http://localhost:8001", timeout=30.0)
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.base_url == "http://localhost:8001"
        assert adapter.timeout == 30.0
        assert adapter._client is None
        assert adapter.logger is not None
    
    def test_init_with_trailing_slash(self):
        """Test initialization with trailing slash in URL."""
        adapter = MockAdapter("http://localhost:8001/", timeout=30.0)
        assert adapter.base_url == "http://localhost:8001"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, adapter):
        """Test async context manager."""
        async with adapter as ctx_adapter:
            assert ctx_adapter is adapter
            assert adapter._client is not None
        
        assert adapter._client is None
    
    @pytest.mark.asyncio
    async def test_context_manager_with_exception(self, adapter):
        """Test context manager with exception."""
        with pytest.raises(ValueError):
            async with adapter:
                raise ValueError("Test exception")
        
        assert adapter._client is None
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, adapter):
        """Test successful health check."""
        await adapter._create_client()
        
        mock_health_response = {"status": "healthy", "version": "1.0.0"}
        adapter._client.health.return_value = mock_health_response
        
        result = await adapter.health_check()
        
        assert result == mock_health_response
        adapter._client.health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_client_not_initialized(self, adapter):
        """Test health check with uninitialized client."""
        with pytest.raises(VectorStoreError, match="Client not initialized"):
            await adapter.health_check()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, adapter):
        """Test health check failure."""
        await adapter._create_client()
        
        adapter._client.health.side_effect = Exception("Service unavailable")
        
        with pytest.raises(ConnectionError, match="Health check failed"):
            await adapter.health_check()
    
    @pytest.mark.asyncio
    async def test_get_help_success(self, adapter):
        """Test successful help request."""
        await adapter._create_client()
        
        mock_help_response = {"commands": ["health", "help"], "version": "1.0.0"}
        adapter._client.get_help.return_value = mock_help_response
        
        result = await adapter.get_help()
        
        assert result == mock_help_response
        adapter._client.get_help.assert_called_once_with(None)
    
    @pytest.mark.asyncio
    async def test_get_help_with_command(self, adapter):
        """Test help request with specific command."""
        await adapter._create_client()
        
        mock_help_response = {"command": "health", "description": "Check service health"}
        adapter._client.get_help.return_value = mock_help_response
        
        result = await adapter.get_help("health")
        
        assert result == mock_help_response
        adapter._client.get_help.assert_called_once_with("health")
    
    @pytest.mark.asyncio
    async def test_get_help_client_not_initialized(self, adapter):
        """Test help request with uninitialized client."""
        with pytest.raises(VectorStoreError, match="Client not initialized"):
            await adapter.get_help()
    
    @pytest.mark.asyncio
    async def test_get_help_failure(self, adapter):
        """Test help request failure."""
        await adapter._create_client()
        
        adapter._client.get_help.side_effect = Exception("Service unavailable")
        
        with pytest.raises(ConnectionError, match="Help request failed"):
            await adapter.get_help()
    
    @pytest.mark.asyncio
    async def test_is_available_success(self, adapter):
        """Test service availability check success."""
        await adapter._create_client()
        
        adapter._client.health.return_value = {"status": "healthy"}
        
        result = await adapter.is_available()
        
        assert result is True
        adapter._client.health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_available_failure(self, adapter):
        """Test service availability check failure."""
        await adapter._create_client()
        
        adapter._client.health.side_effect = Exception("Service unavailable")
        
        result = await adapter.is_available()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_available_client_not_initialized(self, adapter):
        """Test availability check with uninitialized client."""
        result = await adapter.is_available()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_service_info_success(self, adapter):
        """Test successful service info retrieval."""
        await adapter._create_client()
        
        mock_health = {"status": "healthy", "version": "1.0.0"}
        mock_help = {"commands": ["health", "help"]}
        
        adapter._client.health.return_value = mock_health
        adapter._client.get_help.return_value = mock_help
        
        result = await adapter.get_service_info()
        
        expected = {
            "service_type": "MockAdapter",
            "base_url": "http://localhost:8001",
            "timeout": 30.0,
            "health": mock_health,
            "help": mock_help
        }
        
        assert result == expected
        adapter._client.health.assert_called_once()
        adapter._client.get_help.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_service_info_with_error(self, adapter):
        """Test service info retrieval with error."""
        await adapter._create_client()
        
        adapter._client.health.side_effect = Exception("Service unavailable")
        
        result = await adapter.get_service_info()
        
        expected = {
            "service_type": "MockAdapter",
            "base_url": "http://localhost:8001",
            "timeout": 30.0,
            "error": "Health check failed: Service unavailable"
        }
        
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_get_service_info_client_not_initialized(self, adapter):
        """Test service info with uninitialized client."""
        result = await adapter.get_service_info()
        
        expected = {
            "service_type": "MockAdapter",
            "base_url": "http://localhost:8001",
            "timeout": 30.0,
            "error": "Client not initialized"
        }
        
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_close_client_already_closed(self, adapter):
        """Test closing already closed client."""
        # Client is already None
        await adapter._close_client()
        assert adapter._client is None
    
    @pytest.mark.asyncio
    async def test_create_client_twice(self, adapter):
        """Test creating client twice."""
        await adapter._create_client()
        assert adapter._client is not None
        
        # Create again - should work
        await adapter._create_client()
        assert adapter._client is not None
    
    @pytest.mark.asyncio
    async def test_logger_name(self, adapter):
        """Test logger name is correct."""
        assert adapter.logger.name == "MockAdapter"
    
    def test_abstract_methods(self):
        """Test that BaseAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAdapter("http://localhost:8001")


class TestBaseAdapterIntegration:
    """Integration tests for BaseAdapter."""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test complete adapter lifecycle."""
        adapter = MockAdapter("http://localhost:8001")
        
        # Test initialization
        assert adapter._client is None
        
        # Test context manager
        async with adapter:
            assert adapter._client is not None
            
            # Test health check
            adapter._client.health.return_value = {"status": "healthy"}
            health = await adapter.health_check()
            assert health["status"] == "healthy"
            
            # Test help
            adapter._client.get_help.return_value = {"commands": ["health"]}
            help_info = await adapter.get_help()
            assert "commands" in help_info
            
            # Test availability
            available = await adapter.is_available()
            assert available is True
            
            # Test service info
            info = await adapter.get_service_info()
            assert info["service_type"] == "MockAdapter"
            assert info["base_url"] == "http://localhost:8001"
        
        # Test cleanup
        assert adapter._client is None
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling integration."""
        adapter = MockAdapter("http://localhost:8001")
        
        async with adapter:
            # Test health check error
            adapter._client.health.side_effect = Exception("Network error")
            
            with pytest.raises(ConnectionError, match="Health check failed"):
                await adapter.health_check()
            
            # Test availability with error
            available = await adapter.is_available()
            assert available is False
            
            # Test service info with error
            info = await adapter.get_service_info()
            assert "error" in info
            assert info["error"] == "Health check failed: Network error"
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent access to adapter."""
        adapter = MockAdapter("http://localhost:8001")
        
        async def health_check_task():
            async with adapter:
                adapter._client.health.return_value = {"status": "healthy"}
                return await adapter.health_check()
        
        # Run multiple concurrent health checks
        tasks = [health_check_task() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            assert result["status"] == "healthy" 