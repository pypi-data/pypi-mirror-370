"""
Text preprocessing plugin for Vector Store Client.

This plugin provides text preprocessing capabilities including
cleaning, normalization, and text enhancement.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import re
import string
from typing import Dict, Any, Optional, List
from .base_plugin import BasePlugin


class TextPreprocessorPlugin(BasePlugin):
    """
    Plugin for text preprocessing.
    
    Provides text cleaning, normalization, and enhancement
    capabilities for chunks before processing.
    """
    
    def __init__(self, client=None, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.client = client
        self.config = config or {}
        self._setup_config()
    
    def get_name(self) -> str:
        return "text_preprocessor"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Text preprocessing plugin for cleaning and normalizing text"
    
    def _setup_config(self) -> None:
        """Setup plugin configuration with defaults."""
        self.remove_html = self.config.get("remove_html", True)
        self.remove_urls = self.config.get("remove_urls", True)
        self.remove_emails = self.config.get("remove_emails", True)
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.remove_special_chars = self.config.get("remove_special_chars", False)
        self.lowercase = self.config.get("lowercase", False)
        self.min_length = self.config.get("min_length", 10)
        self.max_length = self.config.get("max_length", 10000)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema."""
        return {
            "remove_html": {
                "type": "boolean",
                "default": True,
                "description": "Remove HTML tags from text"
            },
            "remove_urls": {
                "type": "boolean", 
                "default": True,
                "description": "Remove URLs from text"
            },
            "remove_emails": {
                "type": "boolean",
                "default": True,
                "description": "Remove email addresses from text"
            },
            "normalize_whitespace": {
                "type": "boolean",
                "default": True,
                "description": "Normalize whitespace characters"
            },
            "remove_special_chars": {
                "type": "boolean",
                "default": False,
                "description": "Remove special characters"
            },
            "lowercase": {
                "type": "boolean",
                "default": False,
                "description": "Convert text to lowercase"
            },
            "min_length": {
                "type": "integer",
                "default": 10,
                "description": "Minimum text length"
            },
            "max_length": {
                "type": "integer",
                "default": 10000,
                "description": "Maximum text length"
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if "min_length" in config and config["min_length"] < 0:
            raise ValueError("min_length must be non-negative")
        if "max_length" in config and config["max_length"] < 1:
            raise ValueError("max_length must be positive")
        if "min_length" in config and "max_length" in config:
            if config["min_length"] > config["max_length"]:
                raise ValueError("min_length cannot be greater than max_length")
        return True
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        if not self.remove_html:
            return text
        
        # Simple HTML tag removal
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        if not self.remove_urls:
            return text
        
        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        if not self.remove_emails:
            return text
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters."""
        if not self.normalize_whitespace:
            return text
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters."""
        if not self.remove_special_chars:
            return text
        
        # Keep only alphanumeric and basic punctuation
        allowed_chars = string.ascii_letters + string.digits + ' .,!?;:()[]{}"\'-'
        return ''.join(c for c in text if c in allowed_chars)
    
    def _apply_length_filters(self, text: str) -> str:
        """Apply length filters to text."""
        if len(text) < self.min_length:
            return ""
        
        if len(text) > self.max_length:
            return text[:self.max_length]
        
        return text
    
    def _preprocess_text(self, text: str) -> str:
        """Apply all preprocessing steps to text."""
        if not text:
            return ""
        
        # Apply preprocessing steps
        text = self._remove_html_tags(text)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._normalize_whitespace(text)
        text = self._remove_special_chars(text)
        
        if self.lowercase:
            text = text.lower()
        
        text = self._apply_length_filters(text)
        
        return text
    
    async def execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute text preprocessing.
        
        Parameters:
            data: Input data containing text
            context: Optional context
            
        Returns:
            Dict[str, Any]: Processed data with cleaned text
        """
        # Handle different input formats
        if "text" in data:
            original_text = data["text"]
            processed_text = self._preprocess_text(original_text)
            
            data["text"] = processed_text
            data["original_text"] = original_text
            data["text_processed"] = True
            
        elif "body" in data:
            original_body = data["body"]
            processed_body = self._preprocess_text(original_body)
            
            data["body"] = processed_body
            data["original_body"] = original_body
            data["body_processed"] = True
            
        elif "chunks" in data:
            # Process multiple chunks
            chunks = data["chunks"]
            processed_chunks = []
            
            for chunk in chunks:
                if isinstance(chunk, dict):
                    if "text" in chunk:
                        chunk["original_text"] = chunk["text"]
                        chunk["text"] = self._preprocess_text(chunk["text"])
                        chunk["text_processed"] = True
                    if "body" in chunk:
                        chunk["original_body"] = chunk["body"]
                        chunk["body"] = self._preprocess_text(chunk["body"])
                        chunk["body_processed"] = True
                    processed_chunks.append(chunk)
                else:
                    # Assume it's a SemanticChunk object
                    if hasattr(chunk, 'text') and chunk.text:
                        if not hasattr(chunk, 'block_meta') or chunk.block_meta is None:
                            chunk.block_meta = {}
                        chunk.block_meta["original_text"] = chunk.text
                        chunk.text = self._preprocess_text(chunk.text)
                        chunk.block_meta["text_processed"] = True
                    if hasattr(chunk, 'body') and chunk.body:
                        if not hasattr(chunk, 'block_meta') or chunk.block_meta is None:
                            chunk.block_meta = {}
                        chunk.block_meta["original_body"] = chunk.body
                        chunk.body = self._preprocess_text(chunk.body)
                        chunk.block_meta["body_processed"] = True
                    processed_chunks.append(chunk)
            
            data["chunks"] = processed_chunks
            data["chunks_processed"] = True
            
        return data
    
    async def pre_execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pre-execution validation."""
        # Validate that we have text to process
        has_text = any(key in data for key in ["text", "body", "chunks"])
        if not has_text:
            self.logger.warning("No text data found for preprocessing")
        
        return data
    
    async def post_execute(
        self, 
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post-execution logging."""
        if "text_processed" in result or "body_processed" in result:
            self.logger.info("Text preprocessing completed")
        elif "chunks_processed" in result:
            chunk_count = len(result.get("chunks", []))
            self.logger.info(f"Processed {chunk_count} chunks")
        
        return result
    
    def get_preprocessing_stats(self) -> Dict[str, Any]:
        """
        Get preprocessing statistics.
        
        Returns:
            Dict[str, Any]: Preprocessing statistics
        """
        return {
            "plugin_name": self.get_name(),
            "version": self.get_version(),
            "config": {
                "remove_html": self.remove_html,
                "remove_urls": self.remove_urls,
                "remove_emails": self.remove_emails,
                "normalize_whitespace": self.normalize_whitespace,
                "remove_special_chars": self.remove_special_chars,
                "lowercase": self.lowercase,
                "min_length": self.min_length,
                "max_length": self.max_length,
                "preprocessing_level": "standard"
            },
            "description": self.get_description()
        } 