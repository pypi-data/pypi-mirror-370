"""
Metrics collector for Vector Store Client.

This module provides metrics collection and aggregation capabilities
for monitoring and analysis.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from ..exceptions import MonitoringError


class MetricsCollector:
    """
    Collector for metrics and performance data.
    
    Provides capabilities for collecting, aggregating, and analyzing
    metrics from various components.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.aggregations: Dict[str, Dict[str, Any]] = {}
        self.name = "MetricsCollector"
    
    def get_name(self) -> str:
        """Get metrics collector name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get metrics collector configuration.
        
        Returns:
            Dict[str, Any]: Metrics collector configuration
        """
        return {
            "name": self.name,
            "max_history": self.max_history,
            "metrics_count": len(self.metrics),
            "aggregations_count": len(self.aggregations)
        }
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record a metric value.
        
        Parameters:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        metric_data = {
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        }
        
        self.metrics[metric_name].append(metric_data)
    
    def get_metric_history(
        self,
        metric_name: str,
        hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metric history.
        
        Parameters:
            metric_name: Name of the metric
            hours: Optional time window in hours
            
        Returns:
            List[Dict[str, Any]]: Metric history
        """
        if metric_name not in self.metrics:
            return []
        
        history = list(self.metrics[metric_name])
        
        if hours is not None:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            history = [
                entry for entry in history 
                if entry["timestamp"] >= cutoff_time
            ]
        
        return history
    
    def get_metric_summary(
        self,
        metric_name: str,
        hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get metric summary statistics.
        
        Parameters:
            metric_name: Name of the metric
            hours: Optional time window in hours
            
        Returns:
            Dict[str, Any]: Metric summary
        """
        history = self.get_metric_history(metric_name, hours)
        
        if not history:
            return {
                "metric_name": metric_name,
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "sum": None
            }
        
        values = [entry["value"] for entry in history]
        
        return {
            "metric_name": metric_name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "latest": values[-1] if values else None,
            "latest_timestamp": history[-1]["timestamp"] if history else None
        }
    
    def aggregate_metrics(
        self,
        metric_names: List[str],
        aggregation_type: str = "avg",
        hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Aggregate multiple metrics.
        
        Parameters:
            metric_names: List of metric names to aggregate
            aggregation_type: Type of aggregation (avg, sum, min, max)
            hours: Optional time window in hours
            
        Returns:
            Dict[str, Any]: Aggregated metrics
        """
        aggregated = {}
        
        for metric_name in metric_names:
            summary = self.get_metric_summary(metric_name, hours)
            
            if summary["count"] > 0:
                if aggregation_type == "avg":
                    aggregated[metric_name] = summary["avg"]
                elif aggregation_type == "sum":
                    aggregated[metric_name] = summary["sum"]
                elif aggregation_type == "min":
                    aggregated[metric_name] = summary["min"]
                elif aggregation_type == "max":
                    aggregated[metric_name] = summary["max"]
                else:
                    aggregated[metric_name] = summary["avg"]
            else:
                aggregated[metric_name] = None
        
        return {
            "aggregation_type": aggregation_type,
            "time_window_hours": hours,
            "metrics": aggregated,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def record_operation_metrics(
        self,
        operation_name: str,
        duration: float,
        success: bool,
        result_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Record operation metrics.
        
        Parameters:
            operation_name: Name of the operation
            duration: Operation duration in seconds
            success: Whether operation was successful
            result_count: Number of results returned
            error_message: Error message if operation failed
        """
        # Record duration
        self.record_metric(
            f"{operation_name}_duration",
            duration,
            {"operation": operation_name}
        )
        
        # Record success/failure
        self.record_metric(
            f"{operation_name}_success",
            1.0 if success else 0.0,
            {"operation": operation_name}
        )
        
        # Record result count if provided
        if result_count is not None:
            self.record_metric(
                f"{operation_name}_result_count",
                float(result_count),
                {"operation": operation_name}
            )
        
        # Record error if operation failed
        if not success and error_message:
            self.record_metric(
                f"{operation_name}_errors",
                1.0,
                {"operation": operation_name, "error": error_message}
            )
    
    def get_operation_summary(
        self,
        operation_name: str,
        hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get operation summary.
        
        Parameters:
            operation_name: Name of the operation
            hours: Optional time window in hours
            
        Returns:
            Dict[str, Any]: Operation summary
        """
        duration_summary = self.get_metric_summary(f"{operation_name}_duration", hours)
        success_summary = self.get_metric_summary(f"{operation_name}_success", hours)
        result_count_summary = self.get_metric_summary(f"{operation_name}_result_count", hours)
        error_summary = self.get_metric_summary(f"{operation_name}_errors", hours)
        
        total_operations = duration_summary["count"]
        successful_operations = int(success_summary["sum"]) if success_summary["sum"] else 0
        failed_operations = total_operations - successful_operations
        
        return {
            "operation_name": operation_name,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "avg_duration": duration_summary["avg"],
            "min_duration": duration_summary["min"],
            "max_duration": duration_summary["max"],
            "total_results": int(result_count_summary["sum"]) if result_count_summary["sum"] else 0,
            "avg_results_per_operation": result_count_summary["avg"],
            "total_errors": int(error_summary["sum"]) if error_summary["sum"] else 0,
            "time_window_hours": hours
        }
    
    def clear_metrics(self, metric_name: Optional[str] = None) -> None:
        """
        Clear metrics.
        
        Parameters:
            metric_name: Optional specific metric to clear (clears all if None)
        """
        if metric_name:
            if metric_name in self.metrics:
                self.metrics[metric_name].clear()
        else:
            self.metrics.clear()
    
    def export_metrics(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Export all metrics.
        
        Parameters:
            hours: Optional time window in hours
            
        Returns:
            Dict[str, Any]: Exported metrics
        """
        exported = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {}
        }
        
        for metric_name in self.metrics.keys():
            exported["metrics"][metric_name] = {
                "summary": self.get_metric_summary(metric_name, hours),
                "history": self.get_metric_history(metric_name, hours)
            }
        
        return exported
    
    def get_metrics_list(self) -> List[str]:
        """
        Get list of all metric names.
        
        Returns:
            List[str]: List of metric names
        """
        return list(self.metrics.keys()) 