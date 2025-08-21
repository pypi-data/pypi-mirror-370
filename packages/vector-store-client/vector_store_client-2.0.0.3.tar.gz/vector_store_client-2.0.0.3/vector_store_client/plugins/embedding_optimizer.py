"""
Embedding optimizer plugin for Vector Store Client.

This plugin provides embedding optimization capabilities including
vector normalization, dimensionality reduction, and quality checks.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import numpy as np
from typing import Dict, Any, Optional, List
from .base_plugin import BasePlugin


class EmbeddingOptimizerPlugin(BasePlugin):
    """
    Plugin for embedding optimization.
    
    Provides embedding vector optimization, normalization,
    and quality assessment capabilities.
    """
    
    def __init__(self, client=None, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.client = client
        self.config = config or {}
        self._setup_config()
    
    def get_name(self) -> str:
        return "embedding_optimizer"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Embedding optimization plugin for vector enhancement"
    
    def _setup_config(self) -> None:
        """Setup plugin configuration with defaults."""
        self.normalize_vectors = self.config.get("normalize_vectors", True)
        self.check_quality = self.config.get("check_quality", True)
        self.min_quality_score = self.config.get("min_quality_score", 0.1)
        self.expected_dimension = self.config.get("expected_dimension", 384)
        self.remove_zero_vectors = self.config.get("remove_zero_vectors", True)
        self.add_noise = self.config.get("add_noise", False)
        self.noise_factor = self.config.get("noise_factor", 0.01)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get plugin configuration schema."""
        return {
            "normalize_vectors": {
                "type": "boolean",
                "default": True,
                "description": "Normalize embedding vectors"
            },
            "check_quality": {
                "type": "boolean",
                "default": True,
                "description": "Check embedding quality"
            },
            "min_quality_score": {
                "type": "float",
                "default": 0.1,
                "description": "Minimum quality score threshold"
            },
            "expected_dimension": {
                "type": "integer",
                "default": 384,
                "description": "Expected embedding dimension"
            },
            "remove_zero_vectors": {
                "type": "boolean",
                "default": True,
                "description": "Remove zero vectors"
            },
            "add_noise": {
                "type": "boolean",
                "default": False,
                "description": "Add small noise to vectors"
            },
            "noise_factor": {
                "type": "float",
                "default": 0.01,
                "description": "Noise factor for vector perturbation"
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if "min_quality_score" in config:
            if not 0 <= config["min_quality_score"] <= 1:
                raise ValueError("min_quality_score must be between 0 and 1")
        if "expected_dimension" in config and config["expected_dimension"] < 1:
            raise ValueError("expected_dimension must be positive")
        if "noise_factor" in config and config["noise_factor"] < 0:
            raise ValueError("noise_factor must be non-negative")
        return True
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize embedding vector."""
        if not self.normalize_vectors:
            return vector
        
        vector_array = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vector_array)
        
        if norm > 0:
            normalized = vector_array / norm
            return normalized.tolist()
        else:
            return vector
    
    def _check_vector_quality(self, vector: List[float]) -> Dict[str, Any]:
        """Check embedding vector quality."""
        if not self.check_quality:
            return {"quality_score": 1.0, "is_valid": True}
        
        vector_array = np.array(vector, dtype=np.float32)
        
        # Check dimension
        dimension = len(vector)
        dimension_valid = dimension == self.expected_dimension
        
        # Check for zero vector
        norm = np.linalg.norm(vector_array)
        zero_vector = norm == 0
        
        # Check for NaN or infinite values
        has_nan = np.any(np.isnan(vector_array))
        has_inf = np.any(np.isinf(vector_array))
        
        # Calculate quality score
        quality_score = 0.0
        
        if dimension_valid:
            quality_score += 0.3
        if not zero_vector:
            quality_score += 0.3
        if not has_nan:
            quality_score += 0.2
        if not has_inf:
            quality_score += 0.2
        
        is_valid = (quality_score >= self.min_quality_score and 
                   dimension_valid and not has_nan and not has_inf)
        
        return {
            "quality_score": quality_score,
            "is_valid": is_valid,
            "dimension": dimension,
            "expected_dimension": self.expected_dimension,
            "norm": float(norm),
            "has_nan": has_nan,
            "has_inf": has_inf,
            "zero_vector": zero_vector
        }
    
    def _add_noise_to_vector(self, vector: List[float]) -> List[float]:
        """Add small noise to vector for regularization."""
        if not self.add_noise:
            return vector
        
        vector_array = np.array(vector, dtype=np.float32)
        noise = np.random.normal(0, self.noise_factor, vector_array.shape)
        noisy_vector = vector_array + noise
        
        return noisy_vector.tolist()
    
    def _optimize_embedding(self, embedding: List[float]) -> Dict[str, Any]:
        """Optimize a single embedding vector."""
        # Check quality first
        quality_info = self._check_vector_quality(embedding)
        
        if not quality_info["is_valid"]:
            return {
                "embedding": embedding,
                "optimized": False,
                "quality_info": quality_info,
                "error": "Embedding failed quality check"
            }
        
        optimized_embedding = embedding.copy()
        
        # Add noise if enabled
        if self.add_noise:
            optimized_embedding = self._add_noise_to_vector(optimized_embedding)
        
        # Normalize vector
        optimized_embedding = self._normalize_vector(optimized_embedding)
        
        # Re-check quality after optimization
        final_quality = self._check_vector_quality(optimized_embedding)
        
        return {
            "embedding": optimized_embedding,
            "optimized": True,
            "quality_info": final_quality,
            "original_quality": quality_info
        }
    
    async def execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute embedding optimization.
        
        Parameters:
            data: Input data containing embeddings
            context: Optional context
            
        Returns:
            Dict[str, Any]: Processed data with optimized embeddings
        """
        # Handle different input formats
        if "embedding" in data:
            embedding = data["embedding"]
            if embedding:
                result = self._optimize_embedding(embedding)
                data["embedding"] = result["embedding"]
                data["embedding_optimized"] = result["optimized"]
                data["embedding_quality"] = result["quality_info"]
                
        elif "chunks" in data:
            # Process multiple chunks
            chunks = data["chunks"]
            optimized_chunks = []
            total_optimized = 0
            total_failed = 0
            
            for chunk in chunks:
                if isinstance(chunk, dict) and "embedding" in chunk:
                    embedding = chunk["embedding"]
                    if embedding:
                        result = self._optimize_embedding(embedding)
                        chunk["embedding"] = result["embedding"]
                        chunk["embedding_optimized"] = result["optimized"]
                        chunk["embedding_quality"] = result["quality_info"]
                        
                        if result["optimized"]:
                            total_optimized += 1
                        else:
                            total_failed += 1
                            
                    optimized_chunks.append(chunk)
                else:
                    # Assume it's a SemanticChunk object
                    if hasattr(chunk, 'embedding') and chunk.embedding:
                        result = self._optimize_embedding(chunk.embedding)
                        chunk.embedding = result["embedding"]
                        if not hasattr(chunk, 'block_meta') or chunk.block_meta is None:
                            chunk.block_meta = {}
                        chunk.block_meta["embedding_optimized"] = result["optimized"]
                        chunk.block_meta["embedding_quality"] = result["quality_info"]
                        
                        if result["optimized"]:
                            total_optimized += 1
                        else:
                            total_failed += 1
                            
                    optimized_chunks.append(chunk)
            
            data["chunks"] = optimized_chunks
            data["embeddings_optimized"] = True
            data["optimization_stats"] = {
                "total_optimized": total_optimized,
                "total_failed": total_failed,
                "total_processed": len(chunks)
            }
            
        return data
    
    async def pre_execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pre-execution validation."""
        # Check if we have embeddings to process
        has_embedding = any(key in data for key in ["embedding", "chunks"])
        if not has_embedding:
            self.logger.warning("No embedding data found for optimization")
        
        return data
    
    async def post_execute(
        self, 
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post-execution logging."""
        if "embedding_optimized" in result:
            self.logger.info("Single embedding optimization completed")
        elif "embeddings_optimized" in result:
            stats = result.get("optimization_stats", {})
            self.logger.info(
                f"Embedding optimization completed: "
                f"{stats.get('total_optimized', 0)} optimized, "
                f"{stats.get('total_failed', 0)} failed"
            )
        
        return result
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get optimization statistics.
        
        Returns:
            Dict[str, Any]: Optimization statistics
        """
        return {
            "plugin_name": self.get_name(),
            "version": self.get_version(),
            "config": {
                "normalize_vectors": self.normalize_vectors,
                "check_quality": self.check_quality,
                "min_quality_score": self.min_quality_score,
                "expected_dimension": self.expected_dimension,
                "remove_zero_vectors": self.remove_zero_vectors,
                "add_noise": self.add_noise,
                "noise_factor": self.noise_factor
            },
            "description": self.get_description()
        } 