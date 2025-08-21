"""
Tests for metrics collector functionality.

This module contains comprehensive tests for the MetricsCollector class
to ensure proper metrics collection and aggregation capabilities.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from vector_store_client.monitoring.metrics_collector import MetricsCollector


class TestMetricsCollectorExtended:
    """Test extended metrics collector functionality."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector instance."""
        return MetricsCollector(max_history=1000)
    
    def test_get_name(self, metrics_collector):
        """Test get_name method."""
        assert metrics_collector.get_name() == "MetricsCollector"
    
    def test_get_config(self, metrics_collector):
        """Test get_config method."""
        config = metrics_collector.get_config()
        assert config["name"] == "MetricsCollector"
        assert config["max_history"] == 1000
        assert config["metrics_count"] == 0
        assert config["aggregations_count"] == 0
    
    def test_record_metric_basic(self, metrics_collector):
        """Test basic metric recording."""
        metrics_collector.record_metric("test_metric", 42.0)
        
        assert "test_metric" in metrics_collector.metrics
        assert len(metrics_collector.metrics["test_metric"]) == 1
        
        metric_data = metrics_collector.metrics["test_metric"][0]
        assert metric_data["value"] == 42.0
        assert "timestamp" in metric_data
        assert metric_data["tags"] == {}
    
    def test_record_metric_with_tags(self, metrics_collector):
        """Test metric recording with tags."""
        tags = {"service": "test", "version": "1.0"}
        metrics_collector.record_metric("test_metric", 42.0, tags=tags)
        
        metric_data = metrics_collector.metrics["test_metric"][0]
        assert metric_data["tags"] == tags
    
    def test_record_metric_with_timestamp(self, metrics_collector):
        """Test metric recording with custom timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        metrics_collector.record_metric("test_metric", 42.0, timestamp=timestamp)
        
        metric_data = metrics_collector.metrics["test_metric"][0]
        assert metric_data["timestamp"] == timestamp
    
    def test_get_metric_history_empty(self, metrics_collector):
        """Test getting metric history for non-existent metric."""
        history = metrics_collector.get_metric_history("non_existent")
        assert history == []
    
    def test_get_metric_history_basic(self, metrics_collector):
        """Test getting metric history."""
        metrics_collector.record_metric("test_metric", 42.0)
        metrics_collector.record_metric("test_metric", 43.0)
        
        history = metrics_collector.get_metric_history("test_metric")
        assert len(history) == 2
        assert history[0]["value"] == 42.0
        assert history[1]["value"] == 43.0
    
    def test_get_metric_history_with_time_window(self, metrics_collector):
        """Test getting metric history with time window."""
        # Record metrics with different timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        new_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        
        metrics_collector.record_metric("test_metric", 42.0, timestamp=old_timestamp)
        metrics_collector.record_metric("test_metric", 43.0, timestamp=new_timestamp)
        
        # Get history for last 2 hours
        history = metrics_collector.get_metric_history("test_metric", hours=2)
        assert len(history) == 1
        assert history[0]["value"] == 43.0
    
    def test_get_metric_summary_empty(self, metrics_collector):
        """Test getting metric summary for non-existent metric."""
        summary = metrics_collector.get_metric_summary("non_existent")
        
        assert summary["metric_name"] == "non_existent"
        assert summary["count"] == 0
        assert summary["min"] is None
        assert summary["max"] is None
        assert summary["avg"] is None
        assert summary["sum"] is None
    
    def test_get_metric_summary_basic(self, metrics_collector):
        """Test getting metric summary."""
        metrics_collector.record_metric("test_metric", 10.0)
        metrics_collector.record_metric("test_metric", 20.0)
        metrics_collector.record_metric("test_metric", 30.0)
        
        summary = metrics_collector.get_metric_summary("test_metric")
        
        assert summary["metric_name"] == "test_metric"
        assert summary["count"] == 3
        assert summary["min"] == 10.0
        assert summary["max"] == 30.0
        assert summary["avg"] == 20.0
        assert summary["sum"] == 60.0
        assert summary["latest"] == 30.0
        assert "latest_timestamp" in summary
    
    def test_get_metric_summary_with_time_window(self, metrics_collector):
        """Test getting metric summary with time window."""
        # Record metrics with different timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        new_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        
        metrics_collector.record_metric("test_metric", 10.0, timestamp=old_timestamp)
        metrics_collector.record_metric("test_metric", 20.0, timestamp=new_timestamp)
        
        # Get summary for last 2 hours
        summary = metrics_collector.get_metric_summary("test_metric", hours=2)
        assert summary["count"] == 1
        assert summary["min"] == 20.0
        assert summary["max"] == 20.0
        assert summary["avg"] == 20.0
    
    def test_aggregate_metrics_avg(self, metrics_collector):
        """Test aggregating metrics with average."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric1", 20.0)
        metrics_collector.record_metric("metric2", 30.0)
        
        result = metrics_collector.aggregate_metrics(["metric1", "metric2"], "avg")
        
        assert result["aggregation_type"] == "avg"
        assert result["metrics"]["metric1"] == 15.0
        assert result["metrics"]["metric2"] == 30.0
        assert "timestamp" in result
    
    def test_aggregate_metrics_sum(self, metrics_collector):
        """Test aggregating metrics with sum."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric1", 20.0)
        
        result = metrics_collector.aggregate_metrics(["metric1"], "sum")
        
        assert result["aggregation_type"] == "sum"
        assert result["metrics"]["metric1"] == 30.0
    
    def test_aggregate_metrics_min(self, metrics_collector):
        """Test aggregating metrics with min."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric1", 20.0)
        
        result = metrics_collector.aggregate_metrics(["metric1"], "min")
        
        assert result["aggregation_type"] == "min"
        assert result["metrics"]["metric1"] == 10.0
    
    def test_aggregate_metrics_max(self, metrics_collector):
        """Test aggregating metrics with max."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric1", 20.0)
        
        result = metrics_collector.aggregate_metrics(["metric1"], "max")
        
        assert result["aggregation_type"] == "max"
        assert result["metrics"]["metric1"] == 20.0
    
    def test_aggregate_metrics_unknown_type(self, metrics_collector):
        """Test aggregating metrics with unknown aggregation type."""
        metrics_collector.record_metric("metric1", 10.0)
        
        result = metrics_collector.aggregate_metrics(["metric1"], "unknown")
        
        assert result["aggregation_type"] == "unknown"
        assert result["metrics"]["metric1"] == 10.0  # Defaults to avg
    
    def test_aggregate_metrics_empty_metric(self, metrics_collector):
        """Test aggregating metrics with empty metric."""
        result = metrics_collector.aggregate_metrics(["non_existent"], "avg")
        
        assert result["metrics"]["non_existent"] is None
    
    def test_record_operation_metrics_success(self, metrics_collector):
        """Test recording operation metrics for successful operation."""
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=1.5,
            success=True,
            result_count=10
        )
        
        # Check duration metric
        duration_history = metrics_collector.get_metric_history("test_operation_duration")
        assert len(duration_history) == 1
        assert duration_history[0]["value"] == 1.5
        
        # Check success metric
        success_history = metrics_collector.get_metric_history("test_operation_success")
        assert len(success_history) == 1
        assert success_history[0]["value"] == 1.0
        
        # Check result count metric
        result_count_history = metrics_collector.get_metric_history("test_operation_result_count")
        assert len(result_count_history) == 1
        assert result_count_history[0]["value"] == 10.0
    
    def test_record_operation_metrics_failure(self, metrics_collector):
        """Test recording operation metrics for failed operation."""
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=2.0,
            success=False,
            error_message="Test error"
        )
        
        # Check duration metric
        duration_history = metrics_collector.get_metric_history("test_operation_duration")
        assert len(duration_history) == 1
        assert duration_history[0]["value"] == 2.0
        
        # Check success metric
        success_history = metrics_collector.get_metric_history("test_operation_success")
        assert len(success_history) == 1
        assert success_history[0]["value"] == 0.0
        
        # Check error metric
        error_history = metrics_collector.get_metric_history("test_operation_errors")
        assert len(error_history) == 1
        assert error_history[0]["value"] == 1.0
        assert error_history[0]["tags"]["error"] == "Test error"
    
    def test_get_operation_summary(self, metrics_collector):
        """Test getting operation summary."""
        # Record successful operation
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=1.0,
            success=True,
            result_count=5
        )
        
        # Record failed operation
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=2.0,
            success=False,
            error_message="Test error"
        )
        
        summary = metrics_collector.get_operation_summary("test_operation")
        
        assert summary["operation_name"] == "test_operation"
        assert summary["total_operations"] == 2
        assert summary["successful_operations"] == 1
        assert summary["failed_operations"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["avg_duration"] == 1.5
        assert summary["min_duration"] == 1.0
        assert summary["max_duration"] == 2.0
        assert summary["total_results"] == 5
        assert summary["avg_results_per_operation"] == 5.0
        assert summary["total_errors"] == 1
    
    def test_get_operation_summary_no_operations(self, metrics_collector):
        """Test getting operation summary for non-existent operation."""
        summary = metrics_collector.get_operation_summary("non_existent")
        
        assert summary["operation_name"] == "non_existent"
        assert summary["total_operations"] == 0
        assert summary["successful_operations"] == 0
        assert summary["failed_operations"] == 0
        assert summary["success_rate"] == 0
        assert summary["avg_duration"] is None
        assert summary["min_duration"] is None
        assert summary["max_duration"] is None
        assert summary["total_results"] == 0
        assert summary["avg_results_per_operation"] is None
        assert summary["total_errors"] == 0
    
    def test_clear_metrics_specific(self, metrics_collector):
        """Test clearing specific metric."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric2", 20.0)
        
        metrics_collector.clear_metrics("metric1")
        
        assert len(metrics_collector.metrics["metric1"]) == 0
        assert len(metrics_collector.metrics["metric2"]) == 1
    
    def test_clear_metrics_all(self, metrics_collector):
        """Test clearing all metrics."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric2", 20.0)
        
        metrics_collector.clear_metrics()
        
        assert len(metrics_collector.metrics) == 0
    
    def test_export_metrics(self, metrics_collector):
        """Test exporting metrics."""
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric2", 20.0)
        
        exported = metrics_collector.export_metrics()
        
        assert "timestamp" in exported
        assert "metrics" in exported
        assert "metric1" in exported["metrics"]
        assert "metric2" in exported["metrics"]
        assert "summary" in exported["metrics"]["metric1"]
        assert "history" in exported["metrics"]["metric1"]
    
    def test_export_metrics_with_time_window(self, metrics_collector):
        """Test exporting metrics with time window."""
        # Record metrics with different timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        new_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        
        metrics_collector.record_metric("metric1", 10.0, timestamp=old_timestamp)
        metrics_collector.record_metric("metric1", 20.0, timestamp=new_timestamp)
        
        exported = metrics_collector.export_metrics(hours=2)
        
        # Only the newer metric should be included
        assert len(exported["metrics"]["metric1"]["history"]) == 1
        assert exported["metrics"]["metric1"]["history"][0]["value"] == 20.0
    
    def test_get_metrics_list(self, metrics_collector):
        """Test getting metrics list."""
        assert metrics_collector.get_metrics_list() == []
        
        metrics_collector.record_metric("metric1", 10.0)
        metrics_collector.record_metric("metric2", 20.0)
        
        metrics_list = metrics_collector.get_metrics_list()
        assert "metric1" in metrics_list
        assert "metric2" in metrics_list
        assert len(metrics_list) == 2


class TestMetricsCollectorEdgeCases:
    """Test metrics collector edge cases."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector instance."""
        return MetricsCollector(max_history=3)
    
    def test_max_history_limit(self, metrics_collector):
        """Test that max_history limit is respected."""
        # Record more metrics than max_history
        for i in range(5):
            metrics_collector.record_metric("test_metric", float(i))
        
        history = metrics_collector.get_metric_history("test_metric")
        assert len(history) == 3  # Should be limited by max_history
        assert history[0]["value"] == 2.0  # Oldest should be dropped
        assert history[2]["value"] == 4.0  # Newest should be kept
    
    def test_metric_with_zero_value(self, metrics_collector):
        """Test recording metric with zero value."""
        metrics_collector.record_metric("test_metric", 0.0)
        
        summary = metrics_collector.get_metric_summary("test_metric")
        assert summary["min"] == 0.0
        assert summary["max"] == 0.0
        assert summary["avg"] == 0.0
        assert summary["sum"] == 0.0
    
    def test_metric_with_negative_value(self, metrics_collector):
        """Test recording metric with negative value."""
        metrics_collector.record_metric("test_metric", -10.0)
        metrics_collector.record_metric("test_metric", 10.0)
        
        summary = metrics_collector.get_metric_summary("test_metric")
        assert summary["min"] == -10.0
        assert summary["max"] == 10.0
        assert summary["avg"] == 0.0
        assert summary["sum"] == 0.0
    
    def test_operation_metrics_without_result_count(self, metrics_collector):
        """Test recording operation metrics without result count."""
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=1.0,
            success=True
        )
        
        # Should not create result_count metric
        result_count_history = metrics_collector.get_metric_history("test_operation_result_count")
        assert len(result_count_history) == 0
    
    def test_operation_metrics_without_error_message(self, metrics_collector):
        """Test recording operation metrics without error message."""
        metrics_collector.record_operation_metrics(
            "test_operation",
            duration=1.0,
            success=False
        )
        
        # Should not create errors metric when no error message
        error_history = metrics_collector.get_metric_history("test_operation_errors")
        assert len(error_history) == 0
    
    def test_aggregate_metrics_with_time_window(self, metrics_collector):
        """Test aggregating metrics with time window."""
        # Record metrics with different timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        new_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        
        metrics_collector.record_metric("metric1", 10.0, timestamp=old_timestamp)
        metrics_collector.record_metric("metric1", 20.0, timestamp=new_timestamp)
        
        result = metrics_collector.aggregate_metrics(["metric1"], "avg", hours=2)
        
        assert result["time_window_hours"] == 2
        assert result["metrics"]["metric1"] == 20.0  # Only newer metric
    
    def test_clear_metrics_non_existent(self, metrics_collector):
        """Test clearing non-existent metric."""
        # Should not raise an error
        metrics_collector.clear_metrics("non_existent")
        
        # Should not affect other metrics
        metrics_collector.record_metric("existing_metric", 10.0)
        metrics_collector.clear_metrics("non_existent")
        
        assert len(metrics_collector.metrics["existing_metric"]) == 1 