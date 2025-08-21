"""
Tests for QualityCheckerPlugin.

This module contains comprehensive unit tests for the QualityCheckerPlugin class
to achieve 80%+ code coverage.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from vector_store_client.plugins.quality_checker import QualityCheckerPlugin
from vector_store_client.exceptions import ValidationError


class TestQualityCheckerPlugin:
    """Test cases for QualityCheckerPlugin class."""
    
    @pytest.fixture
    def plugin(self):
        """Create a QualityCheckerPlugin instance."""
        return QualityCheckerPlugin()
    
    @pytest.fixture
    def plugin_with_config(self):
        """Create a QualityCheckerPlugin instance with custom config."""
        config = {
            "check_content_quality": True,
            "check_embedding_quality": True,
            "check_metadata_quality": True,
            "min_content_length": 5,
            "max_content_length": 100,
            "min_embedding_norm": 0.1,
            "expected_embedding_dim": 384,
            "filter_low_quality": True,
            "quality_threshold": 0.7
        }
        return QualityCheckerPlugin(config=config)
    
    def test_plugin_creation(self, plugin):
        """Test plugin creation."""
        assert plugin is not None
        assert plugin.get_name() == "quality_checker"
        assert plugin.get_version() == "1.0.0"
        assert plugin.get_description() == "Quality checker plugin for content and embedding validation"
    
    def test_plugin_creation_with_config(self, plugin_with_config):
        """Test plugin creation with custom configuration."""
        assert plugin_with_config.check_content_quality is True
        assert plugin_with_config.check_embedding_quality is True
        assert plugin_with_config.check_metadata_quality is True
        assert plugin_with_config.min_content_length == 5
        assert plugin_with_config.max_content_length == 100
        assert plugin_with_config.min_embedding_norm == 0.1
        assert plugin_with_config.expected_embedding_dim == 384
        assert plugin_with_config.filter_low_quality is True
        assert plugin_with_config.quality_threshold == 0.7
    
    def test_get_config_schema(self, plugin):
        """Test get_config_schema method."""
        schema = plugin.get_config_schema()
        
        assert "check_content_quality" in schema
        assert "check_embedding_quality" in schema
        assert "check_metadata_quality" in schema
        assert "min_content_length" in schema
        assert "max_content_length" in schema
        assert "min_embedding_norm" in schema
        assert "expected_embedding_dim" in schema
        assert "filter_low_quality" in schema
        assert "quality_threshold" in schema
        
        # Check schema structure
        for key, config in schema.items():
            assert "type" in config
            assert "default" in config
            assert "description" in config
    
    def test_validate_config_valid(self, plugin):
        """Test validate_config with valid configuration."""
        config = {
            "min_content_length": 10,
            "max_content_length": 1000,
            "min_embedding_norm": 0.1,
            "expected_embedding_dim": 384,
            "quality_threshold": 0.5
        }
        assert plugin.validate_config(config) is True
    
    def test_validate_config_invalid_min_content_length(self, plugin):
        """Test validate_config with invalid min_content_length."""
        config = {"min_content_length": -1}
        with pytest.raises(ValueError, match="min_content_length must be non-negative"):
            plugin.validate_config(config)
    
    def test_validate_config_invalid_max_content_length(self, plugin):
        """Test validate_config with invalid max_content_length."""
        config = {"max_content_length": 0}
        with pytest.raises(ValueError, match="max_content_length must be positive"):
            plugin.validate_config(config)
    
    def test_validate_config_invalid_min_embedding_norm(self, plugin):
        """Test validate_config with invalid min_embedding_norm."""
        config = {"min_embedding_norm": -0.1}
        with pytest.raises(ValueError, match="min_embedding_norm must be non-negative"):
            plugin.validate_config(config)
    
    def test_validate_config_invalid_expected_embedding_dim(self, plugin):
        """Test validate_config with invalid expected_embedding_dim."""
        config = {"expected_embedding_dim": 0}
        with pytest.raises(ValueError, match="expected_embedding_dim must be positive"):
            plugin.validate_config(config)
    
    def test_validate_config_invalid_quality_threshold(self, plugin):
        """Test validate_config with invalid quality_threshold."""
        config = {"quality_threshold": 1.5}
        with pytest.raises(ValueError, match="quality_threshold must be between 0 and 1"):
            plugin.validate_config(config)
    
    def test_validate_config_quality_threshold_zero(self, plugin):
        """Test validate_config with quality_threshold = 0."""
        config = {"quality_threshold": 0}
        assert plugin.validate_config(config) is True
    
    def test_validate_config_quality_threshold_one(self, plugin):
        """Test validate_config with quality_threshold = 1."""
        config = {"quality_threshold": 1}
        assert plugin.validate_config(config) is True
    
    def test_check_content_quality_disabled(self, plugin):
        """Test content quality check when disabled."""
        plugin.check_content_quality = False
        result = plugin._check_content_quality("test text")
        
        assert result["quality_score"] == 1.0
        assert result["is_valid"] is True
    
    def test_check_content_quality_empty_text(self, plugin):
        """Test content quality check with empty text."""
        result = plugin._check_content_quality("")
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty content"
    
    def test_check_content_quality_none_text(self, plugin):
        """Test content quality check with None text."""
        result = plugin._check_content_quality(None)
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty content"
    
    def test_check_content_quality_good_text(self, plugin):
        """Test content quality check with good text."""
        text = "This is a good quality text with meaningful content and proper length."
        result = plugin._check_content_quality(text)
        
        assert result["quality_score"] > 0.5
        assert result["is_valid"] is True
        assert "length" in result
        assert "word_count" in result
        assert "unique_chars" in result
        assert "unique_words" in result
        assert "length_valid" in result
        assert "word_count_valid" in result
        assert "char_diversity_score" in result
        assert "repetition_score" in result
    
    def test_check_content_quality_too_short(self, plugin):
        """Test content quality check with too short text."""
        plugin.min_content_length = 20
        text = "Short"
        result = plugin._check_content_quality(text)
        
        assert result["quality_score"] <= 0.5
        assert result["is_valid"] is False
        assert result["length_valid"] is False
    
    def test_check_content_quality_too_long(self, plugin):
        """Test content quality check with too long text."""
        plugin.max_content_length = 10
        text = "This is a very long text that should fail the length check"
        result = plugin._check_content_quality(text)
        
        assert result["quality_score"] <= 0.6
        assert result["is_valid"] is False
        assert result["length_valid"] is False
    
    def test_check_content_quality_single_word(self, plugin):
        """Test content quality check with single word."""
        text = "Word"
        result = plugin._check_content_quality(text)
        
        assert result["word_count_valid"] is False
        assert result["is_valid"] is False
    
    def test_check_content_quality_repetitive_text(self, plugin):
        """Test content quality check with repetitive text."""
        text = "word word word word word word word word word word"
        result = plugin._check_content_quality(text)
        
        assert result["repetition_score"] < 1.0
        assert result["unique_words"] == 1
    
    def test_check_content_quality_empty_words(self, plugin):
        """Test content quality check with empty words list."""
        text = "   "  # Only whitespace
        result = plugin._check_content_quality(text)
        
        assert result["repetition_score"] == 0.0
        assert result["unique_words"] == 0
    
    def test_check_embedding_quality_disabled(self, plugin):
        """Test embedding quality check when disabled."""
        plugin.check_embedding_quality = False
        embedding = [0.1] * 384
        result = plugin._check_embedding_quality(embedding)
        
        assert result["quality_score"] == 1.0
        assert result["is_valid"] is True
    
    def test_check_embedding_quality_empty_embedding(self, plugin):
        """Test embedding quality check with empty embedding."""
        result = plugin._check_embedding_quality([])
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty embedding"
    
    def test_check_embedding_quality_none_embedding(self, plugin):
        """Test embedding quality check with None embedding."""
        result = plugin._check_embedding_quality(None)
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty embedding"
    
    def test_check_embedding_quality_good_embedding(self, plugin):
        """Test embedding quality check with good embedding."""
        embedding = [0.1] * 384
        result = plugin._check_embedding_quality(embedding)
        
        assert result["quality_score"] > 0.5
        assert result["is_valid"] is True
        assert "dimension" in result
        assert "expected_dimension" in result
        assert "norm" in result
        assert "has_nan" in result
        assert "has_inf" in result
        assert "zero_vector" in result
        assert "dimension_valid" in result
        assert "norm_valid" in result
        assert "nan_inf_valid" in result
        assert "zero_vector_valid" in result
    
    def test_check_embedding_quality_wrong_dimension(self, plugin):
        """Test embedding quality check with wrong dimension."""
        plugin.expected_embedding_dim = 384
        embedding = [0.1] * 256  # Wrong dimension
        result = plugin._check_embedding_quality(embedding)
        
        assert result["dimension_valid"] is False
        assert result["is_valid"] is False
    
    def test_check_embedding_quality_zero_norm(self, plugin):
        """Test embedding quality check with zero norm."""
        plugin.min_embedding_norm = 0.1
        embedding = [0.0] * 384  # Zero vector
        result = plugin._check_embedding_quality(embedding)
        
        assert bool(result["zero_vector"]) is True
        assert bool(result["zero_vector_valid"]) is False
        assert bool(result["is_valid"]) is False
    
    def test_check_embedding_quality_nan_values(self, plugin):
        """Test embedding quality check with NaN values."""
        embedding = [0.1] * 383 + [float('nan')]
        result = plugin._check_embedding_quality(embedding)
        
        assert bool(result["has_nan"]) is True
        assert bool(result["nan_inf_valid"]) is False
        assert bool(result["is_valid"]) is False
    
    def test_check_embedding_quality_inf_values(self, plugin):
        """Test embedding quality check with Inf values."""
        embedding = [0.1] * 383 + [float('inf')]
        result = plugin._check_embedding_quality(embedding)
        
        assert bool(result["has_inf"]) is True
        assert result["nan_inf_valid"] is False
        assert result["is_valid"] is False
    
    def test_check_embedding_quality_low_norm(self, plugin):
        """Test embedding quality check with low norm."""
        plugin.min_embedding_norm = 1.0
        embedding = [0.01] * 384  # Low norm
        result = plugin._check_embedding_quality(embedding)
        
        assert bool(result["norm_valid"]) is False
        assert bool(result["is_valid"]) is False
    
    def test_check_metadata_quality_disabled(self, plugin):
        """Test metadata quality check when disabled."""
        plugin.check_metadata_quality = False
        metadata = {"uuid": "test", "created_at": "2023-01-01"}
        result = plugin._check_metadata_quality(metadata)
        
        assert result["quality_score"] == 1.0
        assert result["is_valid"] is True
    
    def test_check_metadata_quality_empty_metadata(self, plugin):
        """Test metadata quality check with empty metadata."""
        result = plugin._check_metadata_quality({})
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty metadata"
    
    def test_check_metadata_quality_none_metadata(self, plugin):
        """Test metadata quality check with None metadata."""
        result = plugin._check_metadata_quality(None)
        
        assert result["quality_score"] == 0.0
        assert result["is_valid"] is False
        assert "error" in result
        assert result["error"] == "Empty metadata"
    
    def test_check_metadata_quality_good_metadata(self, plugin):
        """Test metadata quality check with good metadata."""
        metadata = {
            "uuid": "test-uuid",
            "created_at": "2023-01-01T00:00:00Z",
            "source": "test",
            "author": "test"
        }
        result = plugin._check_metadata_quality(metadata)
        
        assert result["quality_score"] > 0.5
        assert result["is_valid"] is True
        assert "total_fields" in result
        assert "present_required_fields" in result
        assert "total_required_fields" in result
        assert "type_valid" in result
        assert "type_errors" in result
        assert "required_fields_score" in result
        assert "completeness_score" in result
        assert "type_score" in result
    
    def test_check_metadata_quality_missing_required_fields(self, plugin):
        """Test metadata quality check with missing required fields."""
        metadata = {"source": "test"}  # Missing uuid and created_at
        result = plugin._check_metadata_quality(metadata)
        
        assert result["present_required_fields"] == 0
        assert result["required_fields_score"] == 0.0
        assert result["is_valid"] is False
    
    def test_check_metadata_quality_partial_required_fields(self, plugin):
        """Test metadata quality check with partial required fields."""
        plugin.quality_threshold = 0.6  # Set higher threshold
        metadata = {"uuid": "test-uuid"}  # Missing created_at
        result = plugin._check_metadata_quality(metadata)
        
        assert result["present_required_fields"] == 1
        assert result["required_fields_score"] == 0.5
        assert result["is_valid"] is False
    
    def test_check_metadata_quality_invalid_types(self, plugin):
        """Test metadata quality check with invalid types."""
        metadata = {
            "uuid": 123,  # Should be string
            "created_at": 456  # Should be string
        }
        result = plugin._check_metadata_quality(metadata)
        
        assert result["type_valid"] is False
        assert len(result["type_errors"]) == 2
        assert result["is_valid"] is False
    
    def test_check_metadata_quality_completeness(self, plugin):
        """Test metadata quality check completeness scoring."""
        # Test with many fields
        metadata = {
            "uuid": "test",
            "created_at": "2023-01-01",
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
            "field4": "value4",
            "field5": "value5",
            "field6": "value6",
            "field7": "value7",
            "field8": "value8",
            "field9": "value9",
            "field10": "value10"
        }
        result = plugin._check_metadata_quality(metadata)
        
        assert result["completeness_score"] == 1.0  # 12 fields / 10 = 1.0
    
    def test_check_chunk_quality_with_text(self, plugin):
        """Test chunk quality check with text."""
        chunk_data = {"text": "This is a good quality text with meaningful content."}
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "content_quality" in result
        assert "overall_quality" in result
        assert "passes_quality_check" in result
    
    def test_check_chunk_quality_with_embedding(self, plugin):
        """Test chunk quality check with embedding."""
        chunk_data = {"embedding": [0.1] * 384}
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "embedding_quality" in result
        assert "overall_quality" in result
        assert "passes_quality_check" in result
    
    def test_check_chunk_quality_with_metadata(self, plugin):
        """Test chunk quality check with metadata."""
        chunk_data = {
            "metadata": {
                "uuid": "test-uuid",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "metadata_quality" in result
        assert "overall_quality" in result
        assert "passes_quality_check" in result
    
    def test_check_chunk_quality_with_body(self, plugin):
        """Test chunk quality check with body field."""
        chunk_data = {"body": "This is a good quality text with meaningful content."}
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "content_quality" in result
        assert "overall_quality" in result
        assert "passes_quality_check" in result
    
    def test_check_chunk_quality_with_all_fields(self, plugin):
        """Test chunk quality check with all fields."""
        chunk_data = {
            "text": "This is a good quality text.",
            "embedding": [0.1] * 384,
            "metadata": {
                "uuid": "test-uuid",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "content_quality" in result
        assert "embedding_quality" in result
        assert "metadata_quality" in result
        assert "overall_quality" in result
        assert "passes_quality_check" in result
    
    def test_check_chunk_quality_no_quality_checks(self, plugin):
        """Test chunk quality check with no quality checks enabled."""
        plugin.check_content_quality = False
        plugin.check_embedding_quality = False
        plugin.check_metadata_quality = False
        
        chunk_data = {"other_field": "value"}  # No text, embedding, or metadata
        result = plugin._check_chunk_quality(chunk_data)
        
        assert "overall_quality" in result
        assert result["overall_quality"] == 0.0
        assert result["passes_quality_check"] is False
    
    @pytest.mark.asyncio
    async def test_execute_single_chunk(self, plugin):
        """Test execute with single chunk."""
        data = {
            "chunk": {
                "text": "This is a good quality text.",
                "embedding": [0.1] * 384,
                "metadata": {
                    "uuid": "test-uuid",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            }
        }
        result = await plugin.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert result["quality_checked"] is True
        assert "filtered_out" not in result
    
    @pytest.mark.asyncio
    async def test_execute_single_chunk_filtered(self, plugin_with_config):
        """Test execute with single chunk that gets filtered."""
        plugin_with_config.quality_threshold = 0.9  # High threshold
        data = {
            "chunk": {
                "text": "Bad",  # Low quality text
                "embedding": [0.01] * 384,  # Low quality embedding
                "metadata": {"source": "test"}  # Missing required fields
            }
        }
        result = await plugin_with_config.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert "filtered_out" in result
        assert result["filtered_out"] is True
        assert result["chunk"] is None
    
    @pytest.mark.asyncio
    async def test_execute_multiple_chunks(self, plugin):
        """Test execute with multiple chunks."""
        chunks = [
            {
                "text": "Good quality text 1.",
                "embedding": [0.1] * 384,
                "metadata": {
                    "uuid": "uuid1",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            },
            {
                "text": "Good quality text 2.",
                "embedding": [0.2] * 384,
                "metadata": {
                    "uuid": "uuid2",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            }
        ]
        data = {"chunks": chunks}
        result = await plugin.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert result["quality_checked"] is True
        assert len(result["quality_results"]) == 2
        assert len(result["chunks"]) == 2
    
    @pytest.mark.asyncio
    async def test_execute_multiple_chunks_with_filtering(self, plugin_with_config):
        """Test execute with multiple chunks and filtering."""
        chunks = [
            {
                "text": "Good quality text.",
                "embedding": [0.1] * 384,
                "metadata": {
                    "uuid": "uuid1",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            },
            {
                "text": "Bad",  # Low quality
                "embedding": [0.01] * 384,  # Low quality
                "metadata": {"source": "test"}  # Missing required fields
            }
        ]
        data = {"chunks": chunks}
        result = await plugin_with_config.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert "original_chunk_count" in result
        assert "filtered_chunk_count" in result
        assert result["original_chunk_count"] == 2
        assert result["filtered_chunk_count"] == 1
        assert len(result["chunks"]) == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_semantic_chunk_objects(self, plugin):
        """Test execute with SemanticChunk objects."""
        # Create mock SemanticChunk objects
        chunk1 = MagicMock()
        chunk1.text = "Good quality text."
        chunk1.embedding = [0.1] * 384
        chunk1.metadata = {
            "uuid": "uuid1",
            "created_at": "2023-01-01T00:00:00Z"
        }
        chunk1.model_dump.return_value = {
            "text": "Good quality text.",
            "embedding": [0.1] * 384,
            "metadata": {
                "uuid": "uuid1",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        
        chunks = [chunk1]
        data = {"chunks": chunks}
        result = await plugin.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert len(result["quality_results"]) == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_semantic_chunk_objects_filtering(self, plugin_with_config):
        """Test execute with SemanticChunk objects and filtering."""
        # Create mock SemanticChunk object
        chunk = MagicMock()
        chunk.text = "Bad"  # Low quality
        chunk.embedding = [0.01] * 384  # Low quality
        chunk.metadata = {"source": "test"}  # Missing required fields
        chunk.model_dump.return_value = {
            "text": "Bad",
            "embedding": [0.01] * 384,
            "metadata": {"source": "test"}
        }
        
        chunks = [chunk]
        data = {"chunks": chunks}
        result = await plugin_with_config.execute(data)
        
        assert "quality_results" in result
        assert "quality_checked" in result
        assert "original_chunk_count" in result
        assert "filtered_chunk_count" in result
        assert result["original_chunk_count"] == 1
        assert result["filtered_chunk_count"] == 0
        assert len(result["chunks"]) == 0
    
    @pytest.mark.asyncio
    async def test_execute_no_data(self, plugin):
        """Test execute with no data."""
        data = {"other_field": "value"}
        result = await plugin.execute(data)
        
        assert result == data
    
    @pytest.mark.asyncio
    async def test_pre_execute_with_data(self, plugin):
        """Test pre_execute with data."""
        data = {"chunk": {"text": "test"}}
        result = await plugin.pre_execute(data)
        
        assert result == data
    
    @pytest.mark.asyncio
    async def test_pre_execute_without_data(self, plugin):
        """Test pre_execute without data."""
        data = {"other_field": "value"}
        result = await plugin.pre_execute(data)
        
        assert result == data
    
    @pytest.mark.asyncio
    async def test_post_execute_with_filtering(self, plugin):
        """Test post_execute with filtering results."""
        result = {
            "quality_checked": True,
            "original_chunk_count": 10,
            "filtered_chunk_count": 8
        }
        final_result = await plugin.post_execute(result)
        
        assert final_result == result
    
    @pytest.mark.asyncio
    async def test_post_execute_without_filtering(self, plugin):
        """Test post_execute without filtering results."""
        result = {"quality_checked": True}
        final_result = await plugin.post_execute(result)
        
        assert final_result == result
    
    @pytest.mark.asyncio
    async def test_post_execute_without_quality_check(self, plugin):
        """Test post_execute without quality check."""
        result = {"other_field": "value"}
        final_result = await plugin.post_execute(result)
        
        assert final_result == result
    
    def test_get_quality_stats(self, plugin):
        """Test get_quality_stats method."""
        stats = plugin.get_quality_stats()
        
        assert "plugin_name" in stats
        assert "version" in stats
        assert "config" in stats
        assert "description" in stats
        assert stats["plugin_name"] == "quality_checker"
        assert stats["version"] == "1.0.0"
        assert "quality_threshold" in stats["config"]
        assert "check_content" in stats["config"]
        assert "check_embedding" in stats["config"]
        assert "check_metadata" in stats["config"]
        assert "filter_low_quality" in stats["config"]
        assert "min_content_length" in stats["config"]
        assert "max_content_length" in stats["config"]
        assert "min_embedding_norm" in stats["config"]
        assert "expected_embedding_dim" in stats["config"]
    
    def test_plugin_with_client(self):
        """Test plugin creation with client."""
        client = MagicMock()
        plugin = QualityCheckerPlugin(client=client)
        
        assert plugin.client == client
    
    def test_plugin_with_none_config(self):
        """Test plugin creation with None config."""
        plugin = QualityCheckerPlugin(config=None)
        
        # Should use default config
        assert plugin.check_content_quality is True
        assert plugin.check_embedding_quality is True
        assert plugin.check_metadata_quality is True
        assert plugin.min_content_length == 10
        assert plugin.max_content_length == 10000
        assert plugin.min_embedding_norm == 0.1
        assert plugin.expected_embedding_dim == 384
        assert plugin.filter_low_quality is False
        assert plugin.quality_threshold == 0.5 