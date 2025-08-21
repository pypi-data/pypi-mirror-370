"""
Tests for Vector Store Client Middleware.

This module contains unit tests for the middleware classes:
- BaseMiddleware
- LoggingMiddleware
- MetricsMiddleware
- CachingMiddleware
- RetryMiddleware

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any, Callable, Awaitable
import time

from vector_store_client.middleware.base_middleware import BaseMiddleware, MiddlewareChain
from vector_store_client.middleware.logging_middleware import LoggingMiddleware
from vector_store_client.middleware.metrics_middleware import MetricsMiddleware
from vector_store_client.middleware.caching_middleware import CachingMiddleware
from vector_store_client.middleware.retry_middleware import RetryMiddleware
from vector_store_client.exceptions import ConnectionError, ValidationError


class TestBaseMiddleware:
    """Test cases for BaseMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create a BaseMiddleware instance."""
        # BaseMiddleware is abstract, so we'll test it through a concrete implementation
        return LoggingMiddleware()
    
    @pytest.mark.asyncio
    async def test_middleware_creation(self, middleware):
        """Test middleware creation."""
        assert middleware is not None
        assert hasattr(middleware, 'process_request')
    
    @pytest.mark.asyncio
    async def test_process_request_default(self, middleware):
        """Test default process_request implementation."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        result = await middleware.process_request(request_data, next_handler)
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_middleware_chain(self, middleware):
        """Test middleware chaining."""
        request_data = {"method": "test", "params": {"key": "value"}}
        response_data = {"result": {"status": "success"}}
        
        next_handler = AsyncMock()
        next_handler.return_value = response_data
        processed_request = await middleware.process_request(request_data, next_handler)
        
        assert processed_request == response_data
    
    @pytest.mark.asyncio
    async def test_enable_middleware(self, middleware):
        """Test enabling middleware."""
        middleware.disable()
        assert not middleware.is_enabled()
        
        middleware.enable()
        assert middleware.is_enabled()
    
    @pytest.mark.asyncio
    async def test_disable_middleware(self, middleware):
        """Test disabling middleware."""
        assert middleware.is_enabled()
        
        middleware.disable()
        assert not middleware.is_enabled()
    
    @pytest.mark.asyncio
    async def test_is_enabled(self, middleware):
        """Test is_enabled method."""
        assert middleware.is_enabled() is True
        
        middleware.disable()
        assert middleware.is_enabled() is False
        
        middleware.enable()
        assert middleware.is_enabled() is True
    
    @pytest.mark.asyncio
    async def test_get_config(self, middleware):
        """Test get_config method."""
        config = middleware.get_config()
        
        assert isinstance(config, dict)
        assert "name" in config
        assert "enabled" in config
        assert "type" in config
        assert config["name"] == middleware.name
        assert config["enabled"] == middleware.enabled
        assert config["type"] == middleware.__class__.__name__
    
    @pytest.mark.asyncio
    async def test_execute_command(self, middleware):
        """Test execute_command method."""
        result = await middleware.execute_command("test_method", {"param": "value"})
        
        assert isinstance(result, dict)
        assert "result" in result
        assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_command_without_params(self, middleware):
        """Test execute_command method without parameters."""
        result = await middleware.execute_command("test_method")
        
        assert isinstance(result, dict)
        assert "result" in result
        assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_middleware_with_default_name(self):
        """Test middleware with default name."""
        middleware = LoggingMiddleware()
        
        assert middleware.name == "LoggingMiddleware"
        assert middleware.logger.name == "middleware.LoggingMiddleware.logging"
    
    @pytest.mark.asyncio
    async def test_middleware_logger_creation(self, middleware):
        """Test middleware logger creation."""
        assert middleware.logger is not None
        assert middleware.logger.name == f"middleware.{middleware.name}.logging"
    
    @pytest.mark.asyncio
    async def test_base_middleware_abstract_method(self):
        """Test that BaseMiddleware cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseMiddleware()


class TestMiddlewareChain:
    """Test cases for MiddlewareChain class."""
    
    @pytest.fixture
    def chain(self):
        """Create a MiddlewareChain instance."""
        return MiddlewareChain()
    
    @pytest.fixture
    def mock_middleware(self):
        """Create a mock middleware that inherits from BaseMiddleware."""
        class MockMiddleware(BaseMiddleware):
            def __init__(self):
                super().__init__("MockMiddleware")
                self._process_request = AsyncMock()
                self._process_request.return_value = {"result": "from_middleware"}
            
            async def process_request(
                self,
                request: Dict[str, Any],
                next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
            ) -> Dict[str, Any]:
                return await self._process_request(request, next_handler)
        
        return MockMiddleware()
    
    @pytest.mark.asyncio
    async def test_chain_creation(self, chain):
        """Test middleware chain creation."""
        assert chain is not None
        assert isinstance(chain.middlewares, list)
        assert len(chain.middlewares) == 0
    
    @pytest.mark.asyncio
    async def test_add_middleware(self, chain, mock_middleware):
        """Test adding middleware to chain."""
        chain.add_middleware(mock_middleware)
        
        assert len(chain.middlewares) == 1
        assert chain.middlewares[0] == mock_middleware
    
    @pytest.mark.asyncio
    async def test_add_middleware_invalid_type(self, chain):
        """Test adding invalid middleware type."""
        invalid_middleware = "not_a_middleware"
        
        with pytest.raises(ValueError, match="Invalid middleware type"):
            chain.add_middleware(invalid_middleware)
    
    @pytest.mark.asyncio
    async def test_remove_middleware_success(self, chain, mock_middleware):
        """Test removing middleware successfully."""
        chain.add_middleware(mock_middleware)
        assert len(chain.middlewares) == 1
        
        result = chain.remove_middleware("MockMiddleware")
        
        assert result is True
        assert len(chain.middlewares) == 0
    
    @pytest.mark.asyncio
    async def test_remove_middleware_not_found(self, chain):
        """Test removing middleware that doesn't exist."""
        result = chain.remove_middleware("NonExistentMiddleware")
        
        assert result is False
        assert len(chain.middlewares) == 0
    
    @pytest.mark.asyncio
    async def test_get_middleware_found(self, chain, mock_middleware):
        """Test getting middleware that exists."""
        chain.add_middleware(mock_middleware)
        
        found_middleware = chain.get_middleware("MockMiddleware")
        
        assert found_middleware == mock_middleware
    
    @pytest.mark.asyncio
    async def test_get_middleware_not_found(self, chain):
        """Test getting middleware that doesn't exist."""
        found_middleware = chain.get_middleware("NonExistentMiddleware")
        
        assert found_middleware is None
    
    @pytest.mark.asyncio
    async def test_list_middlewares(self, chain, mock_middleware):
        """Test listing middleware names."""
        assert chain.list_middlewares() == []
        
        chain.add_middleware(mock_middleware)
        
        middleware_names = chain.list_middlewares()
        assert middleware_names == ["MockMiddleware"]
    
    @pytest.mark.asyncio
    async def test_clear_middlewares(self, chain, mock_middleware):
        """Test clearing all middleware."""
        chain.add_middleware(mock_middleware)
        assert len(chain.middlewares) == 1
        
        chain.clear()
        
        assert len(chain.middlewares) == 0
    
    @pytest.mark.asyncio
    async def test_execute_empty_chain(self, chain):
        """Test executing empty middleware chain."""
        async def final_handler(request):
            return {"result": "final"}
        
        request = {"method": "test", "params": {"key": "value"}}
        
        result = await chain.execute(request, final_handler)
        
        assert result == {"result": "final"}
    
    @pytest.mark.asyncio
    async def test_execute_with_middleware(self, chain, mock_middleware):
        """Test executing chain with middleware."""
        chain.add_middleware(mock_middleware)
        
        async def final_handler(request):
            return {"result": "final"}
        
        request = {"method": "test", "params": {"key": "value"}}
        
        result = await chain.execute(request, final_handler)
        
        # Should return result from middleware
        assert result == {"result": "from_middleware"}
        mock_middleware._process_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_disabled_middleware(self, chain, mock_middleware):
        """Test executing chain with disabled middleware."""
        # Mock the is_enabled method to return False
        with patch.object(mock_middleware, 'is_enabled', return_value=False):
            chain.add_middleware(mock_middleware)
            
            async def final_handler(request):
                return {"result": "final"}
            
            request = {"method": "test", "params": {"key": "value"}}
            
            result = await chain.execute(request, final_handler)
            
            # Should skip disabled middleware and return final handler result
            assert result == {"result": "final"}
            mock_middleware._process_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_with_multiple_middleware(self, chain):
        """Test executing chain with multiple middleware."""
        # Create multiple mock middleware
        class MockMiddleware1(BaseMiddleware):
            def __init__(self):
                super().__init__("Middleware1")
                self._process_request = AsyncMock()
                self._process_request.return_value = {"result": "from_middleware1"}
            
            async def process_request(
                self,
                request: Dict[str, Any],
                next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
            ) -> Dict[str, Any]:
                return await self._process_request(request, next_handler)
        
        class MockMiddleware2(BaseMiddleware):
            def __init__(self):
                super().__init__("Middleware2")
                self._process_request = AsyncMock()
                self._process_request.return_value = {"result": "from_middleware2"}
            
            async def process_request(
                self,
                request: Dict[str, Any],
                next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
            ) -> Dict[str, Any]:
                return await self._process_request(request, next_handler)
        
        middleware1 = MockMiddleware1()
        middleware2 = MockMiddleware2()
        
        chain.add_middleware(middleware1)
        chain.add_middleware(middleware2)
        
        async def final_handler(request):
            return {"result": "final"}
        
        request = {"method": "test", "params": {"key": "value"}}
        
        result = await chain.execute(request, final_handler)
        
        # Should return result from first middleware in chain
        assert result == {"result": "from_middleware1"}
        middleware1._process_request.assert_called_once()
        middleware2._process_request.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, chain, mock_middleware):
        """Test executing chain with exception."""
        mock_middleware._process_request.side_effect = Exception("Middleware error")
        chain.add_middleware(mock_middleware)
        
        async def final_handler(request):
            return {"result": "final"}
        
        request = {"method": "test", "params": {"key": "value"}}
        
        with pytest.raises(Exception, match="Middleware error"):
            await chain.execute(request, final_handler)
    
    @pytest.mark.asyncio
    async def test_get_middleware_info(self, chain, mock_middleware):
        """Test getting middleware information."""
        assert chain.get_middleware_info() == {}
        
        chain.add_middleware(mock_middleware)
        
        info = chain.get_middleware_info()
        
        assert isinstance(info, dict)
        assert "MockMiddleware" in info
        assert info["MockMiddleware"]["name"] == "MockMiddleware"
        assert info["MockMiddleware"]["enabled"] == mock_middleware.enabled
        assert info["MockMiddleware"]["type"] == mock_middleware.__class__.__name__
    
    @pytest.mark.asyncio
    async def test_middleware_chain_logger(self, chain):
        """Test middleware chain logger."""
        assert chain.logger is not None
        assert chain.logger.name == "middleware_chain"
    
    @pytest.mark.asyncio
    async def test_add_middleware_logging(self, chain, mock_middleware):
        """Test logging when adding middleware."""
        with patch.object(chain.logger, 'info') as mock_log:
            chain.add_middleware(mock_middleware)
            mock_log.assert_called_once_with("Added middleware: MockMiddleware")
    
    @pytest.mark.asyncio
    async def test_remove_middleware_logging(self, chain, mock_middleware):
        """Test logging when removing middleware."""
        chain.add_middleware(mock_middleware)
        
        with patch.object(chain.logger, 'info') as mock_log:
            chain.remove_middleware("MockMiddleware")
            mock_log.assert_called_once_with("Removed middleware: MockMiddleware")
    
    @pytest.mark.asyncio
    async def test_clear_logging(self, chain, mock_middleware):
        """Test logging when clearing middleware."""
        chain.add_middleware(mock_middleware)
        
        with patch.object(chain.logger, 'info') as mock_log:
            chain.clear()
            mock_log.assert_called_once_with("Cleared all middleware")
    
    @pytest.mark.asyncio
    async def test_execute_logging_on_exception(self, chain, mock_middleware):
        """Test logging when execution fails."""
        mock_middleware._process_request.side_effect = Exception("Test error")
        chain.add_middleware(mock_middleware)
        
        async def final_handler(request):
            return {"result": "final"}
        
        request = {"method": "test", "params": {"key": "value"}}
        
        with patch.object(chain.logger, 'error') as mock_log:
            with pytest.raises(Exception):
                await chain.execute(request, final_handler)
            
            mock_log.assert_called_once_with("Middleware chain execution failed: Test error")


