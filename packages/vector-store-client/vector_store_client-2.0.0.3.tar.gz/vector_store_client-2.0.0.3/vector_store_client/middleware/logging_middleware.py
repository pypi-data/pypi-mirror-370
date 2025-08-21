"""
Logging middleware for Vector Store Client.

This middleware provides request and response logging capabilities
for debugging and monitoring purposes.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Awaitable, List
from .base_middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for request and response logging.
    
    Logs request details, response data, and timing information
    for debugging and monitoring purposes.
    """
    
    def __init__(self, log_level: str = "INFO", include_body: bool = True):
        super().__init__("LoggingMiddleware")
        self.log_level = log_level.upper()
        self.include_body = include_body
        self.logger = self.logger.getChild("logging")
        self.next_middleware = None
    
    def get_name(self) -> str:
        """Get middleware name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get middleware configuration.
        Returns:
            Dict[str, Any]: Middleware configuration
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "type": self.__class__.__name__,
            "log_level": self.log_level,
            "log_count": 0  # TODO: Implement log counting
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Process request with logging.
        
        Parameters:
            request: Request data
            next_handler: Next handler in the chain
            
        Returns:
            Dict[str, Any]: Response data
        """
        # Log request
        self._log_request(request)
        
        # Record start time
        start_time = time.time()
        
        try:
            # Execute next handler
            response = await next_handler(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            self._log_response(response, duration)
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            self._log_error(e, duration)
            raise
    
    def _log_request(self, request: Dict[str, Any]) -> None:
        """Log request details."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "request",
            "method": request.get("method", "unknown"),
            "params": request.get("params", {})
        }
        
        if self.include_body and "body" in request:
            log_data["body"] = request["body"]
        
        self.logger.info(f"Request: {json.dumps(log_data, default=str)}")
    
    def _log_response(self, response: Dict[str, Any], duration: float) -> None:
        """Log response details."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "response",
            "duration_ms": round(duration * 1000, 2),
            "success": response.get("success", True)
        }
        
        if self.include_body and "result" in response:
            log_data["result"] = response["result"]
        
        self.logger.info(f"Response: {json.dumps(log_data, default=str)}")
    
    def _log_error(self, error: Exception, duration: float) -> None:
        """Log error details."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "error",
            "duration_ms": round(duration * 1000, 2),
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        self.logger.error(f"Error: {json.dumps(log_data, default=str)}")
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get logged entries (placeholder for test compatibility)."""
        return []  # TODO: Implement log storage
    
    def clear_logs(self) -> None:
        """Clear logged entries (placeholder for test compatibility)."""
        pass  # TODO: Implement log storage
    
    def set_next(self, middleware) -> None:
        """Set next middleware in chain."""
        self.next_middleware = middleware
    
    async def execute_chain(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute middleware chain."""
        request = {"method": method, "params": params or {}}
        
        async def final_handler(req):
            return {"result": "success"}
        
        if self.next_middleware:
            return await self.next_middleware.process_request(request, final_handler)
        else:
            return await self.process_request(request, final_handler) 