"""
Tests for performance monitor functionality.

This module contains comprehensive tests for the PerformanceMonitor class
to ensure proper performance monitoring capabilities.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from vector_store_client.monitoring.performance_monitor import PerformanceMonitor


class TestPerformanceMonitorExtended:
    """Test extended performance monitor functionality."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor instance."""
        return PerformanceMonitor()
    
    def test_get_name(self, performance_monitor):
        """Test get_name method."""
        assert performance_monitor.get_name() == "PerformanceMonitor"
    
    def test_get_config(self, performance_monitor):
        """Test get_config method."""
        config = performance_monitor.get_config()
        assert config["name"] == "PerformanceMonitor"
        assert "uptime" in config
        assert config["operation_count"] == 0
        assert config["metrics_count"] == 0
    
    def test_record_operation_basic(self, performance_monitor):
        """Test basic operation recording."""
        performance_monitor.record_operation(
            "test_operation",
            duration=1.5,
            success=True
        )
        
        assert "test_operation" in performance_monitor.metrics
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["count"] == 1
        assert metrics["total_duration"] == 1.5
        assert metrics["success_count"] == 1
        assert metrics["failed_count"] == 0
        assert metrics["min_duration"] == 1.5
        assert metrics["max_duration"] == 1.5
        assert metrics["avg_duration"] == 1.5
        assert performance_monitor.operation_count == 1
    
    def test_record_operation_failed(self, performance_monitor):
        """Test recording failed operation."""
        performance_monitor.record_operation(
            "test_operation",
            duration=2.0,
            success=False
        )
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["success_count"] == 0
        assert metrics["failed_count"] == 1
    
    def test_record_operation_with_result_count(self, performance_monitor):
        """Test recording operation with result count."""
        performance_monitor.record_operation(
            "test_operation",
            duration=1.0,
            success=True,
            result_count=10
        )
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["total_results"] == 10
    
    def test_record_operation_with_memory_usage(self, performance_monitor):
        """Test recording operation with memory usage."""
        performance_monitor.record_operation(
            "test_operation",
            duration=1.0,
            success=True,
            memory_usage=1024 * 1024  # 1MB
        )
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["total_memory"] == 1024 * 1024
        assert metrics["avg_memory"] == 1024 * 1024
    
    def test_record_operation_multiple(self, performance_monitor):
        """Test recording multiple operations."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        performance_monitor.record_operation("test_operation", 2.0, True)
        performance_monitor.record_operation("test_operation", 0.5, False)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["count"] == 3
        assert metrics["total_duration"] == 3.5
        assert metrics["success_count"] == 2
        assert metrics["failed_count"] == 1
        assert metrics["min_duration"] == 0.5
        assert metrics["max_duration"] == 2.0
        assert metrics["avg_duration"] == 3.5 / 3
        assert performance_monitor.operation_count == 3
    
    def test_get_operation_metrics_existing(self, performance_monitor):
        """Test getting metrics for existing operation."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        metrics = performance_monitor.get_operation_metrics("test_operation")
        assert metrics["count"] == 1
        assert metrics["total_duration"] == 1.0
        assert metrics["success_count"] == 1
    
    def test_get_operation_metrics_non_existent(self, performance_monitor):
        """Test getting metrics for non-existent operation."""
        metrics = performance_monitor.get_operation_metrics("non_existent")
        assert metrics == {}
    
    def test_get_summary_empty(self, performance_monitor):
        """Test getting summary with no operations."""
        summary = performance_monitor.get_summary()
        
        assert "uptime" in summary
        assert summary["total_operations"] == 0
        assert summary["operations"] == {}
    
    def test_get_summary_with_operations(self, performance_monitor):
        """Test getting summary with operations."""
        performance_monitor.record_operation("op1", 1.0, True)
        performance_monitor.record_operation("op2", 2.0, False)
        
        summary = performance_monitor.get_summary()
        
        assert summary["total_operations"] == 2
        assert summary["successful_operations"] == 1
        assert summary["failed_operations"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["total_duration"] == 3.0
        assert summary["avg_duration"] == 1.5
        assert "memory_usage_bytes" in summary
        assert "memory_usage_mb" in summary
        assert "operations" in summary
        assert "op1" in summary["operations"]
        assert "op2" in summary["operations"]
    
    def test_get_summary_with_psutil_error(self, performance_monitor):
        """Test getting summary when psutil fails."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        with patch('psutil.Process', side_effect=Exception("Test error")):
            summary = performance_monitor.get_summary()
            
            assert summary["memory_usage_bytes"] == 0
            assert summary["memory_usage_mb"] == 0
    
    def test_get_memory_usage_success(self, performance_monitor):
        """Test getting memory usage successfully."""
        with patch('psutil.Process') as mock_process:
            mock_memory_info = Mock()
            mock_memory_info.rss = 1024 * 1024  # 1MB
            mock_memory_info.vms = 2048 * 1024  # 2MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            mock_process.return_value.memory_percent.return_value = 5.0
            
            memory_usage = performance_monitor.get_memory_usage()
            
            assert memory_usage["rss_bytes"] == 1024 * 1024
            assert memory_usage["vms_bytes"] == 2048 * 1024
            assert memory_usage["rss_mb"] == 1.0
            assert memory_usage["vms_mb"] == 2.0
            assert memory_usage["percent"] == 5.0
    
    def test_get_memory_usage_error(self, performance_monitor):
        """Test getting memory usage when psutil fails."""
        with patch('psutil.Process', side_effect=Exception("Test error")):
            memory_usage = performance_monitor.get_memory_usage()
            
            assert "error" in memory_usage
            assert memory_usage["error"] == "Test error"
            assert memory_usage["rss_bytes"] == 0
            assert memory_usage["vms_bytes"] == 0
            assert memory_usage["rss_mb"] == 0
            assert memory_usage["vms_mb"] == 0
            assert memory_usage["percent"] == 0
    
    def test_clear_metrics_specific(self, performance_monitor):
        """Test clearing metrics for specific operation."""
        performance_monitor.record_operation("op1", 1.0, True)
        performance_monitor.record_operation("op2", 2.0, True)
        
        performance_monitor.clear_metrics("op1")
        
        assert "op1" not in performance_monitor.metrics
        assert "op2" in performance_monitor.metrics
    
    def test_clear_metrics_all(self, performance_monitor):
        """Test clearing all metrics."""
        performance_monitor.record_operation("op1", 1.0, True)
        performance_monitor.record_operation("op2", 2.0, True)
        
        performance_monitor.clear_metrics()
        
        assert len(performance_monitor.metrics) == 0
    
    def test_clear_metrics_non_existent(self, performance_monitor):
        """Test clearing metrics for non-existent operation."""
        # Should not raise an error
        performance_monitor.clear_metrics("non_existent")
        
        # Should not affect other operations
        performance_monitor.record_operation("existing_op", 1.0, True)
        performance_monitor.clear_metrics("non_existent")
        
        assert "existing_op" in performance_monitor.metrics
    
    def test_export_metrics(self, performance_monitor):
        """Test exporting metrics."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        exported = performance_monitor.export_metrics()
        
        assert "timestamp" in exported
        assert "summary" in exported
        assert "memory_usage" in exported
        assert "operations" in exported
        assert "test_operation" in exported["operations"]


class TestPerformanceMonitorEdgeCases:
    """Test performance monitor edge cases."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor instance."""
        return PerformanceMonitor()
    
    def test_record_operation_zero_duration(self, performance_monitor):
        """Test recording operation with zero duration."""
        performance_monitor.record_operation("test_operation", 0.0, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["min_duration"] == 0.0
        assert metrics["max_duration"] == 0.0
        assert metrics["avg_duration"] == 0.0
    
    def test_record_operation_negative_duration(self, performance_monitor):
        """Test recording operation with negative duration."""
        performance_monitor.record_operation("test_operation", -1.0, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["min_duration"] == -1.0
        # max_duration starts as 0.0, so negative value won't update it
        assert metrics["max_duration"] == 0.0
        assert metrics["avg_duration"] == -1.0
    
    def test_record_operation_without_result_count(self, performance_monitor):
        """Test recording operation without result count."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["total_results"] == 0
    
    def test_record_operation_without_memory_usage(self, performance_monitor):
        """Test recording operation without memory usage."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["total_memory"] == 0.0
        assert metrics["avg_memory"] == 0.0
    
    def test_record_operation_multiple_memory_updates(self, performance_monitor):
        """Test recording multiple operations with memory usage."""
        performance_monitor.record_operation("test_operation", 1.0, True, memory_usage=1024)
        performance_monitor.record_operation("test_operation", 2.0, True, memory_usage=2048)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["total_memory"] == 3072
        assert metrics["avg_memory"] == 1536
    
    def test_get_summary_zero_operations(self, performance_monitor):
        """Test getting summary with zero operations."""
        summary = performance_monitor.get_summary()
        
        # When no operations, success_rate and avg_duration are not in summary
        assert "success_rate" not in summary
        assert "avg_duration" not in summary
        assert summary["total_operations"] == 0
    
    def test_get_summary_all_failed_operations(self, performance_monitor):
        """Test getting summary with all failed operations."""
        performance_monitor.record_operation("test_operation", 1.0, False)
        performance_monitor.record_operation("test_operation", 2.0, False)
        
        summary = performance_monitor.get_summary()
        
        assert summary["successful_operations"] == 0
        assert summary["failed_operations"] == 2
        assert summary["success_rate"] == 0
    
    def test_get_summary_all_successful_operations(self, performance_monitor):
        """Test getting summary with all successful operations."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        performance_monitor.record_operation("test_operation", 2.0, True)
        
        summary = performance_monitor.get_summary()
        
        assert summary["successful_operations"] == 2
        assert summary["failed_operations"] == 0
        assert summary["success_rate"] == 1.0
    
    def test_operation_count_increment(self, performance_monitor):
        """Test that operation count increments correctly."""
        assert performance_monitor.operation_count == 0
        
        performance_monitor.record_operation("op1", 1.0, True)
        assert performance_monitor.operation_count == 1
        
        performance_monitor.record_operation("op2", 2.0, False)
        assert performance_monitor.operation_count == 2
    
    def test_last_operation_timestamp(self, performance_monitor):
        """Test that last operation timestamp is recorded."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert "last_operation" in metrics
        assert metrics["last_operation"] is not None
        
        # Should be a valid ISO format timestamp
        from datetime import datetime
        datetime.fromisoformat(metrics["last_operation"])
    
    def test_multiple_operations_same_name(self, performance_monitor):
        """Test recording multiple operations with same name."""
        performance_monitor.record_operation("test_operation", 1.0, True)
        performance_monitor.record_operation("test_operation", 2.0, False)
        performance_monitor.record_operation("test_operation", 0.5, True)
        
        metrics = performance_monitor.metrics["test_operation"]
        assert metrics["count"] == 3
        assert metrics["success_count"] == 2
        assert metrics["failed_count"] == 1
        assert metrics["min_duration"] == 0.5
        assert metrics["max_duration"] == 2.0
        assert metrics["avg_duration"] == 3.5 / 3
    
    def test_clear_metrics_operation_count_unchanged(self, performance_monitor):
        """Test that clearing metrics doesn't affect operation count."""
        performance_monitor.record_operation("op1", 1.0, True)
        performance_monitor.record_operation("op2", 2.0, True)
        
        original_count = performance_monitor.operation_count
        performance_monitor.clear_metrics("op1")
        
        assert performance_monitor.operation_count == original_count 