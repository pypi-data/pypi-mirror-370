"""
Performance monitor for Vector Store Client.

This module provides performance monitoring capabilities
for tracking client performance metrics and optimization.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import time
import psutil
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from ..exceptions import MonitoringError


class PerformanceMonitor:
    """
    Monitor client performance.
    
    Tracks operation timing, memory usage, and other
    performance metrics for optimization.
    """
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.start_time = time.time()
        self.operation_count = 0
        self.name = "PerformanceMonitor"
    
    def get_name(self) -> str:
        """Get performance monitor name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get performance monitor configuration.
        
        Returns:
            Dict[str, Any]: Performance monitor configuration
        """
        return {
            "name": self.name,
            "uptime": time.time() - self.start_time,
            "operation_count": self.operation_count,
            "metrics_count": len(self.metrics)
        }
    
    def record_operation(
        self,
        operation_name: str,
        duration: float,
        success: bool,
        result_count: Optional[int] = None,
        memory_usage: Optional[float] = None
    ) -> None:
        """
        Record operation metrics.
        
        Parameters:
            operation_name: Name of the operation
            duration: Operation duration in seconds
            success: Whether operation was successful
            result_count: Number of results returned
            memory_usage: Memory usage in bytes
        """
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                "count": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "failed_count": 0,
                "total_results": 0,
                "min_duration": float('inf'),
                "max_duration": 0.0,
                "avg_duration": 0.0,
                "total_memory": 0.0,
                "avg_memory": 0.0,
                "last_operation": None
            }
        
        metrics = self.metrics[operation_name]
        
        # Update counters
        metrics["count"] += 1
        metrics["total_duration"] += duration
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)
        metrics["avg_duration"] = metrics["total_duration"] / metrics["count"]
        
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failed_count"] += 1
        
        if result_count is not None:
            metrics["total_results"] += result_count
        
        if memory_usage is not None:
            metrics["total_memory"] += memory_usage
            metrics["avg_memory"] = metrics["total_memory"] / metrics["count"]
        
        metrics["last_operation"] = datetime.now(timezone.utc).isoformat()
        self.operation_count += 1
    
    def get_operation_metrics(self, operation_name: str) -> Dict[str, Any]:
        """
        Get metrics for a specific operation.
        
        Parameters:
            operation_name: Name of the operation
            
        Returns:
            Dict[str, Any]: Operation metrics
        """
        return self.metrics.get(operation_name, {})
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.
        
        Returns:
            Dict[str, Any]: Performance summary
        """
        if not self.metrics:
            return {
                "uptime": time.time() - self.start_time,
                "total_operations": 0,
                "operations": {}
            }
        
        total_operations = sum(m["count"] for m in self.metrics.values())
        total_successful = sum(m["success_count"] for m in self.metrics.values())
        total_failed = sum(m["failed_count"] for m in self.metrics.values())
        total_duration = sum(m["total_duration"] for m in self.metrics.values())
        
        # Get memory usage
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_usage = memory_info.rss
        except Exception:
            memory_usage = 0
        
        return {
            "uptime": time.time() - self.start_time,
            "total_operations": total_operations,
            "successful_operations": total_successful,
            "failed_operations": total_failed,
            "success_rate": total_successful / total_operations if total_operations > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": total_duration / total_operations if total_operations > 0 else 0,
            "memory_usage_bytes": memory_usage,
            "memory_usage_mb": memory_usage / (1024 * 1024),
            "operations": self.metrics
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage.
        
        Returns:
            Dict[str, Any]: Memory usage information
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_bytes": memory_info.rss,
                "vms_bytes": memory_info.vms,
                "rss_mb": memory_info.rss / (1024 * 1024),
                "vms_mb": memory_info.vms / (1024 * 1024),
                "percent": process.memory_percent()
            }
        except Exception as e:
            return {
                "error": str(e),
                "rss_bytes": 0,
                "vms_bytes": 0,
                "rss_mb": 0,
                "vms_mb": 0,
                "percent": 0
            }
    
    def clear_metrics(self, operation_name: str = None) -> None:
        """
        Clear metrics for a specific operation or all operations.
        
        Parameters:
            operation_name: Operation name or None for all operations
        """
        if operation_name:
            if operation_name in self.metrics:
                del self.metrics[operation_name]
        else:
            self.metrics.clear()
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export metrics in a standardized format.
        
        Returns:
            Dict[str, Any]: Exported metrics
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": self.get_summary(),
            "memory_usage": self.get_memory_usage(),
            "operations": self.metrics
        } 