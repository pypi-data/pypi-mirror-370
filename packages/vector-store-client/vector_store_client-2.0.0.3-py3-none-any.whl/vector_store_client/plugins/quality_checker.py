"""
Quality checker plugin for Vector Store Client.

This plugin provides quality assessment capabilities for chunks
including content validation, embedding quality checks, and
metadata validation.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import re
from typing import Dict, Any, Optional, List
from .base_plugin import BasePlugin


class QualityCheckerPlugin(BasePlugin):
    """
    Plugin for quality checking.
    
    Provides quality assessment, validation, and filtering
    capabilities for chunks and embeddings.
    """
    
    def __init__(self, client=None, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.client = client
        self.config = config or {}
        self._setup_config()
    
    def get_name(self) -> str:
        return "quality_checker"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Quality checker plugin for content and embedding validation"
    
    def _setup_config(self) -> None:
        """Setup plugin configuration with defaults."""
        self.check_content_quality = self.config.get("check_content_quality", True)
        self.check_embedding_quality = self.config.get("check_embedding_quality", True)
        self.check_metadata_quality = self.config.get("check_metadata_quality", True)
        self.min_content_length = self.config.get("min_content_length", 10)
        self.max_content_length = self.config.get("max_content_length", 10000)
        self.min_embedding_norm = self.config.get("min_embedding_norm", 0.1)
        self.expected_embedding_dim = self.config.get("expected_embedding_dim", 384)
        self.filter_low_quality = self.config.get("filter_low_quality", False)
        self.quality_threshold = self.config.get("quality_threshold", 0.5)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema."""
        return {
            "check_content_quality": {
                "type": "boolean",
                "default": True,
                "description": "Check content quality"
            },
            "check_embedding_quality": {
                "type": "boolean",
                "default": True,
                "description": "Check embedding quality"
            },
            "check_metadata_quality": {
                "type": "boolean",
                "default": True,
                "description": "Check metadata quality"
            },
            "min_content_length": {
                "type": "integer",
                "default": 10,
                "description": "Minimum content length"
            },
            "max_content_length": {
                "type": "integer",
                "default": 10000,
                "description": "Maximum content length"
            },
            "min_embedding_norm": {
                "type": "float",
                "default": 0.1,
                "description": "Minimum embedding norm"
            },
            "expected_embedding_dim": {
                "type": "integer",
                "default": 384,
                "description": "Expected embedding dimension"
            },
            "filter_low_quality": {
                "type": "boolean",
                "default": False,
                "description": "Filter out low quality chunks"
            },
            "quality_threshold": {
                "type": "float",
                "default": 0.5,
                "description": "Quality threshold for filtering"
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if "min_content_length" in config and config["min_content_length"] < 0:
            raise ValueError("min_content_length must be non-negative")
        if "max_content_length" in config and config["max_content_length"] < 1:
            raise ValueError("max_content_length must be positive")
        if "min_embedding_norm" in config and config["min_embedding_norm"] < 0:
            raise ValueError("min_embedding_norm must be non-negative")
        if "expected_embedding_dim" in config and config["expected_embedding_dim"] < 1:
            raise ValueError("expected_embedding_dim must be positive")
        if "quality_threshold" in config and not 0 <= config["quality_threshold"] <= 1:
            raise ValueError("quality_threshold must be between 0 and 1")
        return True
    
    def _check_content_quality(self, text: str) -> Dict[str, Any]:
        """Check content quality."""
        if not self.check_content_quality:
            return {"quality_score": 1.0, "is_valid": True}
        
        if not text:
            return {"quality_score": 0.0, "is_valid": False, "error": "Empty content"}
        
        # Basic quality checks
        length = len(text)
        word_count = len(text.split())
        
        # Length checks
        length_valid = self.min_content_length <= length <= self.max_content_length
        length_score = 1.0 if length_valid else 0.0
        
        # Word count check
        word_count_valid = word_count >= 2
        word_count_score = 1.0 if word_count_valid else 0.0
        
        # Character diversity check
        unique_chars = len(set(text))
        char_diversity_score = min(1.0, unique_chars / max(1, length))
        
        # Repetition check
        words = text.split()
        if len(words) > 0:
            unique_words = len(set(words))
            repetition_score = unique_words / len(words)
        else:
            repetition_score = 0.0
        
        # Overall quality score
        quality_score = (length_score * 0.3 + 
                        word_count_score * 0.2 + 
                        char_diversity_score * 0.25 + 
                        repetition_score * 0.25)
        
        is_valid = (length_valid and word_count_valid and quality_score >= self.quality_threshold)
        
        return {
            "quality_score": round(quality_score, 3),
            "is_valid": is_valid,
            "length": length,
            "word_count": word_count,
            "unique_chars": unique_chars,
            "unique_words": unique_words if len(words) > 0 else 0,
            "length_valid": length_valid,
            "word_count_valid": word_count_valid,
            "char_diversity_score": round(char_diversity_score, 3),
            "repetition_score": round(repetition_score, 3)
        }
    
    def _check_embedding_quality(self, embedding: List[float]) -> Dict[str, Any]:
        """Check embedding quality."""
        if not self.check_embedding_quality:
            return {"quality_score": 1.0, "is_valid": True}
        
        if not embedding:
            return {"quality_score": 0.0, "is_valid": False, "error": "Empty embedding"}
        
        import numpy as np
        
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Dimension check
        dimension = len(embedding)
        dimension_valid = dimension == self.expected_embedding_dim
        dimension_score = 1.0 if dimension_valid else 0.0
        
        # Norm check
        norm = np.linalg.norm(embedding_array)
        norm_valid = norm >= self.min_embedding_norm
        norm_score = min(1.0, norm / max(self.min_embedding_norm, 1.0))
        
        # NaN/Inf check
        has_nan = np.any(np.isnan(embedding_array))
        has_inf = np.any(np.isinf(embedding_array))
        nan_inf_valid = not (has_nan or has_inf)
        nan_inf_score = 1.0 if nan_inf_valid else 0.0
        
        # Zero vector check
        zero_vector = norm == 0
        zero_vector_valid = not zero_vector
        zero_vector_score = 1.0 if zero_vector_valid else 0.0
        
        # Overall quality score
        quality_score = (dimension_score * 0.3 + 
                        norm_score * 0.3 + 
                        nan_inf_score * 0.2 + 
                        zero_vector_score * 0.2)
        
        is_valid = (dimension_valid and norm_valid and nan_inf_valid and 
                   zero_vector_valid and quality_score >= self.quality_threshold)
        
        return {
            "quality_score": round(quality_score, 3),
            "is_valid": is_valid,
            "dimension": dimension,
            "expected_dimension": self.expected_embedding_dim,
            "norm": float(norm),
            "has_nan": has_nan,
            "has_inf": has_inf,
            "zero_vector": zero_vector,
            "dimension_valid": dimension_valid,
            "norm_valid": norm_valid,
            "nan_inf_valid": nan_inf_valid,
            "zero_vector_valid": zero_vector_valid
        }
    
    def _check_metadata_quality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check metadata quality."""
        if not self.check_metadata_quality:
            return {"quality_score": 1.0, "is_valid": True}
        
        if not metadata:
            return {"quality_score": 0.0, "is_valid": False, "error": "Empty metadata"}
        
        # Required fields check
        required_fields = ["uuid", "created_at"]
        present_fields = sum(1 for field in required_fields if field in metadata)
        required_fields_score = present_fields / len(required_fields)
        
        # Metadata completeness check
        total_fields = len(metadata)
        completeness_score = min(1.0, total_fields / 10)  # Normalize to 10 fields
        
        # Data type validation
        type_valid = True
        type_errors = []
        
        for key, value in metadata.items():
            if key == "uuid" and not isinstance(value, str):
                type_valid = False
                type_errors.append(f"uuid must be string, got {type(value)}")
            elif key == "created_at" and not isinstance(value, str):
                type_valid = False
                type_errors.append(f"created_at must be string, got {type(value)}")
        
        type_score = 1.0 if type_valid else 0.0
        
        # Overall quality score
        quality_score = (required_fields_score * 0.4 + 
                        completeness_score * 0.3 + 
                        type_score * 0.3)
        
        is_valid = (required_fields_score > 0 and type_valid and 
                   quality_score >= self.quality_threshold)
        
        return {
            "quality_score": round(quality_score, 3),
            "is_valid": is_valid,
            "total_fields": total_fields,
            "present_required_fields": present_fields,
            "total_required_fields": len(required_fields),
            "type_valid": type_valid,
            "type_errors": type_errors,
            "required_fields_score": round(required_fields_score, 3),
            "completeness_score": round(completeness_score, 3),
            "type_score": round(type_score, 3)
        }
    
    def _check_chunk_quality(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality for a single chunk."""
        quality_results = {}
        
        # Check content quality
        text = chunk_data.get("text", "") or chunk_data.get("body", "")
        if text:
            content_quality = self._check_content_quality(text)
            quality_results["content_quality"] = content_quality
        
        # Check embedding quality
        embedding = chunk_data.get("embedding", [])
        if embedding:
            embedding_quality = self._check_embedding_quality(embedding)
            quality_results["embedding_quality"] = embedding_quality
        
        # Check metadata quality
        metadata = chunk_data.get("metadata", {})
        if metadata:
            metadata_quality = self._check_metadata_quality(metadata)
            quality_results["metadata_quality"] = metadata_quality
        
        # Calculate overall quality score
        quality_scores = []
        for quality_type, result in quality_results.items():
            if "quality_score" in result:
                quality_scores.append(result["quality_score"])
        
        if quality_scores:
            overall_quality = sum(quality_scores) / len(quality_scores)
        else:
            overall_quality = 0.0
        
        # Determine if chunk passes quality check
        all_valid = all(result.get("is_valid", True) for result in quality_results.values())
        passes_quality_check = all_valid and overall_quality >= self.quality_threshold
        
        quality_results["overall_quality"] = round(overall_quality, 3)
        quality_results["passes_quality_check"] = passes_quality_check
        
        return quality_results
    
    async def execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute quality checking.
        
        Parameters:
            data: Input data containing chunks
            context: Optional context
            
        Returns:
            Dict[str, Any]: Processed data with quality information
        """
        # Handle different input formats
        if "chunk" in data:
            # Single chunk
            chunk_data = data["chunk"]
            quality_results = self._check_chunk_quality(chunk_data)
            data["quality_results"] = quality_results
            data["quality_checked"] = True
            
            # Filter if enabled
            if self.filter_low_quality and not quality_results.get("passes_quality_check", True):
                data["filtered_out"] = True
                data["chunk"] = None
            
        elif "chunks" in data:
            # Multiple chunks
            chunks = data["chunks"]
            quality_results_list = []
            filtered_chunks = []
            
            for chunk in chunks:
                if isinstance(chunk, dict):
                    chunk_quality = self._check_chunk_quality(chunk)
                    chunk["quality_results"] = chunk_quality
                    
                    if self.filter_low_quality and not chunk_quality.get("passes_quality_check", True):
                        chunk["filtered_out"] = True
                    else:
                        filtered_chunks.append(chunk)
                    
                    quality_results_list.append(chunk_quality)
                else:
                    # Assume it's a SemanticChunk object
                    chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else vars(chunk)
                    chunk_quality = self._check_chunk_quality(chunk_dict)
                    
                    # Add quality results to object
                    if hasattr(chunk, 'quality_results'):
                        chunk.quality_results = chunk_quality
                    
                    if self.filter_low_quality and not chunk_quality.get("passes_quality_check", True):
                        if hasattr(chunk, 'filtered_out'):
                            chunk.filtered_out = True
                    else:
                        filtered_chunks.append(chunk)
                    
                    quality_results_list.append(chunk_quality)
            
            # Update chunks list based on filtering
            if self.filter_low_quality:
                data["chunks"] = filtered_chunks
                data["original_chunk_count"] = len(chunks)
                data["filtered_chunk_count"] = len(filtered_chunks)
            
            data["quality_results"] = quality_results_list
            data["quality_checked"] = True
            
        return data
    
    async def pre_execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pre-execution validation."""
        # Check if we have data to quality check
        has_data = any(key in data for key in ["chunk", "chunks"])
        if not has_data:
            self.logger.warning("No data found for quality checking")
        
        return data
    
    async def post_execute(
        self, 
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post-execution logging."""
        if "quality_checked" in result:
            if "filtered_chunk_count" in result:
                original_count = result.get("original_chunk_count", 0)
                filtered_count = result.get("filtered_chunk_count", 0)
                self.logger.info(f"Quality check completed: {filtered_count}/{original_count} chunks passed")
            else:
                self.logger.info("Quality check completed")
        
        return result
    
    def get_quality_stats(self) -> Dict[str, Any]:
        """
        Get quality checking statistics.
        
        Returns:
            Dict[str, Any]: Quality checking statistics
        """
        return {
            "plugin_name": self.get_name(),
            "version": self.get_version(),
            "config": {
                "quality_threshold": self.quality_threshold,
                "check_content": self.check_content_quality,
                "check_embedding": self.check_embedding_quality,
                "check_metadata": self.check_metadata_quality,
                "filter_low_quality": self.filter_low_quality,
                "min_content_length": self.min_content_length,
                "max_content_length": self.max_content_length,
                "min_embedding_norm": self.min_embedding_norm,
                "expected_embedding_dim": self.expected_embedding_dim
            },
            "description": self.get_description()
        } 