"""
Vector Store Client Adapters.

This package provides adapters for integrating with external services
like SVO (Semantic Vector Operations) and EMB (Embedding) services.

Main adapters:
    - SVOChunkerAdapter: Adapter for SVO semantic chunking service
    - EmbeddingAdapter: Adapter for embedding service

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from .base_adapter import BaseAdapter
from .svo_adapter import SVOChunkerAdapter
from .embedding_adapter import EmbeddingAdapter

__all__ = [
    "BaseAdapter",
    "SVOChunkerAdapter", 
    "EmbeddingAdapter"
] 