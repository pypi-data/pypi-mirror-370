"""
Metrics middleware for Vector Store Client.

This middleware provides performance metrics collection
for monitoring and optimization purposes.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Awaitable
from .base_middleware import BaseMiddleware


class MetricsMiddleware(BaseMiddleware):
    """
    Middleware for collecting performance metrics.
    
    Collects timing, success rates, and other performance
    metrics for monitoring and optimization.
    """
    
    def __init__(self):
        super().__init__("MetricsMiddleware")
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.logger = self.logger.getChild("metrics")
    
    def get_name(self) -> str:
        """Get middleware name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get middleware configuration.
        Returns:
            Dict[str, Any]: Middleware configuration
        """
        summary = self.get_summary_metrics()
        return {
            "name": self.name,
            "enabled": self.enabled,
            "type": self.__class__.__name__,
            "metrics_count": len(self.metrics),
            "total_requests": summary.get("total_requests", 0),
            "total_errors": summary.get("failed_requests", 0),
            "avg_response_time": summary.get("avg_duration", 0)
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Process request with metrics collection.
        
        Parameters:
            request: Request data
            next_handler: Next handler in the chain
            
        Returns:
            Dict[str, Any]: Response data
        """
        method = request.get("method", "unknown")
        start_time = time.time()
        
        try:
            # Execute request
            response = await next_handler(request)
            
            # Record success metrics
            duration = time.time() - start_time
            self._record_metrics(method, duration, True)
            
            return response
            
        except Exception as e:
            # Record failure metrics
            duration = time.time() - start_time
            self._record_metrics(method, duration, False, str(e))
            raise
    
    def _record_metrics(self, method: str, duration: float, success: bool, error: str = None) -> None:
        """Record metrics for a request."""
        if method not in self.metrics:
            self.metrics[method] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_duration": 0.0,
                "min_duration": float('inf'),
                "max_duration": 0.0,
                "avg_duration": 0.0,
                "last_request": None,
                "errors": []
            }
        
        metrics = self.metrics[method]
        
        # Update counters
        metrics["total_requests"] += 1
        if success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1
            if error:
                metrics["errors"].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": error
                })
        
        # Update timing metrics
        metrics["total_duration"] += duration
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)
        metrics["avg_duration"] = metrics["total_duration"] / metrics["total_requests"]
        metrics["last_request"] = datetime.now(timezone.utc).isoformat()
        
        # Keep only recent errors
        if len(metrics["errors"]) > 10:
            metrics["errors"] = metrics["errors"][-10:]
    
    def get_metrics(self, method: str = None) -> Dict[str, Any]:
        """
        Get metrics for a specific method or all methods.
        
        Parameters:
            method: Method name or None for all methods
            
        Returns:
            Dict[str, Any]: Metrics data
        """
        if method:
            return self.metrics.get(method, {})
        else:
            return self.metrics.copy()
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary metrics across all methods."""
        if not self.metrics:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "total_duration": 0.0,
                "avg_duration": 0.0,
                "methods": []
            }
        
        total_requests = sum(m["total_requests"] for m in self.metrics.values())
        total_successful = sum(m["successful_requests"] for m in self.metrics.values())
        total_failed = sum(m["failed_requests"] for m in self.metrics.values())
        total_duration = sum(m["total_duration"] for m in self.metrics.values())
        
        return {
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "success_rate": total_successful / total_requests if total_requests > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": total_duration / total_requests if total_requests > 0 else 0,
            "methods": list(self.metrics.keys())
        }
    
    def clear_metrics(self, method: str = None) -> None:
        """
        Clear metrics for a specific method or all methods.
        
        Parameters:
            method: Method name or None for all methods
        """
        if method:
            if method in self.metrics:
                del self.metrics[method]
                self.logger.info(f"Cleared metrics for method: {method}")
        else:
            self.metrics.clear()
            self.logger.info("Cleared all metrics")
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics in a standardized format."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": self.get_summary_metrics(),
            "methods": self.metrics
        }
    
    def reset_metrics(self, method: str = None) -> None:
        """Reset metrics (alias for clear_metrics)."""
        self.clear_metrics(method)
    
    def get_method_metrics(self, method: str) -> Dict[str, Any]:
        """Get metrics for a specific method."""
        return self.get_metrics(method) 