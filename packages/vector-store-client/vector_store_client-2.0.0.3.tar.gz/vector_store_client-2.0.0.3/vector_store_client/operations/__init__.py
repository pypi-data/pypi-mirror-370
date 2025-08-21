"""
Operations package for Vector Store Client.

This package contains all operation modules organized by functionality.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from .base_operations import BaseOperations
from .chunk_operations import ChunkOperations
from .embedding_operations import EmbeddingOperations

__all__ = [
    "BaseOperations",
    "ChunkOperations", 
    "EmbeddingOperations"
] 