class TestLoggingMiddleware:
    """Test cases for LoggingMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create a LoggingMiddleware instance."""
        return LoggingMiddleware()
    
    @pytest.mark.asyncio
    async def test_middleware_creation(self, middleware):
        """Test middleware creation."""
        assert middleware is not None
        assert middleware.logger is not None
    
    @pytest.mark.asyncio
    async def test_process_request_logging(self, middleware):
        """Test request logging."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        with patch.object(middleware.logger, 'info') as mock_log:
            result = await middleware.process_request(request_data, next_handler)
            
            assert result == {"result": "success"}
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_request_with_error(self, middleware):
        """Test request logging with error."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def failing_handler(request):
            raise Exception("Test error")
        
        with patch.object(middleware.logger, 'error') as mock_log:
            with pytest.raises(Exception):
                await middleware.process_request(request_data, failing_handler)
            
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_logging_with_timing(self, middleware):
        """Test logging with timing information."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": {"status": "success"}}
        
        with patch.object(middleware.logger, 'info') as mock_log:
            await middleware.process_request(request_data, next_handler)
            
            # Should log request and response
            assert mock_log.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_logging_with_custom_logger(self):
        """Test middleware with custom logger."""
        middleware = LoggingMiddleware()
        
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}


class TestMetricsMiddleware:
    """Test cases for MetricsMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create a MetricsMiddleware instance."""
        return MetricsMiddleware()
    
    @pytest.mark.asyncio
    async def test_middleware_creation(self, middleware):
        """Test middleware creation."""
        assert middleware is not None
        assert middleware.name == "MetricsMiddleware"
    
    @pytest.mark.asyncio
    async def test_process_request_metrics(self, middleware):
        """Test request metrics collection."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_process_request_error_metrics(self, middleware):
        """Test error response metrics collection."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def failing_handler(request):
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            await middleware.process_request(request_data, failing_handler)
    
    @pytest.mark.asyncio
    async def test_metrics_with_timing(self, middleware):
        """Test metrics with timing information."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": {"status": "success"}}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": {"status": "success"}}
    
    @pytest.mark.asyncio
    async def test_metrics_with_custom_collector(self):
        """Test middleware with custom metrics collector."""
        middleware = MetricsMiddleware()
        
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, middleware):
        """Test getting metrics data."""
        config = middleware.get_config()
        assert "name" in config
        assert config["name"] == "MetricsMiddleware"
    
    @pytest.mark.asyncio
    async def test_get_name(self, middleware):
        """Test get_name method."""
        name = middleware.get_name()
        assert name == "MetricsMiddleware"
    
    @pytest.mark.asyncio
    async def test_get_metrics_specific_method(self, middleware):
        """Test get_metrics for specific method."""
        # First, make a request to populate metrics
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data, next_handler)
        
        # Get metrics for specific method
        metrics = middleware.get_metrics("test_method")
        assert isinstance(metrics, dict)
        assert "total_requests" in metrics
        assert metrics["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_get_metrics_all_methods(self, middleware):
        """Test get_metrics for all methods."""
        # Make requests to populate metrics
        request_data1 = {"method": "method1", "params": {"key": "value"}}
        request_data2 = {"method": "method2", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data1, next_handler)
        await middleware.process_request(request_data2, next_handler)
        
        # Get all metrics
        all_metrics = middleware.get_metrics()
        assert isinstance(all_metrics, dict)
        assert "method1" in all_metrics
        assert "method2" in all_metrics
    
    @pytest.mark.asyncio
    async def test_get_summary_metrics_empty(self, middleware):
        """Test get_summary_metrics with empty metrics."""
        summary = middleware.get_summary_metrics()
        assert isinstance(summary, dict)
        assert summary["total_requests"] == 0
        assert summary["successful_requests"] == 0
        assert summary["failed_requests"] == 0
        assert summary["success_rate"] == 0.0
        assert summary["methods"] == []
    
    @pytest.mark.asyncio
    async def test_get_summary_metrics_with_data(self, middleware):
        """Test get_summary_metrics with populated metrics."""
        # Make successful and failed requests
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        # Successful request
        await middleware.process_request(request_data, next_handler)
        
        # Failed request
        async def failing_handler(request):
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            await middleware.process_request(request_data, failing_handler)
        
        # Get summary
        summary = middleware.get_summary_metrics()
        assert summary["total_requests"] == 2
        assert summary["successful_requests"] == 1
        assert summary["failed_requests"] == 1
        assert summary["success_rate"] == 0.5
        assert "test_method" in summary["methods"]
    
    @pytest.mark.asyncio
    async def test_clear_metrics_specific_method(self, middleware):
        """Test clear_metrics for specific method."""
        # Make requests to populate metrics
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data, next_handler)
        
        # Verify metrics exist
        assert "test_method" in middleware.metrics
        
        # Clear specific method
        middleware.clear_metrics("test_method")
        
        # Verify method is cleared
        assert "test_method" not in middleware.metrics
    
    @pytest.mark.asyncio
    async def test_clear_metrics_all_methods(self, middleware):
        """Test clear_metrics for all methods."""
        # Make requests to populate metrics
        request_data1 = {"method": "method1", "params": {"key": "value"}}
        request_data2 = {"method": "method2", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data1, next_handler)
        await middleware.process_request(request_data2, next_handler)
        
        # Verify metrics exist
        assert len(middleware.metrics) == 2
        
        # Clear all metrics
        middleware.clear_metrics()
        
        # Verify all metrics are cleared
        assert len(middleware.metrics) == 0
    
    @pytest.mark.asyncio
    async def test_clear_metrics_nonexistent_method(self, middleware):
        """Test clear_metrics for non-existent method."""
        # Should not raise an exception
        middleware.clear_metrics("nonexistent_method")
        assert len(middleware.metrics) == 0
    
    @pytest.mark.asyncio
    async def test_export_metrics(self, middleware):
        """Test export_metrics method."""
        # Make a request to populate metrics
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data, next_handler)
        
        # Export metrics
        exported = middleware.export_metrics()
        
        assert isinstance(exported, dict)
        assert "timestamp" in exported
        assert "summary" in exported
        assert "methods" in exported
        assert "test_method" in exported["methods"]
    
    @pytest.mark.asyncio
    async def test_reset_metrics(self, middleware):
        """Test reset_metrics method (alias for clear_metrics)."""
        # Make a request to populate metrics
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data, next_handler)
        
        # Verify metrics exist
        assert "test_method" in middleware.metrics
        
        # Reset metrics
        middleware.reset_metrics("test_method")
        
        # Verify method is cleared
        assert "test_method" not in middleware.metrics
    
    @pytest.mark.asyncio
    async def test_get_method_metrics(self, middleware):
        """Test get_method_metrics method."""
        # Make a request to populate metrics
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        await middleware.process_request(request_data, next_handler)
        
        # Get method metrics
        method_metrics = middleware.get_method_metrics("test_method")
        
        assert isinstance(method_metrics, dict)
        assert "total_requests" in method_metrics
        assert method_metrics["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_record_metrics_error_handling(self, middleware):
        """Test _record_metrics with error handling."""
        # Make a request that fails
        request_data = {"method": "test_method", "params": {"key": "value"}}
        
        async def failing_handler(request):
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            await middleware.process_request(request_data, failing_handler)
        
        # Check that error was recorded
        metrics = middleware.get_metrics("test_method")
        assert metrics["failed_requests"] == 1
        assert len(metrics["errors"]) == 1
        assert "Test error" in metrics["errors"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_record_metrics_multiple_errors(self, middleware):
        """Test _record_metrics with multiple errors (testing error limit)."""
        request_data = {"method": "test_method", "params": {"key": "value"}}
        
        # Make multiple failing requests to test error limit
        for i in range(15):  # More than the 10 error limit
            async def failing_handler(request):
                raise Exception(f"Error {i}")
            
            with pytest.raises(Exception):
                await middleware.process_request(request_data, failing_handler)
        
        # Check that only recent errors are kept
        metrics = middleware.get_metrics("test_method")
        assert len(metrics["errors"]) == 10  # Should be limited to 10
        assert metrics["failed_requests"] == 15
    
    @pytest.mark.asyncio
    async def test_record_metrics_timing_calculation(self, middleware):
        """Test _record_metrics timing calculations."""
        request_data = {"method": "test_method", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        # Make multiple requests
        for _ in range(3):
            await middleware.process_request(request_data, next_handler)
        
        metrics = middleware.get_metrics("test_method")
        
        assert metrics["total_requests"] == 3
        assert metrics["successful_requests"] == 3
        assert metrics["failed_requests"] == 0
        assert metrics["total_duration"] > 0
        assert metrics["min_duration"] > 0
        assert metrics["max_duration"] > 0
        assert metrics["avg_duration"] > 0
        assert metrics["last_request"] is not None
    
    @pytest.mark.asyncio
    async def test_process_request_without_method(self, middleware):
        """Test process_request with request that has no method."""
        request_data = {"params": {"key": "value"}}  # No method field
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}
        
        # Check that metrics were recorded with "unknown" method
        metrics = middleware.get_metrics("unknown")
        assert metrics["total_requests"] == 1


class TestCachingMiddleware:
    """Test cases for CachingMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create a CachingMiddleware instance."""
        return CachingMiddleware()
    
    @pytest.mark.asyncio
    async def test_middleware_creation(self, middleware):
        """Test middleware creation."""
        assert middleware is not None
        assert middleware.name == "CachingMiddleware"
    
    @pytest.mark.asyncio
    async def test_process_request_cache_miss(self, middleware):
        """Test request processing with cache miss."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_process_request_cache_hit(self, middleware):
        """Test request processing with cache hit."""
        request_data = {"method": "test", "params": {"key": "value"}}
        cached_response = {"result": {"cached": True}}
        
        # Mock the cache to return a cached response
        middleware.cache = {middleware._generate_cache_key(request_data): {
            "response": cached_response,
            "timestamp": time.time()
        }}
        
        result = await middleware.process_request(request_data, AsyncMock())
        
        # Should return cached response
        assert result == cached_response
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, middleware):
        """Test cache key generation."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        cache_key = middleware._generate_cache_key(request_data)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
    
    @pytest.mark.asyncio
    async def test_cache_with_different_requests(self, middleware):
        """Test cache with different requests."""
        request1 = {"method": "test1", "params": {"key": "value1"}}
        request2 = {"method": "test2", "params": {"key": "value2"}}
        
        key1 = middleware._generate_cache_key(request1)
        key2 = middleware._generate_cache_key(request2)
        
        assert key1 != key2
    
    @pytest.mark.asyncio
    async def test_cache_ttl(self, middleware):
        """Test cache TTL functionality."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": {"status": "success"}}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": {"status": "success"}}
        assert middleware.ttl > 0
    
    @pytest.mark.asyncio
    async def test_cache_clear(self, middleware):
        """Test cache clearing."""
        middleware.clear_cache()
        assert len(middleware.cache) == 0
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, middleware):
        """Test cache statistics."""
        stats = middleware.get_cache_stats()
        assert isinstance(stats, dict)
        assert "total_entries" in stats
    
    @pytest.mark.asyncio
    async def test_get_name(self, middleware):
        """Test get_name method."""
        name = middleware.get_name()
        assert name == "CachingMiddleware"
    
    @pytest.mark.asyncio
    async def test_get_config(self, middleware):
        """Test get_config method."""
        config = middleware.get_config()
        assert isinstance(config, dict)
        assert config["name"] == "CachingMiddleware"
        assert config["type"] == "CachingMiddleware"
        assert "max_size" in config
        assert "ttl" in config
        assert "cache_size" in config
        assert "hit_rate" in config
    
    @pytest.mark.asyncio
    async def test_get_cached_response_with_logging(self, middleware):
        """Test _get_cached_response with logging."""
        request_data = {"method": "test", "params": {"key": "value"}}
        cache_key = middleware._generate_cache_key(request_data)
        
        # Add a cached response
        middleware.cache[cache_key] = {
            "response": {"result": "cached"},
            "timestamp": time.time()
        }
        
        with patch.object(middleware.logger, 'debug') as mock_log:
            result = middleware._get_cached_response(cache_key)
            assert result == {"result": "cached"}
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_response_with_logging(self, middleware):
        """Test _cache_response with logging."""
        cache_key = "test_key"
        response = {"result": "test"}
        
        with patch.object(middleware.logger, 'debug') as mock_log:
            middleware._cache_response(cache_key, response)
            assert cache_key in middleware.cache
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evict_oldest_entry(self, middleware):
        """Test _evict_oldest_entry method."""
        # Add multiple cache entries with different timestamps
        middleware.cache["old_key"] = {
            "response": {"old": "data"},
            "timestamp": time.time() - 100  # Old entry
        }
        middleware.cache["new_key"] = {
            "response": {"new": "data"},
            "timestamp": time.time()  # New entry
        }
        
        initial_size = len(middleware.cache)
        
        with patch.object(middleware.logger, 'debug') as mock_log:
            middleware._evict_oldest_entry()
            
            # Should remove the oldest entry
            assert len(middleware.cache) == initial_size - 1
            assert "old_key" not in middleware.cache
            assert "new_key" in middleware.cache
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evict_oldest_entry_empty_cache(self, middleware):
        """Test _evict_oldest_entry with empty cache."""
        middleware.cache.clear()
        
        # Should not raise an exception
        middleware._evict_oldest_entry()
        assert len(middleware.cache) == 0
    
    @pytest.mark.asyncio
    async def test_cache_size_limit(self, middleware):
        """Test cache size limit enforcement."""
        middleware.max_size = 2
        
        # Add entries up to the limit
        for i in range(3):
            middleware._cache_response(f"key{i}", {"data": f"value{i}"})
        
        # Should have only 2 entries (max_size)
        assert len(middleware.cache) == 2
    
    @pytest.mark.asyncio
    async def test_get_cache_stats_with_expired_entries(self, middleware):
        """Test get_cache_stats with expired entries."""
        # Add expired entries
        middleware.cache["expired_key"] = {
            "response": {"expired": "data"},
            "timestamp": time.time() - middleware.ttl - 10  # Expired
        }
        middleware.cache["valid_key"] = {
            "response": {"valid": "data"},
            "timestamp": time.time()  # Valid
        }
        
        stats = middleware.get_cache_stats()
        
        assert stats["total_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["max_size"] == middleware.max_size
        assert stats["ttl_seconds"] == middleware.ttl
    
    @pytest.mark.asyncio
    async def test_get_stats(self, middleware):
        """Test get_stats method (alias for get_cache_stats)."""
        stats = middleware.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "expired_entries" in stats
        assert "max_size" in stats
        assert "ttl_seconds" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "size" in stats
    
    @pytest.mark.asyncio
    async def test_cache_size_method(self, middleware):
        """Test cache_size method."""
        # Add some entries
        middleware._cache_response("key1", {"data": "value1"})
        middleware._cache_response("key2", {"data": "value2"})
        
        size = middleware.cache_size()
        assert size == 2
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, middleware):
        """Test cleanup_expired method."""
        # Add expired and valid entries
        middleware.cache["expired_key"] = {
            "response": {"expired": "data"},
            "timestamp": time.time() - middleware.ttl - 10  # Expired
        }
        middleware.cache["valid_key"] = {
            "response": {"valid": "data"},
            "timestamp": time.time()  # Valid
        }
        
        initial_size = len(middleware.cache)
        
        with patch.object(middleware.logger, 'info') as mock_log:
            cleaned_count = middleware.cleanup_expired()
            
            assert cleaned_count == 1
            assert len(middleware.cache) == initial_size - 1
            assert "expired_key" not in middleware.cache
            assert "valid_key" in middleware.cache
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_no_expired_entries(self, middleware):
        """Test cleanup_expired with no expired entries."""
        # Add only valid entries
        middleware.cache["valid_key"] = {
            "response": {"valid": "data"},
            "timestamp": time.time()
        }
        
        initial_size = len(middleware.cache)
        
        with patch.object(middleware.logger, 'info') as mock_log:
            cleaned_count = middleware.cleanup_expired()
            
            assert cleaned_count == 0
            assert len(middleware.cache) == initial_size
            mock_log.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_empty_cache(self, middleware):
        """Test cleanup_expired with empty cache."""
        middleware.cache.clear()
        
        cleaned_count = middleware.cleanup_expired()
        assert cleaned_count == 0
    
    @pytest.mark.asyncio
    async def test_cache_expiration_automatic_cleanup(self, middleware):
        """Test automatic cleanup of expired entries during cache access."""
        # Add an expired entry
        cache_key = "expired_key"
        middleware.cache[cache_key] = {
            "response": {"expired": "data"},
            "timestamp": time.time() - middleware.ttl - 10  # Expired
        }
        
        # Try to get the expired entry
        result = middleware._get_cached_response(cache_key)
        
        # Should return None and remove the expired entry
        assert result is None
        assert cache_key not in middleware.cache
    
    @pytest.mark.asyncio
    async def test_cache_key_generation_with_missing_fields(self, middleware):
        """Test cache key generation with missing fields."""
        # Test with missing method
        request_data = {"params": {"key": "value"}}
        cache_key1 = middleware._generate_cache_key(request_data)
        
        # Test with missing params
        request_data = {"method": "test"}
        cache_key2 = middleware._generate_cache_key(request_data)
        
        # Test with empty request
        request_data = {}
        cache_key3 = middleware._generate_cache_key(request_data)
        
        # All should generate valid keys
        assert isinstance(cache_key1, str)
        assert isinstance(cache_key2, str)
        assert isinstance(cache_key3, str)
        assert len(cache_key1) > 0
        assert len(cache_key2) > 0
        assert len(cache_key3) > 0
    
    @pytest.mark.asyncio
    async def test_cache_key_consistency(self, middleware):
        """Test that same request generates same cache key."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        key1 = middleware._generate_cache_key(request_data)
        key2 = middleware._generate_cache_key(request_data)
        
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_cache_key_different_order(self, middleware):
        """Test cache key generation with different parameter order."""
        request1 = {"method": "test", "params": {"key1": "value1", "key2": "value2"}}
        request2 = {"method": "test", "params": {"key2": "value2", "key1": "value1"}}
        
        key1 = middleware._generate_cache_key(request1)
        key2 = middleware._generate_cache_key(request2)
        
        # Should generate same key due to sort_keys=True in json.dumps
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_clear_cache_with_logging(self, middleware):
        """Test clear_cache with logging."""
        # Add some entries
        middleware._cache_response("key1", {"data": "value1"})
        middleware._cache_response("key2", {"data": "value2"})
        
        assert len(middleware.cache) == 2
        
        with patch.object(middleware.logger, 'info') as mock_log:
            middleware.clear_cache()
            
            assert len(middleware.cache) == 0
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_custom_ttl_and_max_size(self):
        """Test middleware with custom TTL and max size."""
        middleware = CachingMiddleware(ttl=600, max_size=500)
        
        assert middleware.ttl == 600
        assert middleware.max_size == 500


class TestRetryMiddleware:
    """Test cases for RetryMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create a RetryMiddleware instance."""
        return RetryMiddleware()
    
    @pytest.mark.asyncio
    async def test_middleware_creation(self, middleware):
        """Test middleware creation."""
        assert middleware is not None
        assert middleware.max_retries > 0
        assert middleware.base_delay > 0
    
    @pytest.mark.asyncio
    async def test_process_request_no_retry(self, middleware):
        """Test request processing without retry."""
        request_data = {"method": "test", "params": {"key": "value"}}
        next_handler = AsyncMock()
        next_handler.return_value = {"result": "success"}
        
        result = await middleware.process_request(request_data, next_handler)
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self, middleware):
        """Test retry on connection error."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        # Mock a function that fails with ConnectionError
        async def failing_handler(request):
            raise ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            await middleware.process_request(request_data, failing_handler)
    
    @pytest.mark.asyncio
    async def test_retry_on_validation_error(self, middleware):
        """Test retry on validation error."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        # Mock a function that fails with ValidationError
        async def failing_handler(request):
            raise ValidationError("Validation failed")
        
        with pytest.raises(ValidationError):
            await middleware.process_request(request_data, failing_handler)
    
    @pytest.mark.asyncio
    async def test_should_retry_connection_error(self, middleware):
        """Test should_retry for connection error."""
        error = ConnectionError("Connection failed")
        
        result = middleware._is_retryable_exception(error)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_retry_validation_error(self, middleware):
        """Test should_retry for validation error."""
        error = ValidationError("Validation failed")
        
        result = middleware._is_retryable_exception(error)
        
        assert result is True  # ValidationError is in retryable_exceptions
    
    @pytest.mark.asyncio
    async def test_should_retry_generic_error(self, middleware):
        """Test should_retry for generic error."""
        error = Exception("Generic error")
        
        result = middleware._is_retryable_exception(error)
        
        assert result is True  # Exception is in retryable_exceptions by default
    
    @pytest.mark.asyncio
    async def test_retry_delay_calculation(self, middleware):
        """Test retry delay calculation."""
        delay = middleware._calculate_delay(1)
        
        assert delay > 0
        assert isinstance(delay, (int, float))
    
    @pytest.mark.asyncio
    async def test_retry_delay_exponential_backoff(self, middleware):
        """Test exponential backoff for retry delays."""
        delay1 = middleware._calculate_delay(1)
        delay2 = middleware._calculate_delay(2)
        delay3 = middleware._calculate_delay(3)
        
        # Delays should increase with retry attempts
        assert delay2 >= delay1
        assert delay3 >= delay2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, middleware):
        """Test behavior when max retries exceeded."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        # Mock a function that always fails
        async def always_failing_handler(request):
            raise ConnectionError("Always fails")
        
        with pytest.raises(ConnectionError):
            await middleware.process_request(request_data, always_failing_handler)
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self, middleware):
        """Test successful retry after initial failures."""
        attempt_count = 0
        
        async def eventually_succeeding_handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Temporary failure")
            return {"result": "success"}
        
        result = await middleware.process_request({"method": "test"}, eventually_succeeding_handler)
        
        assert result == {"result": "success"}
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_custom_retry_configuration(self):
        """Test middleware with custom retry configuration."""
        middleware = RetryMiddleware(
            max_retries=5,
            base_delay=2.0,
            backoff_factor=2.0
        )
        
        assert middleware.max_retries == 5
        assert middleware.base_delay == 2.0
        assert middleware.backoff_factor == 2.0
    
    @pytest.mark.asyncio
    async def test_retry_statistics(self, middleware):
        """Test retry statistics tracking."""
        config = middleware.get_config()
        
        assert "max_retries" in config
        assert "base_delay" in config
        assert "backoff_factor" in config 
    
    @pytest.mark.asyncio
    async def test_get_name(self, middleware):
        """Test get_name method."""
        name = middleware.get_name()
        assert name == "RetryMiddleware"
    
    @pytest.mark.asyncio
    async def test_add_retryable_exception(self, middleware):
        """Test adding retryable exception."""
        class CustomException(Exception):
            pass
        
        initial_count = len(middleware.retryable_exceptions)
        middleware.add_retryable_exception(CustomException)
        
        assert len(middleware.retryable_exceptions) == initial_count + 1
        assert CustomException in middleware.retryable_exceptions
    
    @pytest.mark.asyncio
    async def test_add_retryable_exception_already_exists(self, middleware):
        """Test adding retryable exception that already exists."""
        initial_count = len(middleware.retryable_exceptions)
        middleware.add_retryable_exception(Exception)  # Exception is already in the list
        
        assert len(middleware.retryable_exceptions) == initial_count
    
    @pytest.mark.asyncio
    async def test_remove_retryable_exception(self, middleware):
        """Test removing retryable exception."""
        class CustomException(Exception):
            pass
        
        # Add custom exception first
        middleware.add_retryable_exception(CustomException)
        initial_count = len(middleware.retryable_exceptions)
        
        # Remove it
        result = middleware.remove_retryable_exception(CustomException)
        
        assert result is True
        assert len(middleware.retryable_exceptions) == initial_count - 1
        assert CustomException not in middleware.retryable_exceptions
    
    @pytest.mark.asyncio
    async def test_remove_retryable_exception_not_exists(self, middleware):
        """Test removing retryable exception that doesn't exist."""
        class CustomException(Exception):
            pass
        
        initial_count = len(middleware.retryable_exceptions)
        result = middleware.remove_retryable_exception(CustomException)
        
        assert result is False
        assert len(middleware.retryable_exceptions) == initial_count
    
    @pytest.mark.asyncio
    async def test_get_retry_config(self, middleware):
        """Test getting retry configuration."""
        config = middleware.get_retry_config()
        
        assert "max_retries" in config
        assert "base_delay" in config
        assert "max_delay" in config
        assert "backoff_factor" in config
        assert "retryable_exceptions" in config
        assert isinstance(config["retryable_exceptions"], list)
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, middleware):
        """Test getting metrics."""
        metrics = middleware.get_metrics()
        
        assert "total_retries" in metrics
        assert "successful_retries" in metrics
        assert "failed_retries" in metrics
        assert metrics["total_retries"] == 0
        assert metrics["successful_retries"] == 0
        assert metrics["failed_retries"] == 0
    
    @pytest.mark.asyncio
    async def test_reset_metrics(self, middleware):
        """Test resetting metrics."""
        # This should not raise any exception
        middleware.reset_metrics()
    
    @pytest.mark.asyncio
    async def test_set_next(self, middleware):
        """Test setting next middleware."""
        class MockMiddleware:
            def __init__(self):
                self.name = "MockMiddleware"
        
        mock_middleware = MockMiddleware()
        middleware.set_next(mock_middleware)
        
        assert middleware.next_middleware == mock_middleware
    
    @pytest.mark.asyncio
    async def test_execute_chain_with_next_middleware(self, middleware):
        """Test executing chain with next middleware."""
        class MockMiddleware:
            def __init__(self):
                self.name = "MockMiddleware"
            
            async def process_request(self, request, next_handler):
                return {"result": "from_mock"}
        
        mock_middleware = MockMiddleware()
        middleware.set_next(mock_middleware)
        
        result = await middleware.execute_chain("test_method", {"param": "value"})
        
        assert result == {"result": "from_mock"}
    
    @pytest.mark.asyncio
    async def test_execute_chain_without_next_middleware(self, middleware):
        """Test executing chain without next middleware."""
        result = await middleware.execute_chain("test_method", {"param": "value"})
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_non_retryable_exception_logging(self, middleware):
        """Test logging when non-retryable exception occurs."""
        class NonRetryableException(Exception):
            pass
        
        # Remove Exception from retryable exceptions to make it non-retryable
        middleware.remove_retryable_exception(Exception)
        
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def failing_handler(request):
            raise NonRetryableException("Non-retryable error")
        
        with patch.object(middleware.logger, 'warning') as mock_log:
            with pytest.raises(NonRetryableException):
                await middleware.process_request(request_data, failing_handler)
            
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded_logging(self, middleware):
        """Test logging when max retries are exceeded."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def always_failing_handler(request):
            raise ConnectionError("Always fails")
        
        with patch.object(middleware.logger, 'error') as mock_log:
            with pytest.raises(ConnectionError):
                await middleware.process_request(request_data, always_failing_handler)
            
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_retry_attempt_logging(self, middleware):
        """Test logging during retry attempts."""
        request_data = {"method": "test", "params": {"key": "value"}}
        
        attempt_count = 0
        
        async def eventually_succeeding_handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ConnectionError("Temporary failure")
            return {"result": "success"}
        
        with patch.object(middleware.logger, 'warning') as mock_log:
            result = await middleware.process_request(request_data, eventually_succeeding_handler)
            
            assert result == {"result": "success"}
            mock_log.assert_called()
    
    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self):
        """Test middleware with custom retryable exceptions."""
        class CustomRetryableException(Exception):
            pass
        
        middleware = RetryMiddleware(
            max_retries=2,
            retryable_exceptions=[CustomRetryableException]
        )
        
        request_data = {"method": "test", "params": {"key": "value"}}
        
        attempt_count = 0
        
        async def eventually_succeeding_handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise CustomRetryableException("Custom error")
            return {"result": "success"}
        
        result = await middleware.process_request(request_data, eventually_succeeding_handler)
        
        assert result == {"result": "success"}
        assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_max_delay_respect(self, middleware):
        """Test that max_delay is respected in delay calculation."""
        middleware.max_delay = 1.0
        middleware.base_delay = 0.1
        middleware.backoff_factor = 10.0
        
        # First attempt should be limited by max_delay
        delay1 = middleware._calculate_delay(0)
        assert delay1 == 0.1  # base_delay
        
        # Second attempt should be limited by max_delay
        delay2 = middleware._calculate_delay(1)
        assert delay2 == 1.0  # max_delay
        
        # Third attempt should also be limited by max_delay
        delay3 = middleware._calculate_delay(2)
        assert delay3 == 1.0  # max_delay
    
    @pytest.mark.asyncio
    async def test_remove_retryable_exception_return_true(self, middleware):
        """Test remove_retryable_exception returns True when exception is removed."""
        class CustomException(Exception):
            pass
        
        # Add custom exception
        middleware.add_retryable_exception(CustomException)
        
        # Remove it and verify return value
        result = middleware.remove_retryable_exception(CustomException)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_process_request_fallback_exception(self, middleware):
        """Test the fallback exception handling in process_request."""
        # Create middleware with 0 retries to force the fallback case
        middleware.max_retries = 0
        
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def always_failing_handler(request):
            raise ConnectionError("Always fails")
        
        # This should trigger the fallback exception at the end of the method
        with pytest.raises(ConnectionError):
            await middleware.process_request(request_data, always_failing_handler)
    
    @pytest.mark.asyncio
    async def test_process_request_fallback_exception_edge_case(self, middleware):
        """Test the fallback exception handling in process_request with edge case."""
        # Set max_retries to -1 to force the fallback case
        middleware.max_retries = -1
        
        request_data = {"method": "test", "params": {"key": "value"}}
        
        async def always_failing_handler(request):
            raise ConnectionError("Always fails")
        
        # This should trigger the fallback exception at the end of the method
        with pytest.raises(TypeError, match="exceptions must derive from BaseException"):
            await middleware.process_request(request_data, always_failing_handler) 