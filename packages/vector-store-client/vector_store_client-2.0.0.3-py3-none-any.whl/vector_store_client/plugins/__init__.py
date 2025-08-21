"""
Plugins package for Vector Store Client.

This package provides a plugin architecture for extending the functionality
of the Vector Store Client with custom operations, preprocessing, and
post-processing capabilities.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from .base_plugin import BasePlugin, PluginRegistry
from .text_preprocessor import TextPreprocessorPlugin
from .embedding_optimizer import EmbeddingOptimizerPlugin
from .metadata_enricher import MetadataEnricherPlugin
from .quality_checker import QualityCheckerPlugin

__all__ = [
    "BasePlugin",
    "PluginRegistry", 
    "TextPreprocessorPlugin",
    "EmbeddingOptimizerPlugin",
    "MetadataEnricherPlugin",
    "QualityCheckerPlugin"
] 