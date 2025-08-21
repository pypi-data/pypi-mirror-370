"""
Extended tests for validation module.

This module contains comprehensive tests for validation functions
to achieve maximum code coverage.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from vector_store_client.validation import (
    validate_url, validate_timeout, validate_chunk_id, validate_embedding,
    validate_metadata, validate_search_params, validate_chunk_type,
    validate_language, validate_status, validate_search_order,
    validate_embedding_model, validate_uuid_list, validate_json_rpc_response,
    validate_health_response, validate_create_response, validate_source_id,
    validate_embedding_dimension, validate_chunk_metadata, validate_chunk_role,
    validate_block_type, validate_maintenance_params, validate_duplicate_cleanup_params,
    validate_ast_filter, validate_text_content, validate_tags
)
from vector_store_client.exceptions import ValidationError


class TestValidationExtended:
    """Extended tests for validation functions."""
    
    def test_validate_url_valid(self):
        """Test valid URL validation."""
        valid_urls = [
            "http://localhost:8007",
            "https://api.example.com",
            "http://127.0.0.1:8007",
            "https://vector-store.example.com/v1"
        ]
        
        for url in valid_urls:
            result = validate_url(url)
            assert result == url.rstrip('/')
    
    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "ftp://example.com",
            "http://",
            "https://"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                validate_url(url)
    
    def test_validate_timeout_valid(self):
        """Test valid timeout validation."""
        valid_timeouts = [1.0, 30.0, 60.0, 300.0]
        
        for timeout in valid_timeouts:
            result = validate_timeout(timeout)
            assert result == timeout
    
    def test_validate_timeout_invalid(self):
        """Test invalid timeout validation."""
        invalid_timeouts = [
            -1.0,
            0.0,
            "30",
            None,
            -30.0
        ]
        
        for timeout in invalid_timeouts:
            with pytest.raises(ValidationError):
                validate_timeout(timeout)
    
    def test_validate_chunk_id_valid(self):
        """Test valid chunk ID validation."""
        valid_ids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000"
        ]
        
        for chunk_id in valid_ids:
            result = validate_chunk_id(chunk_id)
            assert result == chunk_id
    
    def test_validate_chunk_id_invalid(self):
        """Test invalid chunk ID validation."""
        invalid_ids = [
            "",
            None,
            "not-a-uuid",
            "123e4567-e89b-12d3-a456-42661417400",  # Too short
            "123e4567-e89b-12d3-a456-4266141740000"  # Too long
        ]
        
        for chunk_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_chunk_id(chunk_id)
    
    def test_validate_embedding_valid(self):
        """Test valid embedding validation."""
        embedding = [0.1] * 384  # Correct dimension
        result = validate_embedding(embedding)
        assert result == embedding
    
    def test_validate_embedding_invalid(self):
        """Test invalid embedding validation."""
        invalid_embeddings = [
            [],
            None,
            "not-a-list",
            [0.1, 0.2],  # Wrong dimension
            [0.1, "not-a-number", 0.3],
            [0.1, float('inf'), 0.3],
            [0.1, float('nan'), 0.3]
        ]
        
        for embedding in invalid_embeddings:
            with pytest.raises(ValidationError):
                validate_embedding(embedding)
    
    def test_validate_metadata_valid(self):
        """Test valid metadata validation."""
        valid_metadata = [
            {},
            {"key": "value"},
            {"type": "doc", "language": "en", "source": "test"},
            {"nested": {"key": "value"}},
            {"list": [1, 2, 3], "number": 42, "boolean": True}
        ]
        
        for metadata in valid_metadata:
            result = validate_metadata(metadata)
            assert result == metadata
    
    def test_validate_metadata_invalid(self):
        """Test invalid metadata validation."""
        invalid_metadata = [
            {"": "value"},  # Empty key
            {123: "value"},  # Non-string key
            {"key": object()}  # Unsupported value type
        ]
        
        for metadata in invalid_metadata:
            with pytest.raises(ValidationError):
                validate_metadata(metadata)
    
    def test_validate_search_params_valid(self):
        """Test valid search parameters validation."""
        params = {
            "search_str": "test query",
            "limit": 10,
            "level_of_relevance": 0.5
        }
        result = validate_search_params(**params)
        assert result["search_str"] == "test query"
        assert result["limit"] == 10
        assert result["level_of_relevance"] == 0.5
    
    def test_validate_search_params_invalid(self):
        """Test invalid search parameters validation."""
        invalid_params = [
            {"limit": -1},
            {"offset": -1},
            {"level_of_relevance": 1.5},
            {"level_of_relevance": -0.1},
            {"limit": "not-a-number"}
        ]
        
        for params in invalid_params:
            with pytest.raises(ValidationError):
                validate_search_params(params)
    
    def test_validate_chunk_type_valid(self):
        """Test valid chunk type validation."""
        valid_types = [
            "Draft", "DocBlock", "CodeBlock", "Message", "Section", "Other"
        ]
        
        for chunk_type in valid_types:
            result = validate_chunk_type(chunk_type)
            assert result == chunk_type
    
    def test_validate_chunk_type_invalid(self):
        """Test invalid chunk type validation."""
        invalid_types = [
            "",
            None,
            "invalid",
            "doc_block"
        ]
        
        for chunk_type in invalid_types:
            with pytest.raises(ValidationError):
                validate_chunk_type(chunk_type)
    
    def test_validate_language_valid(self):
        """Test valid language validation."""
        valid_languages = [
            "en", "ru", "es", "fr", "de", "UNKNOWN"
        ]
        
        for language in valid_languages:
            result = validate_language(language)
            assert result == language
    
    def test_validate_language_invalid(self):
        """Test invalid language validation."""
        invalid_languages = [
            "",
            None,
            "invalid",
            "ENGLISH"
        ]
        
        for language in invalid_languages:
            with pytest.raises(ValidationError):
                validate_language(language)
    
    def test_validate_status_valid(self):
        """Test valid status validation."""
        valid_statuses = [
            "NEW", "RAW", "CLEANED", "VERIFIED", "VALIDATED", "RELIABLE", "INDEXED", "OBSOLETE", "REJECTED", "IN_PROGRESS", "NEEDS_REVIEW", "ARCHIVED"
        ]
        
        for status in valid_statuses:
            result = validate_status(status)
            assert result == status
    
    def test_validate_status_invalid(self):
        """Test invalid status validation."""
        invalid_statuses = [
            "",
            None,
            "invalid",
            "ACTIVE"
        ]
        
        for status in invalid_statuses:
            with pytest.raises(ValidationError):
                validate_status(status)
    
    def test_validate_search_order_valid(self):
        """Test valid search order validation."""
        valid_orders = [
            "relevance", "date_created", "date_updated", "uuid", "type", "language"
        ]
        
        for order in valid_orders:
            result = validate_search_order(order)
            assert result == order
    
    def test_validate_search_order_invalid(self):
        """Test invalid search order validation."""
        invalid_orders = [
            "",
            None,
            "invalid",
            "RELEVANCE"
        ]
        
        for order in invalid_orders:
            with pytest.raises(ValidationError):
                validate_search_order(order)
    
    def test_validate_embedding_model_valid(self):
        """Test valid embedding model validation."""
        valid_models = [
            "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large", "all-MiniLM-L6-v2", "all-mpnet-base-v2", "custom_384", "custom_768", "custom_1536"
        ]
        
        for model in valid_models:
            result = validate_embedding_model(model)
            assert result == model
    
    def test_validate_embedding_model_invalid(self):
        """Test invalid embedding model validation."""
        invalid_models = [
            "",
            None,
            "invalid model with spaces",
            "model@#$%"
        ]
        
        for model in invalid_models:
            with pytest.raises(ValidationError):
                validate_embedding_model(model)
    
    def test_validate_uuid_list_valid(self):
        """Test valid UUID list validation."""
        uuid_list = [
            "123e4567-e89b-12d3-a456-426614174000",
            "987fcdeb-51a2-43d1-b789-123456789abc"
        ]
        result = validate_uuid_list(uuid_list)
        assert result == uuid_list
    
    def test_validate_uuid_list_invalid(self):
        """Test invalid UUID list validation."""
        invalid_uuids = [
            [],
            None,
            "not-a-list",
            ["invalid-uuid"],
            [123, "uuid"]
        ]
        
        for uuid_list in invalid_uuids:
            with pytest.raises(ValidationError):
                validate_uuid_list(uuid_list)
    
    def test_validate_json_rpc_response_valid(self):
        """Test valid JSON-RPC response validation."""
        valid_responses = [
            {"jsonrpc": "2.0", "result": {"status": "success"}, "id": 1},
            {"jsonrpc": "2.0", "error": {"code": -1, "message": "Error"}, "id": 1}
        ]
        
        for response in valid_responses:
            result = validate_json_rpc_response(response)
            assert result == response
    
    def test_validate_json_rpc_response_invalid(self):
        """Test invalid JSON-RPC response validation."""
        invalid_responses = [
            {},
            {"result": "success"},
            {"jsonrpc": "1.0", "result": "success", "id": 1}
        ]
        
        for response in invalid_responses:
            with pytest.raises(ValidationError):
                validate_json_rpc_response(response)
    
    def test_validate_health_response_valid(self):
        """Test valid health response validation."""
        valid_responses = [
            {"status": "healthy"},
            {"status": "unhealthy", "error": "Service unavailable"}
        ]
        
        for response in valid_responses:
            result = validate_health_response(response)
            assert result == response
    
    def test_validate_health_response_invalid(self):
        """Test invalid health response validation."""
        invalid_responses = [
            {},
            {"status": "invalid"},
            {"health": "good"}
        ]
        
        for response in invalid_responses:
            with pytest.raises(ValidationError):
                validate_health_response(response)
    
    def test_validate_create_response_valid(self):
        """Test valid create response validation."""
        response = {
            "success": True,
            "uuids": [
                "123e4567-e89b-12d3-a456-426614174000",
                "987fcdeb-51a2-43d1-b789-123456789abc"
            ],
            "created_count": 2
        }
        result = validate_create_response(response)
        assert result == response
    
    def test_validate_create_response_invalid(self):
        """Test invalid create response validation."""
        invalid_response = {"uuids": ["invalid-uuid"]}
        with pytest.raises(ValidationError, match="UUID at index 0: Chunk ID must be a valid UUID format"):
            validate_create_response(invalid_response)
    
    def test_validate_source_id_valid(self):
        """Test valid source ID validation."""
        valid_source_ids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "987fcdeb-51a2-43d1-b789-123456789abc",
            "uuid-1",
            "uuid-123"
        ]
        
        for source_id in valid_source_ids:
            result = validate_source_id(source_id)
            assert result == source_id
    
    def test_validate_source_id_invalid(self):
        """Test invalid source ID validation."""
        invalid_source_ids = [
            "",
            None,
            "a" * 256  # Too long
        ]
        
        for source_id in invalid_source_ids:
            with pytest.raises(ValidationError):
                validate_source_id(source_id)
    
    def test_validate_embedding_dimension_valid(self):
        """Test valid embedding dimension validation."""
        valid_embeddings = [
            [0.1] * 384,
            [0.0] * 384,
            [-1.0, 0.5, 1.0] * 128  # 3 * 128 = 384
        ]
        
        for embedding in valid_embeddings:
            result = validate_embedding_dimension(embedding)
            assert result == embedding
    
    def test_validate_embedding_dimension_invalid(self):
        """Test invalid embedding dimension validation."""
        invalid_embeddings = [
            [],
            [0.1, 0.2],  # Wrong dimension
            [0.1] * 1000  # Too large
        ]
        
        for embedding in invalid_embeddings:
            with pytest.raises(ValidationError):
                validate_embedding_dimension(embedding)
    
    def test_validate_chunk_metadata_valid(self):
        """Test valid chunk metadata validation."""
        valid_metadata = [
            {"type": "doc", "language": "en"},
            {"source": "test", "category": "example"}
        ]
        
        for metadata in valid_metadata:
            result = validate_chunk_metadata(metadata)
            assert result == metadata
    
    def test_validate_chunk_metadata_invalid(self):
        """Test invalid chunk metadata validation."""
        invalid_metadata = [
            {"category": "a" * 65},  # Too long category
            {"year": -1},  # Invalid year
            {"year": 2101}  # Invalid year
        ]
        
        for metadata in invalid_metadata:
            with pytest.raises(ValidationError):
                validate_chunk_metadata(metadata)
    
    def test_validate_chunk_role_valid(self):
        """Test valid chunk role validation."""
        valid_roles = [
            "system", "user", "assistant", "tool", "reviewer", "developer"
        ]
        
        for role in valid_roles:
            result = validate_chunk_role(role)
            assert result == role
    
    def test_validate_chunk_role_invalid(self):
        """Test invalid chunk role validation."""
        invalid_roles = [
            None,
            "invalid",
            "CONTENT"
        ]
        
        for role in invalid_roles:
            with pytest.raises(ValidationError):
                validate_chunk_role(role)
    
    def test_validate_block_type_valid(self):
        """Test valid block type validation."""
        valid_types = [
            "paragraph", "message", "section", "other"
        ]
        
        for block_type in valid_types:
            result = validate_block_type(block_type)
            assert result == block_type
    
    def test_validate_block_type_invalid(self):
        """Test invalid block type validation."""
        invalid_types = [
            None,
            "invalid",
            "PARAGRAPH"
        ]
        
        for block_type in invalid_types:
            with pytest.raises(ValidationError):
                validate_block_type(block_type)
    
    def test_validate_maintenance_params_valid(self):
        """Test valid maintenance parameters validation."""
        valid_params = [
            {"operation": "cleanup", "force": True},
            {"operation": "reindex", "batch_size": 100}
        ]
        
        for params in valid_params:
            result = validate_maintenance_params(params)
            assert result == params
    
    def test_validate_maintenance_params_invalid(self):
        """Test invalid maintenance parameters validation."""
        invalid_params = [
            None,
            {"dry_run": "not_a_boolean"},
            {"metadata_filter": "not_a_dict"}
        ]
        
        for params in invalid_params:
            with pytest.raises(ValidationError):
                validate_maintenance_params(params)
    
    def test_validate_duplicate_cleanup_params_valid(self):
        """Test valid duplicate cleanup parameters validation."""
        # Test with metadata_filter
        params = {"strategy": "keep_latest", "dry_run": True}
        result = validate_duplicate_cleanup_params(metadata_filter=params, dry_run=True)
        assert result["dry_run"] is True
        assert "strategy" in result
        
        # Test without metadata_filter
        result = validate_duplicate_cleanup_params(dry_run=False)
        assert result["dry_run"] is False
    
    def test_validate_duplicate_cleanup_params_invalid(self):
        """Test invalid duplicate cleanup parameters validation."""
        # Test with invalid metadata_filter type
        with pytest.raises(ValidationError, match="metadata_filter must be a dictionary"):
            validate_duplicate_cleanup_params(metadata_filter="not_a_dict")
    
    def test_validate_ast_filter_valid(self):
        """Test valid AST filter validation."""
        valid_filters = [
            {"type": "equals", "field": "status", "value": "active"},
            {"type": "range", "field": "date", "min": "2024-01-01", "max": "2024-12-31"}
        ]
        
        for ast_filter in valid_filters:
            result = validate_ast_filter(ast_filter)
            assert result == ast_filter
    
    def test_validate_ast_filter_invalid(self):
        """Test invalid AST filter validation."""
        # Test with invalid operator
        invalid_filter = {"operator": "INVALID_OP"}
        with pytest.raises(ValidationError, match="Invalid AST operator"):
            validate_ast_filter(invalid_filter)
        
        # Test with invalid conditions type
        invalid_filter = {"conditions": "not_a_list"}
        with pytest.raises(ValidationError, match="AST conditions must be a list"):
            validate_ast_filter(invalid_filter)
    
    def test_validate_text_content_valid(self):
        """Test valid text content validation."""
        valid_texts = [
            "Simple text",
            "Text with numbers 123",
            "Text with special chars: !@#$%^&*()",
            "Text with unicode: привет мир",
            "a" * 10000  # Max length
        ]
        
        for text in valid_texts:
            result = validate_text_content(text)
            assert result == text
    
    def test_validate_text_content_invalid(self):
        """Test invalid text content validation."""
        invalid_texts = [
            "",
            None,
            "a" * 10001,  # Too long
            123,
            ["not", "a", "string"]
        ]
        
        for text in invalid_texts:
            with pytest.raises(ValidationError):
                validate_text_content(text)
    
    def test_validate_text_content_with_field_name(self):
        """Test text content validation with custom field name."""
        result = validate_text_content("test", "body")
        assert result == "test"
    
    def test_validate_tags_valid(self):
        """Test valid tags validation."""
        valid_tags = [
            None,
            [],
            ["tag1", "tag2"],
            ["python", "api", "documentation"]
        ]
        
        for tags in valid_tags:
            result = validate_tags(tags)
            assert result == tags
    
    def test_validate_tags_invalid(self):
        """Test invalid tags validation."""
        invalid_tags = [
            "not-a-list",
            123,
            [None, "tag"],
            ["", "tag"],
            ["tag", 123]
        ]
        
        for tags in invalid_tags:
            with pytest.raises(ValidationError):
                validate_tags(tags) 