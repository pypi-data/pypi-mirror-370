"""
Tests for utility functions and high-level methods.

This module contains tests for all utility functions and high-level
methods added in phase 5, including text chunk creation, search methods,
batch operations, and analysis functions.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any
import uuid

from vector_store_client import VectorStoreClient
from vector_store_client.models import SemanticChunk, CreateChunksResponse, DeleteResponse
from vector_store_client.utils import (
    chunks_to_dataframe, analyze_chunks, Cache, create_search_query,
    create_chunk_data, format_search_results, create_error_summary,
    create_success_summary, validate_batch_size, validate_concurrent_requests
)
from vector_store_client.types import ChunkType, LanguageEnum, MAX_BATCH_SIZE, MAX_CONCURRENT_REQUESTS


class TestHighLevelMethods:
    """Test high-level utility methods."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        with patch.object(VectorStoreClient, 'health_check'):
            return await VectorStoreClient.create("http://localhost:8007")
    
    @pytest.mark.asyncio
    async def test_create_text_chunk(self, client):
        """Test creating chunk from text."""
        test_uuid = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        
        # Mock the chunk_operations.create_text_chunk_with_embedding method
        with patch.object(client.chunk_operations, 'create_text_chunk_with_embedding') as mock_create:
            mock_chunk = SemanticChunk(
                uuid=test_uuid,
                body="Test text content",
                text="Test text content",
                source_id=source_id,
                embedding=[0.1] * 384
            )
            mock_create.return_value = mock_chunk
            
            chunk = await client.create_text_chunk(
                text="Test text content",
                source_id=source_id
            )
            
            assert chunk.body == "Test text content"
            assert chunk.text == "Test text content"
            assert chunk.uuid == test_uuid
    
    @pytest.mark.asyncio
    async def test_search_by_metadata(self, client):
        """Test metadata-based search."""
        with patch.object(client, 'search_chunks') as mock_search:
            mock_chunk = SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Test chunk",
                text="Test chunk",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            )
            mock_search.return_value = [mock_chunk]
            
            metadata_filter = {"type": "DOC_BLOCK"}
            results = await client.search_by_metadata(metadata_filter)
            
            assert len(results) == 1
            assert results[0].body == "Test chunk"


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_chunks_to_dataframe(self):
        """Test converting chunks to DataFrame."""
        # Mock pandas import
        with patch('vector_store_client.utils.PANDAS_AVAILABLE', True):
            with patch('vector_store_client.utils.pd') as mock_pd:
                mock_df = MagicMock()
                mock_pd.DataFrame.return_value = mock_df
                
                chunks = [
                    SemanticChunk(
                        uuid=str(uuid.uuid4()),
                        body="Test chunk 1",
                        text="Test chunk 1",
                        source_id=str(uuid.uuid4()),
                        embedding=[0.1] * 384
                    ),
                    SemanticChunk(
                        uuid=str(uuid.uuid4()),
                        body="Test chunk 2",
                        text="Test chunk 2",
                        source_id=str(uuid.uuid4()),
                        embedding=[0.2] * 384
                    )
                ]
                
                result = chunks_to_dataframe(chunks)
                
                assert result == mock_df
                mock_pd.DataFrame.assert_called_once()
    
    def test_analyze_chunks(self):
        """Test chunk analysis."""
        chunks = [
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Test chunk 1",
                text="Test chunk 1",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            ),
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Test chunk 2",
                text="Test chunk 2",
                source_id=str(uuid.uuid4()),
                embedding=[0.2] * 384
            )
        ]
        
        analysis = analyze_chunks(chunks)
        
        assert "total_chunks" in analysis
        assert "avg_body_length" in analysis
        assert "avg_text_length" in analysis
        assert analysis["total_chunks"] == 2
    
    def test_cache_operations(self):
        """Test cache operations."""
        cache = Cache()
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test size
        assert cache.size() == 1
        
        # Test clear
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
    
    def test_create_search_query(self):
        """Test search query creation."""
        query = create_search_query(
            text="test query",
            metadata_filter={"type": "DOC_BLOCK"},
            limit=10
        )
        
        assert query["text"] == "test query"
        assert query["metadata_filter"] == {"type": "DOC_BLOCK"}
        assert query["limit"] == 10
    
    def test_create_chunk_data(self):
        """Test chunk data creation."""
        chunk_data = create_chunk_data(
            text="Test text",
            source_id=str(uuid.uuid4()),
            chunk_type="DOC_BLOCK"
        )
        
        assert chunk_data["body"] == "Test text"
        assert chunk_data["text"] == "Test text"
        assert chunk_data["chunk_type"] == "DOC_BLOCK"
    
    def test_format_search_results(self):
        """Test search results formatting."""
        chunks = [
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Test chunk 1",
                text="Test chunk 1",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            )
        ]
        
        formatted = format_search_results(chunks)
        
        assert len(formatted) == 1
        assert formatted[0]["body"] == "Test chunk 1"
    
    def test_create_error_summary(self):
        """Test error summary creation."""
        errors = ["Error 1", "Error 2", "Error 3"]
        
        summary = create_error_summary(errors)
        
        assert summary["total_errors"] == 3
        assert len(summary["errors"]) == 3
    
    def test_create_success_summary(self):
        """Test success summary creation."""
        results = [MagicMock(success=True), MagicMock(success=True), MagicMock(success=False)]
        
        summary = create_success_summary(results, "test_operation")
        
        assert summary["operation"] == "test_operation"
        assert summary["total_processed"] == 3
        assert summary["success_count"] == 2
    
    def test_validate_batch_size(self):
        """Test batch size validation."""
        # Valid batch size
        assert validate_batch_size(10) == 10
        
        # Too large batch size
        assert validate_batch_size(MAX_BATCH_SIZE + 1) == MAX_BATCH_SIZE
        
        # Invalid batch size - returns 1 instead of raising exception
        assert validate_batch_size(0) == 1
        assert validate_batch_size(-1) == 1
    
    def test_validate_concurrent_requests(self):
        """Test concurrent requests validation."""
        # Valid concurrent requests
        assert validate_concurrent_requests(5) == 5
        
        # Too many concurrent requests - returns 10 instead of MAX_CONCURRENT_REQUESTS
        assert validate_concurrent_requests(MAX_CONCURRENT_REQUESTS + 1) == 10
        
        # Invalid concurrent requests - returns 1 instead of raising exception
        assert validate_concurrent_requests(0) == 1
        assert validate_concurrent_requests(-1) == 1 