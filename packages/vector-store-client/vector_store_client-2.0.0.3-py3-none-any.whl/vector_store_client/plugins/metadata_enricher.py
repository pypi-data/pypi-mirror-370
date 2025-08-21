"""
Metadata enricher plugin for Vector Store Client.

This plugin provides metadata enrichment capabilities including
automatic metadata generation, validation, and enhancement.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from .base_plugin import BasePlugin


class MetadataEnricherPlugin(BasePlugin):
    """
    Plugin for metadata enrichment.
    
    Provides automatic metadata generation, validation,
    and enhancement capabilities for chunks.
    """
    
    def __init__(self, client=None, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.client = client
        self.config = config or {}
        self._setup_config()
    
    def get_name(self) -> str:
        return "metadata_enricher"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Metadata enrichment plugin for automatic metadata generation"
    
    def _setup_config(self) -> None:
        """Setup plugin configuration with defaults."""
        self.auto_generate_metadata = self.config.get("auto_generate_metadata", True)
        self.detect_language = self.config.get("detect_language", True)
        self.extract_keywords = self.config.get("extract_keywords", True)
        self.calculate_metrics = self.config.get("calculate_metrics", True)
        self.add_timestamps = self.config.get("add_timestamps", True)
        self.generate_hashes = self.config.get("generate_hashes", True)
        self.max_keywords = self.config.get("max_keywords", 10)
        self.min_keyword_length = self.config.get("min_keyword_length", 3)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema."""
        return {
            "auto_generate_metadata": {
                "type": "boolean",
                "default": True,
                "description": "Automatically generate metadata"
            },
            "detect_language": {
                "type": "boolean",
                "default": True,
                "description": "Detect text language"
            },
            "extract_keywords": {
                "type": "boolean",
                "default": True,
                "description": "Extract keywords from text"
            },
            "calculate_metrics": {
                "type": "boolean",
                "default": True,
                "description": "Calculate text metrics"
            },
            "add_timestamps": {
                "type": "boolean",
                "default": True,
                "description": "Add timestamps to metadata"
            },
            "generate_hashes": {
                "type": "boolean",
                "default": True,
                "description": "Generate content hashes"
            },
            "max_keywords": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of keywords to extract"
            },
            "min_keyword_length": {
                "type": "integer",
                "default": 3,
                "description": "Minimum keyword length"
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if "max_keywords" in config and config["max_keywords"] < 1:
            raise ValueError("max_keywords must be positive")
        if "min_keyword_length" in config and config["min_keyword_length"] < 1:
            raise ValueError("min_keyword_length must be positive")
        return True
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character sets."""
        if not self.detect_language:
            return "unknown"
        
        # Simple language detection
        text_lower = text.lower()
        
        # Check for Cyrillic characters
        if re.search(r'[а-яё]', text_lower):
            return "ru"
        
        # Check for Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text_lower):
            return "zh"
        
        # Check for Japanese characters
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text_lower):
            return "ja"
        
        # Check for Korean characters
        if re.search(r'[\uac00-\ud7af]', text_lower):
            return "ko"
        
        # Default to English
        return "en"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        if not self.extract_keywords:
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter by length and frequency
        word_freq = {}
        for word in words:
            if len(word) >= self.min_keyword_length:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:self.max_keywords]]
        
        return keywords
    
    def _calculate_text_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate text metrics."""
        if not self.calculate_metrics:
            return {}
        
        if not text:
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "average_word_length": 0,
                "readability_score": 0
            }
        
        # Basic metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        character_count = len(text)
        sentence_count = len(sentences)
        
        # Average word length
        if word_count > 0:
            total_word_length = sum(len(word) for word in words)
            average_word_length = total_word_length / word_count
        else:
            average_word_length = 0
        
        # Simple readability score (Flesch Reading Ease approximation)
        if word_count > 0 and sentence_count > 0:
            avg_sentence_length = word_count / sentence_count
            readability_score = max(0, 100 - (avg_sentence_length * 1.5))
        else:
            readability_score = 0
        
        return {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "average_word_length": round(average_word_length, 2),
            "readability_score": round(readability_score, 2)
        }
    
    def _generate_content_hash(self, text: str) -> str:
        """Generate content hash."""
        if not self.generate_hashes:
            return ""
        
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _add_timestamps(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamps to metadata."""
        if not self.add_timestamps:
            return metadata
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        metadata["enriched_at"] = current_time
        metadata["enriched_timestamp"] = current_time
        
        return metadata
    
    def _enrich_chunk_metadata(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich metadata for a single chunk."""
        if not self.auto_generate_metadata:
            return chunk_data
        
        text = chunk_data.get("text", "") or chunk_data.get("body", "")
        
        if not text:
            return chunk_data
        
        # Initialize metadata if not present
        if "metadata" not in chunk_data:
            chunk_data["metadata"] = {}
        
        metadata = chunk_data["metadata"]
        
        # Detect language
        if self.detect_language:
            metadata["detected_language"] = self._detect_language(text)
        
        # Extract keywords
        if self.extract_keywords:
            keywords = self._extract_keywords(text)
            if keywords:
                metadata["keywords"] = keywords
        
        # Calculate metrics
        if self.calculate_metrics:
            metrics = self._calculate_text_metrics(text)
            metadata["text_metrics"] = metrics
        
        # Generate content hash
        if self.generate_hashes:
            content_hash = self._generate_content_hash(text)
            if content_hash:
                metadata["content_hash"] = content_hash
        
        # Add timestamps
        metadata = self._add_timestamps(metadata)
        
        # Mark as enriched
        metadata["enriched"] = True
        
        chunk_data["metadata"] = metadata
        return chunk_data
    
    async def execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute metadata enrichment.
        
        Parameters:
            data: Input data containing chunks
            context: Optional context
            
        Returns:
            Dict[str, Any]: Processed data with enriched metadata
        """
        # Handle different input formats
        if "chunk" in data:
            # Single chunk
            chunk_data = data["chunk"]
            enriched_chunk = self._enrich_chunk_metadata(chunk_data)
            data["chunk"] = enriched_chunk
            data["metadata_enriched"] = True
            
        elif "chunks" in data:
            # Multiple chunks
            chunks = data["chunks"]
            enriched_chunks = []
            
            for chunk in chunks:
                if isinstance(chunk, dict):
                    enriched_chunk = self._enrich_chunk_metadata(chunk)
                    enriched_chunks.append(enriched_chunk)
                else:
                    # Assume it's a SemanticChunk object
                    chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else vars(chunk)
                    enriched_dict = self._enrich_chunk_metadata(chunk_dict)
                    
                    # Update the object with enriched metadata
                    if hasattr(chunk, 'metadata'):
                        chunk.metadata = enriched_dict.get("metadata", {})
                    enriched_chunks.append(chunk)
            
            data["chunks"] = enriched_chunks
            data["metadata_enriched"] = True
            
        elif "text" in data or "body" in data:
            # Single text item
            text_data = data.copy()
            enriched_data = self._enrich_chunk_metadata(text_data)
            data.update(enriched_data)
            data["metadata_enriched"] = True
            
        return data
    
    async def pre_execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pre-execution validation."""
        # Check if we have data to enrich
        has_data = any(key in data for key in ["chunk", "chunks", "text", "body"])
        if not has_data:
            self.logger.warning("No data found for metadata enrichment")
        
        return data
    
    async def post_execute(
        self, 
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post-execution logging."""
        if "metadata_enriched" in result:
            self.logger.info("Metadata enrichment completed")
        
        return result
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """
        Get enrichment statistics.
        
        Returns:
            Dict[str, Any]: Enrichment statistics
        """
        return {
            "plugin_name": self.get_name(),
            "version": self.get_version(),
            "config": {
                "detect_language": self.detect_language,
                "extract_keywords": self.extract_keywords,
                "calculate_metrics": self.calculate_metrics,
                "generate_hashes": self.generate_hashes,
                "add_timestamps": self.add_timestamps,
                "max_keywords": self.max_keywords,
                "min_keyword_length": self.min_keyword_length
            },
            "description": self.get_description()
        } 