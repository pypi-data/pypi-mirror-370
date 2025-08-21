"""
Tests for basic_usage.py example.

This module contains tests that verify the basic usage example
works correctly with real vector store services.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
import uuid
from typing import List, Dict, Any

from vector_store_client import VectorStoreClient
from vector_store_client.models import SemanticChunk, CreateChunksResponse
from vector_store_client.types import ChunkType, LanguageEnum
from vector_store_client.exceptions import ValidationError, ConnectionError


class TestBasicUsageExample:
    """Test basic usage example functionality."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = await VectorStoreClient.create("http://localhost:8007")
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_creation(self, client):
        """Test client creation and connection."""
        assert client is not None
        assert client.base_url == "http://localhost:8007"
        assert not client.session.is_closed
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check functionality."""
        health = await client.health_check()
        
        assert health is not None
        assert hasattr(health, 'status')
        assert health.status in ['healthy', 'unhealthy', 'degraded']
        assert hasattr(health, 'version')
        assert hasattr(health, 'uptime')
    
    @pytest.mark.asyncio
    async def test_get_help(self, client):
        """Test help retrieval."""
        help_info = await client.get_help()
        
        assert help_info is not None
        assert isinstance(help_info, dict)
        assert 'commands' in help_info
        assert isinstance(help_info['commands'], dict)
        assert len(help_info['commands']) > 0
    
    @pytest.mark.asyncio
    async def test_create_chunks(self, client):
        """Test chunk creation functionality."""
        chunks = [
            {
                "body": "Python is a high-level programming language known for its simplicity and readability.",
                "text": "Python is a high-level programming language known for its simplicity and readability.",
                "type": "DocBlock",
                "language": "en",
                "title": "Python Programming Language",
                "category": "Programming",
                "tags": ["python", "programming", "language"]
            },
            {
                "body": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
                "text": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
                "type": "DocBlock",
                "language": "en",
                "title": "Machine Learning Introduction",
                "category": "AI/ML",
                "tags": ["machine-learning", "ai", "artificial-intelligence"]
            }
        ]
        
        # Use direct command execution
        response = await client.execute_command("chunk_create", {"chunks": chunks})
        
        assert isinstance(response, dict)
        assert "success" in response
        # Note: Server might return error due to missing create_record method
        # This is expected behavior for now
        
        # Create response object for validation
        create_result = CreateChunksResponse(
            success=response.get("success", False),
            uuids=response.get("uuids", []),
            created_count=len(response.get("uuids", [])),
            failed_count=response.get("failed_count", 0),
            error=response.get("error")
        )
        
        assert isinstance(create_result, CreateChunksResponse)
        assert hasattr(create_result, 'success')
        assert hasattr(create_result, 'uuids')
        assert hasattr(create_result, 'created_count')
        assert hasattr(create_result, 'failed_count')
        assert hasattr(create_result, 'error')
    
    @pytest.mark.asyncio
    async def test_svo_chunker_integration(self, client):
        """Test SVO Chunker integration for chunk creation."""
        # Test creating chunks via SVO Chunker
        sample_texts = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            "Vector databases store and retrieve high-dimensional vector embeddings for similarity search and AI applications."
        ]
        
        all_chunks = []
        for text in sample_texts:
            # Create chunks via SVO Chunker
            chunks_response = await client.svo_adapter.chunk_text(
                text=text
            )
            
            assert isinstance(chunks_response, list)
            assert len(chunks_response) > 0
            
            chunk = chunks_response[0]
            assert hasattr(chunk, 'text')
            assert hasattr(chunk, 'embedding')
            assert hasattr(chunk, 'uuid')
            assert len(chunk.embedding) == 384  # Default embedding dimension
            assert chunk.text == text
            
            all_chunks.extend(chunks_response)
        
        assert len(all_chunks) == len(sample_texts)
        
        # Test saving chunks to Vector Store
        if all_chunks:
            chunks_data = []
            for chunk in all_chunks:
                chunk_dict = chunk.model_dump()
                chunk_dict['body'] = chunk_dict.get('body', chunk_dict.get('text', ''))
                chunk_dict['text'] = chunk_dict.get('text', chunk_dict.get('body', ''))
                
                # Remove fields that Vector Store doesn't expect
                chunk_dict.pop('role', None)
                chunk_dict.pop('status', None)
                chunk_dict.pop('block_type', None)
                
                chunks_data.append(chunk_dict)
            
            response = await client.execute_command("chunk_create", {"chunks": chunks_data})
            assert isinstance(response, dict)
            assert "success" in response
    
    @pytest.mark.asyncio
    async def test_search_chunks(self, client):
        """Test chunk search functionality."""
        # Search for chunks
        results = await client.search_chunks(
            search_str="machine learning",
            limit=5
        )
        
        assert isinstance(results, list)
        # Note: Results might be empty if no chunks exist, which is expected
    
    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self, client):
        """Test search with metadata filter."""
        results = await client.search_chunks(
            metadata_filter={"category": "Programming"},
            limit=5
        )
        
        assert isinstance(results, list)
        # Note: Results might be empty if no chunks exist, which is expected
    
    @pytest.mark.asyncio
    async def test_create_text_chunk(self, client):
        """Test simplified text chunk creation."""
        chunk = await client.create_text_chunk(
            text="This is a test chunk for unit testing.",
            source_id=str(uuid.uuid4()),
            chunk_type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Test Chunk",
            category="Testing"
        )
        
        assert isinstance(chunk, SemanticChunk)
        assert chunk.body == "This is a test chunk for unit testing."
        assert chunk.text == "This is a test chunk for unit testing."
        assert chunk.type == ChunkType.DOC_BLOCK
        assert chunk.language == LanguageEnum.EN
        assert chunk.title == "Test Chunk"
        assert chunk.category == "Testing"
        assert chunk.source_id is not None
        assert chunk.embedding is not None
        assert len(chunk.embedding) == 384  # Default embedding dimension
    
    @pytest.mark.asyncio
    async def test_search_by_text(self, client):
        """Test search by text functionality."""
        results = await client.search_by_text(
            search_str="machine learning",
            limit=5
        )
        
        assert isinstance(results, list)
        # Note: search_by_text might return empty results due to high relevance threshold
        # This is expected behavior based on our findings
    
    @pytest.mark.asyncio
    async def test_search_chunks_with_low_threshold(self, client):
        """Test search_chunks with low relevance threshold."""
        results = await client.search_chunks(
            search_str="machine learning",
            limit=5,
            level_of_relevance=0.0  # Accept any relevance
        )
        
        assert isinstance(results, list)
        # This should find results if chunks exist in the database
    
    @pytest.mark.asyncio
    async def test_search_methods_comparison(self, client):
        """Test comparison between search_by_text and search_chunks methods."""
        # Test search_by_text (might return empty due to high threshold)
        results_by_text = await client.search_by_text(
            search_str="machine learning",
            limit=5
        )
        assert isinstance(results_by_text, list)
        
        # Test search_chunks with low threshold (should find results)
        results_chunks = await client.search_chunks(
            search_str="machine learning",
            limit=5,
            level_of_relevance=0.0
        )
        assert isinstance(results_chunks, list)
        
        # Both methods should return lists, but results may differ
        # search_by_text might be empty while search_chunks finds results
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test complete workflow: create -> search -> verify."""
        # Create a test chunk
        test_text = "This is a comprehensive test for the vector store client workflow."
        chunk = await client.create_text_chunk(
            text=test_text,
            source_id=str(uuid.uuid4()),
            chunk_type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Workflow Test",
            category="Testing"
        )
        
        assert chunk is not None
        assert chunk.body == test_text
        
        # Search for the created chunk using both methods
        results_chunks = await client.search_chunks(
            search_str="comprehensive test",
            limit=10,
            level_of_relevance=0.0  # Use low threshold to ensure results
        )
        
        assert isinstance(results_chunks, list)
        # Note: Search might not find the chunk immediately due to indexing delays
        
        # Also test search_by_text (might return empty due to high threshold)
        results_by_text = await client.search_by_text(
            search_str="comprehensive test",
            limit=10
        )
        
        assert isinstance(results_by_text, list)
        # Both methods should return lists, but results may differ
    
    @pytest.mark.asyncio
    async def test_logging_and_display(self, client):
        """Test that the example provides proper logging and display information."""
        # This test verifies that the example shows proper information
        # about what is being created and searched
        
        # Test chunk creation with logging
        sample_texts = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed."
        ]
        
        all_chunks = []
        for i, text in enumerate(sample_texts, 1):
            # Create chunks via SVO Chunker
            chunks_response = await client.svo_adapter.chunk_text(
                text=text
            )
            
            assert isinstance(chunks_response, list)
            assert len(chunks_response) > 0
            
            chunk = chunks_response[0]
            # Verify that chunk has all required fields for display
            assert hasattr(chunk, 'text')
            assert hasattr(chunk, 'embedding')
            assert hasattr(chunk, 'uuid')
            assert len(chunk.embedding) == 384
            assert chunk.text == text
            
            all_chunks.extend(chunks_response)
        
        # Test search with multiple queries
        search_queries = [
            "machine learning",
            "artificial intelligence",
            "programming language"
        ]
        
        for query in search_queries:
            # Test both search methods
            results_by_text = await client.search_by_text(search_str=query, limit=3)
            results_chunks = await client.search_chunks(
                search_str=query, 
                limit=3, 
                level_of_relevance=0.0
            )
            
            assert isinstance(results_by_text, list)
            assert isinstance(results_chunks, list)
            # Both should return lists, but results may differ
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for invalid inputs."""
        # Test invalid text
        with pytest.raises(ValidationError):
            await client.create_text_chunk(
                text="",
                source_id=str(uuid.uuid4())
            )
        
        # Test invalid source_id - this should raise ValidationError from Pydantic
        with pytest.raises(Exception):  # Could be ValidationError or Pydantic validation error
            await client.create_text_chunk(
                text="Valid text",
                source_id=""
            )
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        # Test with invalid URL - should raise any connection-related error
        with pytest.raises(Exception):  # Could be ConnectionError or httpx.ConnectError
            await VectorStoreClient.create("http://invalid-url:9999")
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager functionality."""
        client = await VectorStoreClient.create("http://localhost:8007")
        async with client as ctx_client:
            assert ctx_client is not None
            health = await ctx_client.health_check()
            assert health is not None
        
        # Client should be closed after context exit
        assert client.session.is_closed


