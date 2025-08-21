"""
Middleware package for Vector Store Client.

This package provides middleware architecture for extending the functionality
of the Vector Store Client with request/response processing, logging,
caching, and other cross-cutting concerns.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from .base_middleware import BaseMiddleware, MiddlewareChain
from .logging_middleware import LoggingMiddleware
from .caching_middleware import CachingMiddleware
from .retry_middleware import RetryMiddleware
from .metrics_middleware import MetricsMiddleware

__all__ = [
    "BaseMiddleware",
    "MiddlewareChain",
    "LoggingMiddleware", 
    "CachingMiddleware",
    "RetryMiddleware",
    "MetricsMiddleware"
] 