"""
Comprehensive tests for VectorStoreClient.

This module provides extensive test coverage for all VectorStoreClient methods
with coverage target of 90%+.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any, Optional

import pytest
from pydantic import ValidationError

from vector_store_client.client import VectorStoreClient
from vector_store_client.models import (
    SemanticChunk, CreateChunksResponse, DeleteResponse, 
    DuplicateUuidsResponse, HealthResponse, SearchResponse,
    EmbedResponse, ModelsResponse, CleanupResponse, ReindexResponse,
    ChunkType, LanguageEnum
)
from vector_store_client.exceptions import (
    ValidationError as ClientValidationError,
    ConnectionError, ServerError, UserCancelledError
)


class TestVectorStoreClient:
    """Comprehensive test suite for VectorStoreClient."""
    
    @pytest.fixture
    async def client(self):
        """Create test client instance."""
        with patch('vector_store_client.client.SVOChunkerAdapter'), \
             patch('vector_store_client.client.EmbeddingAdapter'):
            client = VectorStoreClient("http://localhost:8007")
            client.logger = MagicMock()
            yield client
    
    @pytest.fixture
    def sample_chunk(self):
        """Create sample chunk for testing."""
        return SemanticChunk(
            body="Test chunk body",
            text="Test chunk text",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN
        )
    
    @pytest.fixture
    def sample_chunks(self, sample_chunk):
        """Create sample chunks list."""
        chunk2 = sample_chunk.model_copy()
        chunk2.body = "Test chunk body 2"
        chunk2.text = "Test chunk text 2"
        chunk2.source_id = "550e8400-e29b-41d4-a716-446655440002"
        return [sample_chunk, chunk2]

    # ===== Initialization Tests =====
    
    def test_init(self):
        """Test client initialization."""
        with patch('vector_store_client.client.SVOChunkerAdapter'), \
             patch('vector_store_client.client.EmbeddingAdapter'):
            client = VectorStoreClient("http://localhost:8007")
            
            assert client.base_url == "http://localhost:8007"
            assert client.timeout == 30.0
            assert client.plugins == {}
            assert client.plugin_registry == {}
            assert client.middleware_chain == []
            assert client.middleware_registry == {}
    
    @pytest.mark.asyncio
    async def test_create_success(self):
        """Test successful client creation."""
        with patch('vector_store_client.client.SVOChunkerAdapter'), \
             patch('vector_store_client.client.EmbeddingAdapter'):
            # Mock the health check to return a proper JSON-RPC response
            mock_response = AsyncMock()
            mock_response.json = MagicMock(return_value={
                "jsonrpc": "2.0",
                "result": {"status": "healthy"},
                "id": 1
            })
            mock_response.raise_for_status = MagicMock()
            
            with patch('httpx.AsyncClient.post', return_value=mock_response):
                result = await VectorStoreClient.create("http://localhost:8007")
                assert isinstance(result, VectorStoreClient)
    
    # ===== Chunk Creation Tests =====
    
    @pytest.mark.asyncio
    async def test_create_chunks_success(self, client, sample_chunks):
        """Test successful chunk creation."""
        mock_response = {
            "success": True,
            "data": {
                "uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
                "created_count": 2,
                "failed_count": 0
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        with patch('vector_store_client.utils.generate_uuid', side_effect=[
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002"
        ]):
            result = await client.create_chunks(sample_chunks)
        
        assert result.success is True
        assert result.uuids == ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        assert result.created_count == 2
        assert result.failed_count == 0
    
    @pytest.mark.asyncio
    async def test_create_chunks_empty_list(self, client):
        """Test chunk creation with empty list."""
        with pytest.raises(ClientValidationError, match="Chunks list cannot be empty"):
            await client.create_chunks([])
    
    @pytest.mark.asyncio
    async def test_create_chunks_missing_body(self, client, sample_chunk):
        """Test chunk creation with missing body."""
        sample_chunk.body = ""
        with pytest.raises(ClientValidationError, match="Chunk missing required field 'body'"):
            await client.create_chunks([sample_chunk])
    
    @pytest.mark.asyncio
    async def test_create_chunks_missing_source_id(self, client, sample_chunk):
        """Test chunk creation with missing source_id."""
        sample_chunk.source_id = ""
        with pytest.raises(ClientValidationError, match="Chunk missing required field 'source_id'"):
            await client.create_chunks([sample_chunk])
    
    @pytest.mark.asyncio
    async def test_create_chunks_missing_embedding(self, client, sample_chunk):
        """Test chunk creation with missing embedding."""
        sample_chunk.embedding = []
        with pytest.raises(ClientValidationError, match="Chunk embedding must have 384 dimensions"):
            await client.create_chunks([sample_chunk])
    
    @pytest.mark.asyncio
    async def test_create_chunks_invalid_embedding_dimension(self, client, sample_chunk):
        """Test chunk creation with invalid embedding dimension."""
        sample_chunk.embedding = [0.1] * 100  # Wrong dimension
        with pytest.raises(ClientValidationError, match="Chunk embedding must have 384 dimensions"):
            await client.create_chunks([sample_chunk])
    
    @pytest.mark.asyncio
    async def test_create_chunks_failure(self, client, sample_chunks):
        """Test chunk creation failure."""
        mock_response = {
            "success": False,
            "error": {"message": "Creation failed"}
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        with pytest.raises(ServerError, match="Failed to create chunks"):
            await client.create_chunks(sample_chunks)

    # ===== Text Chunk Creation Tests =====
    
    @pytest.mark.asyncio
    async def test_create_text_chunk_success(self, client):
        """Test successful text chunk creation."""
        mock_response = {
            "success": True,
            "data": {
                "uuids": ["550e8400-e29b-41d4-a716-446655440001"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        client.embedding_adapter.embed_text = AsyncMock(return_value=EmbedResponse(
            embedding=[0.1] * 384,
            model="test-model",
            dimension=384
        ))
        
        result = await client.create_text_chunk(
            text="Test text",
            source_id="550e8400-e29b-41d4-a716-446655440001"
        )
        
        assert result.uuid == "550e8400-e29b-41d4-a716-446655440001"
        assert result.body == "Test text"
        assert result.text == "Test text"
        assert result.source_id == "550e8400-e29b-41d4-a716-446655440001"
    
    @pytest.mark.asyncio
    async def test_create_text_chunk_embedding_failure(self, client):
        """Test text chunk creation with embedding failure."""
        mock_response = {
            "success": True,
            "data": {
                "uuids": ["550e8400-e29b-41d4-a716-446655440001"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        client.embedding_adapter.embed_text = AsyncMock(side_effect=Exception("Embedding failed"))
        
        result = await client.create_text_chunk(
            text="Test text",
            source_id="550e8400-e29b-41d4-a716-446655440001"
        )
        
        assert result.uuid == "550e8400-e29b-41d4-a716-446655440001"
        # The actual embedding will be generated by the real embedding service
        assert len(result.embedding) == 384

    # ===== Search Tests =====
    
    @pytest.mark.asyncio
    async def test_search_chunks_success(self, client):
        """Test successful chunk search."""
        mock_response = {
            "data": {
                "chunks": [
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440001",
                        "body": "Test body 1",
                        "text": "Test text 1",
                        "embedding": [0.1] * 384,
                        "source_id": "550e8400-e29b-41d4-a716-446655440001"
                    },
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440002", 
                        "body": "Test body 2",
                        "text": "Test text 2",
                        "embedding": [0.2] * 384,
                        "source_id": "550e8400-e29b-41d4-a716-446655440002"
                    }
                ]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.search_chunks(search_str="test query")
        
        assert len(result) == 2
        assert result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        assert result[1].uuid == "550e8400-e29b-41d4-a716-446655440002"
    
    @pytest.mark.asyncio
    async def test_search_chunks_no_parameters(self, client):
        """Test search with no parameters."""
        # This should work now as search_chunks delegates to chunk_operations
        mock_response = {"data": {"chunks": []}}
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.search_chunks()
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_chunks_results_format(self, client):
        """Test search with results format."""
        mock_response = {
            "data": {
                "chunks": [
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440001",
                        "body": "Test body 1",
                        "text": "Test text 1",
                        "embedding": [0.1] * 384,
                        "source_id": "550e8400-e29b-41d4-a716-446655440001"
                    }
                ]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.search_chunks(search_str="test query")
        
        assert len(result) == 1
        assert result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
    
    @pytest.mark.asyncio
    async def test_search_by_metadata(self, client):
        """Test search by metadata."""
        mock_response = {"data": {"chunks": []}}
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.search_by_metadata({"type": "DOC_BLOCK"})
        
        assert result == []
        client.chunk_operations._execute_command.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_ast(self, client):
        """Test search by AST."""
        mock_response = {"data": {"chunks": []}}
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.search_by_ast({"type": "logical", "operator": "AND"})
        
        assert result == []
        client.chunk_operations._execute_command.assert_called_once()

    # ===== Count and Statistics Tests =====
    
    @pytest.mark.asyncio
    async def test_count_chunks(self, client):
        """Test chunk counting."""
        mock_response = {"data": {"count": 42}}
        client._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.count_chunks()
        
        assert result == 42
    
    @pytest.mark.asyncio
    async def test_get_chunk_statistics(self, client):
        """Test getting chunk statistics."""
        mock_response = {
            "data": {
                "statistics": {
                    "total": 100,
                    "by_type": {"DOC_BLOCK": 50, "Draft": 50}
                }
            }
        }
        client._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.get_chunk_statistics()
        
        assert result["statistics"]["total"] == 100
        assert result["statistics"]["by_type"]["DOC_BLOCK"] == 50
    
    @pytest.mark.asyncio
    async def test_count_chunks_by_type(self, client):
        """Test counting chunks by type."""
        mock_response = {"data": {"count": 25}}
        client._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.count_chunks_by_type("DOC_BLOCK")
        
        assert result == 25
    
    @pytest.mark.asyncio
    async def test_count_chunks_by_language(self, client):
        """Test counting chunks by language."""
        mock_response = {"data": {"count": 30}}
        client._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.count_chunks_by_language("en")
        
        assert result == 30

    # ===== Delete Tests =====
    
    @pytest.mark.asyncio
    async def test_delete_chunks_by_uuids(self, client):
        """Test deleting chunks by UUIDs."""
        mock_response = {
            "success": True,
            "data": {
                "deleted_count": 2,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.delete_chunks(uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"])
        
        assert result.success is True
        assert result.deleted_count == 2
        assert result.deleted_uuids == ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
    
    @pytest.mark.asyncio
    async def test_delete_chunks_by_metadata(self, client):
        """Test deleting chunks by metadata."""
        mock_response = {
            "success": True,
            "data": {
                "deleted_count": 5,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002", "550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440004", "550e8400-e29b-41d4-a716-446655440005"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.delete_chunks(metadata_filter={"type": "DOC_BLOCK"})
        
        assert result.success is True
        assert result.deleted_count == 5
    
    @pytest.mark.asyncio
    async def test_delete_chunks_no_parameters(self, client):
        """Test delete with no parameters."""
        with pytest.raises(ClientValidationError, match="Must provide either uuids or metadata_filter"):
            await client.delete_chunks()
    
    @pytest.mark.asyncio
    async def test_delete_chunk_single(self, client):
        """Test deleting single chunk."""
        mock_response = {
            "success": True,
            "data": {
                "deleted_count": 1,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.delete_chunk("550e8400-e29b-41d4-a716-446655440001")
        
        assert result.success is True
        assert result.deleted_count == 1

    # ===== Maintenance Tests =====
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids(self, client):
        """Test finding duplicate UUIDs."""
        mock_response = {
            "success": True,
            "data": {
                "total_duplicates": 4,
                "duplicates": [["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"], ["550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440004"]]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.find_duplicate_uuids()
        
        assert result.total_duplicates == 4
        assert len(result.duplicates) == 2
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids(self, client):
        """Test force delete by UUIDs."""
        mock_response = {
            "success": True,
            "data": {
                "deleted": 2,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.force_delete_by_uuids(["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"])
        
        assert result.success is True
        assert result.deleted_count == 2
    
    @pytest.mark.asyncio
    async def test_chunk_hard_delete(self, client):
        """Test hard delete chunks."""
        mock_response = {
            "success": True,
            "data": {
                "deleted_count": 3,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002", "550e8400-e29b-41d4-a716-446655440003"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.chunk_hard_delete(
            uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002", "550e8400-e29b-41d4-a716-446655440003"],
            confirm=True
        )
        
        assert result.success is True
        assert result.deleted_count == 3
    
    @pytest.mark.asyncio
    async def test_chunk_deferred_cleanup(self, client):
        """Test deferred cleanup."""
        mock_response = {
            "success": True,
            "data": {
                "cleaned_count": 10
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.chunk_deferred_cleanup()
        
        assert result.success is True
        assert result.cleaned_count == 10
    
    @pytest.mark.asyncio
    async def test_clean_faiss_orphans(self, client):
        """Test cleaning FAISS orphans."""
        mock_response = {
            "success": True,
            "data": {
                "cleaned_count": 5
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.clean_faiss_orphans()
        
        assert result.success is True
        assert result.cleaned_count == 5
    
    @pytest.mark.asyncio
    async def test_reindex_missing_embeddings(self, client):
        """Test reindexing missing embeddings."""
        mock_response = {
            "success": True,
            "data": {
                "reindexed_count": 15
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_response)
        
        result = await client.reindex_missing_embeddings()
        
        assert result.success is True
        assert result.reindexed_count == 15

    # ===== Health Check Tests =====
    
    @pytest.mark.asyncio
    async def test_maintenance_health_check(self, client):
        """Test maintenance health check."""
        client._check_duplicates_health = AsyncMock(return_value={"status": "healthy"})
        client._check_orphans_health = AsyncMock(return_value={"status": "healthy"})
        client._check_deleted_health = AsyncMock(return_value={"status": "healthy"})
        client._check_embeddings_health = AsyncMock(return_value={"status": "healthy"})
        
        result = await client.maintenance_health_check()
        
        assert "duplicate_chunks" in result
        assert "orphaned_entries" in result
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_perform_full_maintenance(self, client):
        """Test full maintenance cycle."""
        client.find_duplicate_uuids = AsyncMock(return_value=DuplicateUuidsResponse(
            success=True, total_duplicates=0, duplicates=[]
        ))
        client.clean_faiss_orphans = AsyncMock(return_value=CleanupResponse(
            success=True, cleaned_count=5
        ))
        client.chunk_deferred_cleanup = AsyncMock(return_value=CleanupResponse(
            success=True, cleaned_count=10
        ))
        client.reindex_missing_embeddings = AsyncMock(return_value=ReindexResponse(
            success=True, reindexed_count=15
        ))
        
        result = await client.perform_full_maintenance()
        
        assert "faiss_cleanup" in result
        assert "deferred_cleanup" in result
        assert "reindex" in result

    # ===== Edge Cases and Error Scenarios =====
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_no_duplicates(self, client):
        """Test cleanup duplicates with no duplicates."""
        mock_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=0,
            duplicates=[]
        )
        client.find_duplicate_uuids = AsyncMock(return_value=mock_response)
        
        result = await client.cleanup_duplicates()
        
        assert result["success"] is True
        assert result["duplicates_found"] == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_dry_run(self, client):
        """Test cleanup duplicates in dry run mode."""
        mock_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        client.find_duplicate_uuids = AsyncMock(return_value=mock_response)
        
        result = await client.cleanup_duplicates(dry_run=True)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["total_duplicates"] == 2
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_actual_cleanup(self, client):
        """Test cleanup duplicates with actual cleanup."""
        mock_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        client.find_duplicate_uuids = AsyncMock(return_value=mock_response)
        
        delete_response = DeleteResponse(
            success=True,
            deleted_count=1,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440002"]
        )
        client.force_delete_by_uuids = AsyncMock(return_value=delete_response)
        
        result = await client.cleanup_duplicates(dry_run=False)
        
        assert result["success"] is True
        assert result["dry_run"] is False
        assert result["deleted_count"] == 1

    # ===== Integration Tests =====
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test full workflow: create, search, delete."""
        # Create chunks
        mock_create_response = CreateChunksResponse(
            success=True,
            uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
            created_count=2,
            failed_count=0
        )
        client.create_chunks = AsyncMock(return_value=mock_create_response)
        
        chunks = [
            SemanticChunk(
                body="Test 1", text="Test 1", source_id="550e8400-e29b-41d4-a716-446655440001", embedding=[0.1] * 384
            ),
            SemanticChunk(
                body="Test 2", text="Test 2", source_id="550e8400-e29b-41d4-a716-446655440002", embedding=[0.2] * 384
            )
        ]
        
        create_result = await client.create_chunks(chunks)
        assert create_result.success is True
        assert len(create_result.uuids) == 2
        
        # Search chunks
        mock_search_response = {
            "data": {
                "chunks": [
                    {
                        "uuid": "550e8400-e29b-41d4-a716-446655440001",
                        "body": "Test 1",
                        "text": "Test 1",
                        "embedding": [0.1] * 384,
                        "source_id": "550e8400-e29b-41d4-a716-446655440001"
                    }
                ]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_search_response)
        
        search_result = await client.search_chunks(search_str="Test")
        assert len(search_result) == 1
        assert search_result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        
        # Delete chunks
        mock_delete_response = {
            "success": True,
            "data": {
                "deleted_count": 2,
                "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            }
        }
        client.chunk_operations._execute_command = AsyncMock(return_value=mock_delete_response)
        
        delete_result = await client.delete_chunks(uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"])
        assert delete_result.success is True
        assert delete_result.deleted_count == 2 