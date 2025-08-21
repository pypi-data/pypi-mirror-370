"""
Tests for health checker functionality.

This module contains comprehensive tests for the HealthChecker class
to ensure proper health monitoring capabilities.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from vector_store_client.monitoring.health_checker import HealthChecker


class TestHealthCheckerExtended:
    """Test extended health checker functionality."""
    
    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        return HealthChecker()
    
    def test_get_name(self, health_checker):
        """Test get_name method."""
        assert health_checker.get_name() == "HealthChecker"
    
    def test_get_config_before_check(self, health_checker):
        """Test get_config before any health checks."""
        config = health_checker.get_config()
        assert config["name"] == "HealthChecker"
        assert config["health_checks_count"] == 0
        assert config["last_check_time"] is None
    
    def test_get_config_after_check(self, health_checker):
        """Test get_config after health checks."""
        # Simulate a check time
        health_checker.last_check_time = datetime(2023, 1, 1, 0, 0, 0)
        health_checker.health_checks["test"] = {"function": lambda: None, "interval": 300}
        
        config = health_checker.get_config()
        assert config["name"] == "HealthChecker"
        assert config["health_checks_count"] == 1
        assert config["last_check_time"] == "2023-01-01T00:00:00"
    
    @pytest.mark.asyncio
    async def test_check_system_health_basic(self, health_checker):
        """Test basic system health check."""
        result = await health_checker.check_system_health()
        
        assert "overall_status" in result
        assert "components" in result
        assert "timestamp" in result
        assert "warnings" in result
        assert "errors" in result
    
    @pytest.mark.asyncio
    async def test_check_system_health_exception(self, health_checker):
        """Test system health check with exception."""
        # Mock the individual health check methods to raise exceptions
        with patch.object(health_checker, '_check_memory_health', side_effect=Exception("Test error")):
            result = await health_checker.check_system_health()
            
            assert result["overall_status"] == "error"
            assert "errors" in result
            assert len(result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_memory_health_check(self, health_checker):
        """Test memory health check."""
        result = await health_checker._check_memory_health()
        
        assert "status" in result
        # Status can be "healthy", "warning", "error", or "unknown" depending on system
        assert result["status"] in ["healthy", "warning", "error", "unknown"]
    
    @pytest.mark.asyncio
    async def test_cpu_health_check(self, health_checker):
        """Test CPU health check."""
        result = await health_checker._check_cpu_health()
        
        assert "status" in result
        # Status can be "healthy", "warning", "error", or "unknown" depending on system
        assert result["status"] in ["healthy", "warning", "error", "unknown"]
    
    @pytest.mark.asyncio
    async def test_disk_health_check(self, health_checker):
        """Test disk health check."""
        result = await health_checker._check_disk_health()
        
        assert "status" in result
        # Status can be "healthy", "warning", "error", or "unknown" depending on system
        assert result["status"] in ["healthy", "warning", "error", "unknown"]
    
    @pytest.mark.asyncio
    async def test_network_health_check(self, health_checker):
        """Test network health check."""
        result = await health_checker._check_network_health()
        
        assert "status" in result
        # Status can be "healthy", "warning", "error", or "unknown" depending on system
        assert result["status"] in ["healthy", "warning", "error", "unknown"]
    
    def test_add_custom_health_check(self, health_checker):
        """Test adding custom health check."""
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("test_check", test_check, 300)
        
        assert "test_check" in health_checker.health_checks
        assert health_checker.health_checks["test_check"]["function"] == test_check
        assert health_checker.health_checks["test_check"]["interval"] == 300
        assert health_checker.health_checks["test_check"]["last_run"] is None
        assert health_checker.health_checks["test_check"]["last_result"] is None
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_success(self, health_checker):
        """Test running custom health checks successfully."""
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("test_check", test_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "test_check" in result
        assert result["test_check"]["status"] == "success"
        assert "result" in result["test_check"]
        assert "timestamp" in result["test_check"]
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_async(self, health_checker):
        """Test running async custom health checks."""
        async def async_test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("async_check", async_test_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "async_check" in result
        assert result["async_check"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_error(self, health_checker):
        """Test running custom health checks with error."""
        def failing_check():
            raise Exception("Test error")
        
        health_checker.add_custom_health_check("failing_check", failing_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "failing_check" in result
        assert result["failing_check"]["status"] == "error"
        assert "error" in result["failing_check"]
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_cached(self, health_checker):
        """Test running custom health checks with cached results."""
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("test_check", test_check, 300)
        
        # Run first time
        result1 = await health_checker.run_custom_health_checks()
        assert result1["test_check"]["status"] == "success"
        
        # Run again immediately (should be cached)
        result2 = await health_checker.run_custom_health_checks()
        assert result2["test_check"]["status"] == "cached"
    
    def test_get_health_summary(self, health_checker):
        """Test getting health summary."""
        # Add some custom checks
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("check1", test_check, 300)
        health_checker.add_custom_health_check("check2", test_check, 600)
        
        summary = health_checker.get_health_summary()
        
        assert "last_check_time" in summary
        assert "custom_checks_count" in summary
        assert "custom_checks" in summary
        assert summary["custom_checks_count"] == 2
        assert "check1" in summary["custom_checks"]
        assert "check2" in summary["custom_checks"]
    
    def test_get_health_summary_no_checks(self, health_checker):
        """Test getting health summary with no custom checks."""
        summary = health_checker.get_health_summary()
        
        assert "last_check_time" in summary
        assert "custom_checks_count" in summary
        assert "custom_checks" in summary
        assert summary["custom_checks_count"] == 0
        assert len(summary["custom_checks"]) == 0


class TestHealthCheckerEdgeCases:
    """Test health checker edge cases."""
    
    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        return HealthChecker()
    
    @pytest.mark.asyncio
    async def test_check_system_health_all_components_error(self, health_checker):
        """Test system health check when all components have errors."""
        with patch.object(health_checker, '_check_memory_health', return_value={"status": "error"}):
            with patch.object(health_checker, '_check_cpu_health', return_value={"status": "error"}):
                with patch.object(health_checker, '_check_disk_health', return_value={"status": "error"}):
                    with patch.object(health_checker, '_check_network_health', return_value={"status": "error"}):
                        result = await health_checker.check_system_health()
                        
                        assert result["overall_status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_check_system_health_mixed_statuses(self, health_checker):
        """Test system health check with mixed component statuses."""
        with patch.object(health_checker, '_check_memory_health', return_value={"status": "healthy"}):
            with patch.object(health_checker, '_check_cpu_health', return_value={"status": "warning"}):
                with patch.object(health_checker, '_check_disk_health', return_value={"status": "healthy"}):
                    with patch.object(health_checker, '_check_network_health', return_value={"status": "error"}):
                        result = await health_checker.check_system_health()
                        
                        assert result["overall_status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_check_system_health_warning_only(self, health_checker):
        """Test system health check with only warnings."""
        with patch.object(health_checker, '_check_memory_health', return_value={"status": "warning"}):
            with patch.object(health_checker, '_check_cpu_health', return_value={"status": "warning"}):
                with patch.object(health_checker, '_check_disk_health', return_value={"status": "healthy"}):
                    with patch.object(health_checker, '_check_network_health', return_value={"status": "healthy"}):
                        result = await health_checker.check_system_health()
                        
                        assert result["overall_status"] == "degraded"
    
    def test_add_custom_health_check_duplicate(self, health_checker):
        """Test adding duplicate custom health check."""
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("test_check", test_check, 300)
        health_checker.add_custom_health_check("test_check", test_check, 600)  # Overwrite
        
        assert "test_check" in health_checker.health_checks
        assert health_checker.health_checks["test_check"]["interval"] == 600
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_empty(self, health_checker):
        """Test running custom health checks with no checks."""
        result = await health_checker.run_custom_health_checks()
        
        assert isinstance(result, dict)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_interval_not_reached(self, health_checker):
        """Test running custom health checks when interval not reached."""
        def test_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("test_check", test_check, 300)
        
        # Run first time
        result1 = await health_checker.run_custom_health_checks()
        assert result1["test_check"]["status"] == "success"
        
        # Run again immediately (should be cached)
        result2 = await health_checker.run_custom_health_checks()
        assert result2["test_check"]["status"] == "cached"
        assert "result" in result2["test_check"]
    
    def test_get_health_summary_with_last_check_time(self, health_checker):
        """Test getting health summary with last check time."""
        health_checker.last_check_time = datetime(2023, 1, 1, 0, 0, 0)
        
        summary = health_checker.get_health_summary()
        
        assert summary["last_check_time"] == "2023-01-01T00:00:00"
        assert summary["custom_checks_count"] == 0


class TestHealthCheckerErrorHandling:
    """Test health checker error handling."""
    
    @pytest.fixture
    def health_checker(self):
        """Create health checker instance."""
        return HealthChecker()
    

    
    @pytest.mark.asyncio
    async def test_memory_health_check_exception(self, health_checker):
        """Test memory health check with exception."""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = MagicMock()
            mock_import.return_value.virtual_memory.side_effect = Exception("Test error")
            
            result = await health_checker._check_memory_health()
            
            assert result["status"] == "error"
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cpu_health_check_exception(self, health_checker):
        """Test CPU health check with exception."""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = MagicMock()
            mock_import.return_value.cpu_percent.side_effect = Exception("Test error")
            
            result = await health_checker._check_cpu_health()
            
            assert result["status"] == "error"
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_disk_health_check_exception(self, health_checker):
        """Test disk health check with exception."""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = MagicMock()
            mock_import.return_value.disk_usage.side_effect = Exception("Test error")
            
            result = await health_checker._check_disk_health()
            
            assert result["status"] == "error"
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_network_health_check_exception(self, health_checker):
        """Test network health check with exception."""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = MagicMock()
            mock_import.return_value.net_io_counters.side_effect = Exception("Test error")
            
            result = await health_checker._check_network_health()
            
            assert result["status"] == "error"
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_network_health_check_timeout(self, health_checker):
        """Test network health check with timeout."""
        with patch('builtins.__import__') as mock_import:
            mock_psutil = MagicMock()
            mock_net_io = MagicMock()
            mock_net_io.bytes_sent = 1000
            mock_net_io.bytes_recv = 2000
            mock_net_io.packets_sent = 10
            mock_net_io.packets_recv = 20
            mock_psutil.net_io_counters.return_value = mock_net_io
            mock_import.return_value = mock_psutil
            
            # Mock asyncio.wait_for to raise TimeoutError
            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
                result = await health_checker._check_network_health()
                
                assert result["status"] == "warning"
                assert "connectivity" in result
                assert result["connectivity"] == "slow"
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_sync_function(self, health_checker):
        """Test running custom health checks with sync function."""
        def sync_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("sync_check", sync_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "sync_check" in result
        assert result["sync_check"]["status"] == "success"
        assert "result" in result["sync_check"]
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_async_function(self, health_checker):
        """Test running custom health checks with async function."""
        async def async_check():
            return {"status": "healthy"}
        
        health_checker.add_custom_health_check("async_check", async_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "async_check" in result
        assert result["async_check"]["status"] == "success"
        assert "result" in result["async_check"]
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_function_exception(self, health_checker):
        """Test running custom health checks with function exception."""
        def failing_check():
            raise Exception("Test error")
        
        health_checker.add_custom_health_check("failing_check", failing_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "failing_check" in result
        assert result["failing_check"]["status"] == "error"
        assert "error" in result["failing_check"]
        assert "Test error" in result["failing_check"]["error"]
    
    @pytest.mark.asyncio
    async def test_run_custom_health_checks_async_function_exception(self, health_checker):
        """Test running custom health checks with async function exception."""
        async def async_failing_check():
            raise Exception("Test async error")
        
        health_checker.add_custom_health_check("async_failing_check", async_failing_check, 300)
        
        result = await health_checker.run_custom_health_checks()
        
        assert "async_failing_check" in result
        assert result["async_failing_check"]["status"] == "error"
        assert "error" in result["async_failing_check"]
        assert "Test async error" in result["async_failing_check"]["error"] 