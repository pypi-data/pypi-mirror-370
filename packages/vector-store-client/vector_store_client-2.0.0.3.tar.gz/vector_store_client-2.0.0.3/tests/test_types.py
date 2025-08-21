"""
Tests for vector_store_client.types module.

This module tests all type definitions, enums, and constants
defined in the types module.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from typing import List, Dict, Any

from vector_store_client.types import (
    # Type aliases
    ChunkId, Vector, MetadataDict, SearchResult, JsonRpcId, JsonRpcResult,
    MetadataFilter, SearchParams,
    
    # Enums
    ChunkType, LanguageEnum, ChunkRole, ChunkStatus, BlockType, 
    SearchOrder, EmbeddingModel,
    
    # Constants
    MIN_CHUNK_SIZE, MAX_CHUNK_SIZE, MIN_SEARCH_LIMIT, MAX_SEARCH_LIMIT,
    MIN_RELEVANCE_THRESHOLD, MAX_RELEVANCE_THRESHOLD, MIN_OFFSET, MAX_OFFSET,
    MIN_TIMEOUT, MAX_TIMEOUT, EMBEDDING_DIMENSION, UUID_LENGTH, SHA256_LENGTH,
    
    # Default values
    DEFAULT_TIMEOUT, DEFAULT_LIMIT, DEFAULT_OFFSET, DEFAULT_RELEVANCE_THRESHOLD,
    DEFAULT_CHUNK_TYPE, DEFAULT_LANGUAGE, DEFAULT_STATUS, DEFAULT_SEARCH_ORDER,
    DEFAULT_EMBEDDING_MODEL,
    
    # JSON-RPC constants
    JSON_RPC_VERSION, DEFAULT_JSON_RPC_ID,
    
    # HTTP constants
    DEFAULT_HEADERS,
    
    # Retry constants
    DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY, DEFAULT_BACKOFF_FACTOR,
    
    # Batch processing constants
    DEFAULT_BATCH_SIZE, MAX_BATCH_SIZE, DEFAULT_CONCURRENT_REQUESTS,
    MAX_CONCURRENT_REQUESTS,
    
    # Logging constants
    DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT, DEFAULT_LOG_DATE_FORMAT,
    
    # Cache constants
    DEFAULT_CACHE_TTL, MAX_CACHE_TTL, DEFAULT_CACHE_SIZE, MAX_CACHE_SIZE
)


class TestTypeAliases:
    """Test type aliases."""
    
    def test_chunk_id_type(self):
        """Test ChunkId type alias."""
        chunk_id: ChunkId = "550e8400-e29b-41d4-a716-446655440001"
        assert isinstance(chunk_id, str)
        assert len(chunk_id) == 36
    
    def test_vector_type(self):
        """Test Vector type alias."""
        vector: Vector = [0.1, 0.2, 0.3]
        assert isinstance(vector, list)
        assert all(isinstance(x, float) for x in vector)
    
    def test_metadata_dict_type(self):
        """Test MetadataDict type alias."""
        metadata: MetadataDict = {"key": "value", "number": 42}
        assert isinstance(metadata, dict)
    
    def test_search_result_type(self):
        """Test SearchResult type alias."""
        result: SearchResult = ["item1", "item2"]
        assert isinstance(result, list)
    
    def test_json_rpc_id_type(self):
        """Test JsonRpcId type alias."""
        # String ID
        str_id: JsonRpcId = "request-1"
        assert isinstance(str_id, str)
        
        # Integer ID
        int_id: JsonRpcId = 1
        assert isinstance(int_id, int)
        
        # None ID
        none_id: JsonRpcId = None
        assert none_id is None
    
    def test_json_rpc_result_type(self):
        """Test JsonRpcResult type alias."""
        # Dict result
        dict_result: JsonRpcResult = {"key": "value"}
        assert isinstance(dict_result, dict)
        
        # List result
        list_result: JsonRpcResult = [1, 2, 3]
        assert isinstance(list_result, list)
        
        # String result
        str_result: JsonRpcResult = "success"
        assert isinstance(str_result, str)
        
        # Boolean result
        bool_result: JsonRpcResult = True
        assert isinstance(bool_result, bool)
        
        # None result
        none_result: JsonRpcResult = None
        assert none_result is None
    
    def test_metadata_filter_type(self):
        """Test MetadataFilter type alias."""
        filter_dict: MetadataFilter = {
            "type": "DOC_BLOCK",
            "language": "en",
            "tags": ["tag1", "tag2"]
        }
        assert isinstance(filter_dict, dict)
    
    def test_search_params_type(self):
        """Test SearchParams type alias."""
        params: SearchParams = {
            "search_str": "query",
            "limit": 10,
            "filter": {"type": "DOC_BLOCK"}
        }
        assert isinstance(params, dict)


class TestChunkType:
    """Test ChunkType enum."""
    
    def test_chunk_type_values(self):
        """Test all chunk type values."""
        assert ChunkType.DRAFT == "Draft"
        assert ChunkType.DOC_BLOCK == "DocBlock"
        assert ChunkType.CODE_BLOCK == "CodeBlock"
        assert ChunkType.MESSAGE == "Message"
        assert ChunkType.SECTION == "Section"
        assert ChunkType.OTHER == "Other"
    
    def test_get_default(self):
        """Test get_default method."""
        default = ChunkType.get_default()
        assert default == ChunkType.DOC_BLOCK
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert ChunkType.is_valid("Draft") is True
        assert ChunkType.is_valid("DocBlock") is True
        assert ChunkType.is_valid("CodeBlock") is True
        assert ChunkType.is_valid("Message") is True
        assert ChunkType.is_valid("Section") is True
        assert ChunkType.is_valid("Other") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert ChunkType.is_valid("invalid") is False
        assert ChunkType.is_valid("") is False
        assert ChunkType.is_valid(None) is False


class TestLanguageEnum:
    """Test LanguageEnum."""
    
    def test_language_values(self):
        """Test all language values."""
        assert LanguageEnum.UNKNOWN == "UNKNOWN"
        assert LanguageEnum.EN == "en"
        assert LanguageEnum.RU == "ru"
        assert LanguageEnum.DE == "de"
        assert LanguageEnum.FR == "fr"
        assert LanguageEnum.ES == "es"
        assert LanguageEnum.ZH == "zh"
        assert LanguageEnum.JA == "ja"
        assert LanguageEnum.MARKDOWN == "markdown"
        assert LanguageEnum.PYTHON == "python"
    
    def test_get_default(self):
        """Test get_default method."""
        default = LanguageEnum.get_default()
        assert default == LanguageEnum.EN
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert LanguageEnum.is_valid("en") is True
        assert LanguageEnum.is_valid("ru") is True
        assert LanguageEnum.is_valid("python") is True
        assert LanguageEnum.is_valid("UNKNOWN") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert LanguageEnum.is_valid("invalid") is False
        assert LanguageEnum.is_valid("") is False
        assert LanguageEnum.is_valid(None) is False


class TestChunkRole:
    """Test ChunkRole enum."""
    
    def test_role_values(self):
        """Test all role values."""
        assert ChunkRole.SYSTEM == "system"
        assert ChunkRole.USER == "user"
        assert ChunkRole.ASSISTANT == "assistant"
        assert ChunkRole.TOOL == "tool"
        assert ChunkRole.REVIEWER == "reviewer"
        assert ChunkRole.DEVELOPER == "developer"
    
    def test_get_default(self):
        """Test get_default method."""
        default = ChunkRole.get_default()
        assert default == ChunkRole.USER
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert ChunkRole.is_valid("system") is True
        assert ChunkRole.is_valid("user") is True
        assert ChunkRole.is_valid("assistant") is True
        assert ChunkRole.is_valid("tool") is True
        assert ChunkRole.is_valid("reviewer") is True
        assert ChunkRole.is_valid("developer") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert ChunkRole.is_valid("invalid") is False
        assert ChunkRole.is_valid("") is False
        assert ChunkRole.is_valid(None) is False


class TestChunkStatus:
    """Test ChunkStatus enum."""
    
    def test_status_values(self):
        """Test all status values."""
        assert ChunkStatus.NEW == "NEW"
        assert ChunkStatus.RAW == "RAW"
        assert ChunkStatus.CLEANED == "CLEANED"
        assert ChunkStatus.VERIFIED == "VERIFIED"
        assert ChunkStatus.VALIDATED == "VALIDATED"
        assert ChunkStatus.RELIABLE == "RELIABLE"
        assert ChunkStatus.INDEXED == "INDEXED"
        assert ChunkStatus.OBSOLETE == "OBSOLETE"
        assert ChunkStatus.REJECTED == "REJECTED"
        assert ChunkStatus.IN_PROGRESS == "IN_PROGRESS"
        assert ChunkStatus.NEEDS_REVIEW == "NEEDS_REVIEW"
        assert ChunkStatus.ARCHIVED == "ARCHIVED"
    
    def test_get_default(self):
        """Test get_default method."""
        default = ChunkStatus.get_default()
        assert default == ChunkStatus.NEW
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert ChunkStatus.is_valid("NEW") is True
        assert ChunkStatus.is_valid("INDEXED") is True
        assert ChunkStatus.is_valid("ARCHIVED") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert ChunkStatus.is_valid("invalid") is False
        assert ChunkStatus.is_valid("") is False
        assert ChunkStatus.is_valid(None) is False


class TestBlockType:
    """Test BlockType enum."""
    
    def test_block_type_values(self):
        """Test all block type values."""
        assert BlockType.PARAGRAPH == "paragraph"
        assert BlockType.MESSAGE == "message"
        assert BlockType.SECTION == "section"
        assert BlockType.OTHER == "other"
    
    def test_get_default(self):
        """Test get_default method."""
        default = BlockType.get_default()
        assert default == BlockType.PARAGRAPH
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert BlockType.is_valid("paragraph") is True
        assert BlockType.is_valid("message") is True
        assert BlockType.is_valid("section") is True
        assert BlockType.is_valid("other") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert BlockType.is_valid("invalid") is False
        assert BlockType.is_valid("") is False
        assert BlockType.is_valid(None) is False
    
    def test_get_all_values(self):
        """Test get_all_values method."""
        values = BlockType.get_all_values()
        expected = ["paragraph", "message", "section", "other"]
        assert values == expected


class TestSearchOrder:
    """Test SearchOrder enum."""
    
    def test_search_order_values(self):
        """Test all search order values."""
        assert SearchOrder.RELEVANCE == "relevance"
        assert SearchOrder.DATE_CREATED == "date_created"
        assert SearchOrder.DATE_UPDATED == "date_updated"
        assert SearchOrder.UUID == "uuid"
        assert SearchOrder.TYPE == "type"
        assert SearchOrder.LANGUAGE == "language"
    
    def test_get_default(self):
        """Test get_default method."""
        default = SearchOrder.get_default()
        assert default == SearchOrder.RELEVANCE
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert SearchOrder.is_valid("relevance") is True
        assert SearchOrder.is_valid("date_created") is True
        assert SearchOrder.is_valid("uuid") is True
        assert SearchOrder.is_valid("type") is True
        assert SearchOrder.is_valid("language") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert SearchOrder.is_valid("invalid") is False
        assert SearchOrder.is_valid("") is False
        assert SearchOrder.is_valid(None) is False


class TestEmbeddingModel:
    """Test EmbeddingModel enum."""
    
    def test_embedding_model_values(self):
        """Test all embedding model values."""
        assert EmbeddingModel.TEXT_EMBEDDING_ADA_002 == "text-embedding-ada-002"
        assert EmbeddingModel.TEXT_EMBEDDING_3_SMALL == "text-embedding-3-small"
        assert EmbeddingModel.TEXT_EMBEDDING_3_LARGE == "text-embedding-3-large"
        assert EmbeddingModel.ALL_MINILM_L6_V2 == "all-MiniLM-L6-v2"
        assert EmbeddingModel.ALL_MPNET_BASE_V2 == "all-mpnet-base-v2"
        assert EmbeddingModel.CUSTOM_384 == "custom_384"
        assert EmbeddingModel.CUSTOM_768 == "custom_768"
        assert EmbeddingModel.CUSTOM_1536 == "custom_1536"
    
    def test_get_default(self):
        """Test get_default method."""
        default = EmbeddingModel.get_default()
        assert default == EmbeddingModel.ALL_MINILM_L6_V2
    
    def test_get_dimensions(self):
        """Test get_dimensions method."""
        assert EmbeddingModel.get_dimensions(EmbeddingModel.TEXT_EMBEDDING_ADA_002) == 1536
        assert EmbeddingModel.get_dimensions(EmbeddingModel.TEXT_EMBEDDING_3_SMALL) == 1536
        assert EmbeddingModel.get_dimensions(EmbeddingModel.TEXT_EMBEDDING_3_LARGE) == 3072
        assert EmbeddingModel.get_dimensions(EmbeddingModel.ALL_MINILM_L6_V2) == 384
        assert EmbeddingModel.get_dimensions(EmbeddingModel.ALL_MPNET_BASE_V2) == 768
        assert EmbeddingModel.get_dimensions(EmbeddingModel.CUSTOM_384) == 384
        assert EmbeddingModel.get_dimensions(EmbeddingModel.CUSTOM_768) == 768
        assert EmbeddingModel.get_dimensions(EmbeddingModel.CUSTOM_1536) == 1536
        
        # Test with invalid model (should return default 384)
        assert EmbeddingModel.get_dimensions("invalid_model") == 384
    
    def test_is_valid_valid_values(self):
        """Test is_valid with valid values."""
        assert EmbeddingModel.is_valid("text-embedding-ada-002") is True
        assert EmbeddingModel.is_valid("all-MiniLM-L6-v2") is True
        assert EmbeddingModel.is_valid("custom_384") is True
    
    def test_is_valid_invalid_values(self):
        """Test is_valid with invalid values."""
        assert EmbeddingModel.is_valid("invalid") is False
        assert EmbeddingModel.is_valid("") is False
        assert EmbeddingModel.is_valid(None) is False


class TestConstants:
    """Test all constants."""
    
    def test_validation_constants(self):
        """Test validation constants."""
        assert MIN_CHUNK_SIZE == 1
        assert MAX_CHUNK_SIZE == 10000
        assert MIN_SEARCH_LIMIT == 1
        assert MAX_SEARCH_LIMIT == 1000
        assert MIN_RELEVANCE_THRESHOLD == 0.0
        assert MAX_RELEVANCE_THRESHOLD == 1.0
        assert MIN_OFFSET == 0
        assert MAX_OFFSET == 10000
        assert MIN_TIMEOUT == 1.0
        assert MAX_TIMEOUT == 300.0
        assert EMBEDDING_DIMENSION == 384
        assert UUID_LENGTH == 36
        assert SHA256_LENGTH == 64
    
    def test_default_values(self):
        """Test default values."""
        assert DEFAULT_TIMEOUT == 30.0
        assert DEFAULT_LIMIT == 10
        assert DEFAULT_OFFSET == 0
        assert DEFAULT_RELEVANCE_THRESHOLD == 0.0
        assert DEFAULT_CHUNK_TYPE == ChunkType.DOC_BLOCK
        assert DEFAULT_LANGUAGE == LanguageEnum.EN
        assert DEFAULT_STATUS == ChunkStatus.NEW
        assert DEFAULT_SEARCH_ORDER == SearchOrder.RELEVANCE
        assert DEFAULT_EMBEDDING_MODEL == EmbeddingModel.ALL_MINILM_L6_V2
    
    def test_json_rpc_constants(self):
        """Test JSON-RPC constants."""
        assert JSON_RPC_VERSION == "2.0"
        assert DEFAULT_JSON_RPC_ID == 1
    
    def test_http_constants(self):
        """Test HTTP constants."""
        assert DEFAULT_HEADERS == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_retry_constants(self):
        """Test retry constants."""
        assert DEFAULT_MAX_RETRIES == 3
        assert DEFAULT_RETRY_DELAY == 1.0
        assert DEFAULT_BACKOFF_FACTOR == 2.0
    
    def test_batch_processing_constants(self):
        """Test batch processing constants."""
        assert DEFAULT_BATCH_SIZE == 100
        assert MAX_BATCH_SIZE == 1000
        assert DEFAULT_CONCURRENT_REQUESTS == 5
        assert MAX_CONCURRENT_REQUESTS == 20
    
    def test_logging_constants(self):
        """Test logging constants."""
        assert DEFAULT_LOG_LEVEL == "INFO"
        assert DEFAULT_LOG_FORMAT == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert DEFAULT_LOG_DATE_FORMAT == "%Y-%m-%d %H:%M:%S"
    
    def test_cache_constants(self):
        """Test cache constants."""
        assert DEFAULT_CACHE_TTL == 300
        assert MAX_CACHE_TTL == 3600
        assert DEFAULT_CACHE_SIZE == 1000
        assert MAX_CACHE_SIZE == 10000 