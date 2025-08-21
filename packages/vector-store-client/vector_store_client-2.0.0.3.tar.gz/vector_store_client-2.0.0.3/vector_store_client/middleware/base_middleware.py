"""
Base middleware classes for Vector Store Client.

This module provides the foundation for the middleware architecture,
including the base middleware class and middleware chain.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime


class BaseMiddleware(ABC):
    """
    Base class for all middleware.
    
    Middleware can be used to process requests and responses,
    add cross-cutting concerns like logging, caching, and metrics.
    
    Attributes:
        name (str): Middleware name
        enabled (bool): Whether the middleware is enabled
    """
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.enabled = True
        self.logger = logging.getLogger(f"middleware.{self.name}")
    
    @abstractmethod
    async def process_request(
        self,
        request: Dict[str, Any],
        next_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Process request.
        
        Parameters:
            request: Request data
            next_handler: Next handler in the chain
            
        Returns:
            Dict[str, Any]: Response data
        """
        pass
    
    def enable(self) -> None:
        """Enable the middleware."""
        self.enabled = True
        self.logger.info(f"Middleware {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the middleware."""
        self.enabled = False
        self.logger.info(f"Middleware {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if middleware is enabled."""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get middleware configuration.
        
        Returns:
            Dict[str, Any]: Middleware configuration
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "type": self.__class__.__name__
        }
    
    async def execute_command(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute command through middleware chain.
        
        This is a convenience method for testing compatibility.
        In real usage, middleware should be chained together.
        
        Parameters:
            method: Command method name
            params: Command parameters
            
        Returns:
            Dict[str, Any]: Response data
        """
        request = {
            "method": method,
            "params": params or {}
        }
        
        # Create a simple final handler that returns mock data
        async def final_handler(req: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "success"}
        
        return await self.process_request(request, final_handler)


class MiddlewareChain:
    """
    Chain of middleware for processing requests.
    
    Provides functionality for managing and executing
    middleware in sequence.
    
    Attributes:
        middlewares (List[BaseMiddleware]): List of middleware
    """
    
    def __init__(self):
        self.middlewares: List[BaseMiddleware] = []
        self.logger = logging.getLogger("middleware_chain")
    
    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """
        Add middleware to the chain.
        
        Parameters:
            middleware: Middleware to add
        """
        if not isinstance(middleware, BaseMiddleware):
            raise ValueError(f"Invalid middleware type: {type(middleware)}")
        
        self.middlewares.append(middleware)
        self.logger.info(f"Added middleware: {middleware.name}")
    
    def remove_middleware(self, name: str) -> bool:
        """
        Remove middleware by name.
        
        Parameters:
            name: Middleware name
            
        Returns:
            bool: True if middleware was removed
        """
        for i, middleware in enumerate(self.middlewares):
            if middleware.name == name:
                del self.middlewares[i]
                self.logger.info(f"Removed middleware: {name}")
                return True
        return False
    
    def get_middleware(self, name: str) -> Optional[BaseMiddleware]:
        """
        Get middleware by name.
        
        Parameters:
            name: Middleware name
            
        Returns:
            Optional[BaseMiddleware]: Middleware or None
        """
        for middleware in self.middlewares:
            if middleware.name == name:
                return middleware
        return None
    
    def list_middlewares(self) -> List[str]:
        """
        List all middleware names.
        
        Returns:
            List[str]: List of middleware names
        """
        return [mw.name for mw in self.middlewares]
    
    def clear(self) -> None:
        """Clear all middleware."""
        self.middlewares.clear()
        self.logger.info("Cleared all middleware")
    
    async def execute(
        self,
        request: Dict[str, Any],
        final_handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Execute middleware chain.
        
        Parameters:
            request: Request data
            final_handler: Final handler to execute
            
        Returns:
            Dict[str, Any]: Response data
        """
        # Create middleware chain
        handler = final_handler
        
        # Build chain in reverse order
        for middleware in reversed(self.middlewares):
            if middleware.is_enabled():
                # Create closure to capture middleware and handler
                current_middleware = middleware
                current_handler = handler
                
                def create_middleware_wrapper(mw, h):
                    async def middleware_wrapper(req: Dict[str, Any]) -> Dict[str, Any]:
                        return await mw.process_request(req, h)
                    return middleware_wrapper
                
                handler = create_middleware_wrapper(current_middleware, current_handler)
        
        # Execute the chain
        try:
            response = await handler(request)
            return response
        except Exception as e:
            self.logger.error(f"Middleware chain execution failed: {e}")
            raise
    
    def get_middleware_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all middleware.
        
        Returns:
            Dict[str, Dict[str, Any]]: Middleware information
        """
        info = {}
        for middleware in self.middlewares:
            info[middleware.name] = {
                "name": middleware.name,
                "enabled": middleware.enabled,
                "type": middleware.__class__.__name__
            }
        return info 