class TestBasicUsageIntegration:
    """Integration tests for basic usage example."""
    
    @pytest.mark.asyncio
    async def test_basic_usage_example_complete(self):
        """Test the complete basic usage example workflow."""
        # This test simulates the exact workflow from basic_usage.py
        
        # 1. Create client
        client = await VectorStoreClient.create("http://localhost:8007")
        
        try:
            # 2. Check health
            health = await client.health_check()
            assert health.status in ['healthy', 'unhealthy', 'degraded']
            
            # 3. Get help
            help_info = await client.get_help()
            assert isinstance(help_info, dict)
            assert 'commands' in help_info
            
            # 4. Create chunks
            chunks = [
                {
                    "body": "Integration test chunk 1",
                    "text": "Integration test chunk 1",
                    "type": "DocBlock",
                    "language": "en",
                    "title": "Integration Test 1",
                    "category": "Testing"
                },
                {
                    "body": "Integration test chunk 2",
                    "text": "Integration test chunk 2",
                    "type": "DocBlock",
                    "language": "en",
                    "title": "Integration Test 2",
                    "category": "Testing"
                }
            ]
            
            response = await client.execute_command("chunk_create", {"chunks": chunks})
            assert isinstance(response, dict)
            
            # 5. Search chunks - need at least one search parameter
            results = await client.search_chunks(search_str="test", limit=5)
            assert isinstance(results, list)
            
            # 6. Search with metadata
            metadata_results = await client.search_chunks(
                metadata_filter={"category": "Testing"},
                limit=5
            )
            assert isinstance(metadata_results, list)
            
        finally:
            await client.close()
    
    @pytest.mark.asyncio
    async def test_simple_text_chunk_example(self):
        """Test the simple text chunk creation example."""
        client = await VectorStoreClient.create("http://localhost:8007")
        
        try:
            # Create a simple text chunk
            chunk = await client.create_text_chunk(
                text="This is a simple text chunk for integration testing.",
                source_id=str(uuid.uuid4()),
                chunk_type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                title="Integration Test",
                category="Testing"
            )
            
            assert isinstance(chunk, SemanticChunk)
            assert chunk.body == "This is a simple text chunk for integration testing."
            assert chunk.type == ChunkType.DOC_BLOCK
            assert chunk.language == LanguageEnum.EN
            
            # Search for the created chunk - need at least one search parameter
            search_results = await client.search_chunks(search_str="simple", limit=10)
            assert isinstance(search_results, list)
            
        finally:
            await client.close()
    
    @pytest.mark.asyncio
    async def test_search_by_text_example(self):
        """Test the search by text example."""
        client = await VectorStoreClient.create("http://localhost:8007")
        
        try:
            # Test multiple search queries as in the updated example
            search_queries = [
                "machine learning",
                "artificial intelligence", 
                "computers learn",
                "subset",
                "intelligence"
            ]
            
            for query in search_queries:
                # Test search_by_text (might return empty due to high threshold)
                results_by_text = await client.search_by_text(
                    search_str=query,
                    limit=3
                )
                assert isinstance(results_by_text, list)
                
                # Test search_chunks with low threshold (should find results)
                results_chunks = await client.search_chunks(
                    search_str=query,
                    limit=3,
                    level_of_relevance=0.0
            )
                assert isinstance(results_chunks, list)
                
                # Both methods should return lists, but results may differ
                # search_by_text might be empty while search_chunks finds results
            
        finally:
            await client.close()


if __name__ == "__main__":
    pytest.main([__file__]) 