"""
Tests for Vector Store Client.

This module contains unit tests for the main VectorStoreClient class
and its methods.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any
import uuid
from pydantic import ValidationError as PydanticValidationError

from vector_store_client import VectorStoreClient
from vector_store_client.models import (
    SemanticChunk,
    SearchResult,
    CreateChunksResponse,
    HealthResponse,
    HelpResponse,
    ConfigResponse,
    DeleteResponse,
    DuplicateUuidsResponse,
    CleanupResponse,
    ReindexResponse,
    ModelsResponse,
)
from vector_store_client.types import ChunkType, LanguageEnum, ChunkStatus
from vector_store_client.exceptions import (
    VectorStoreError,
    ConnectionError,
    ValidationError,
    ServerError,
    JsonRpcError,
)


def create_mock_response(response_data: Dict[str, Any]) -> AsyncMock:
    """Create a properly configured mock response."""
    mock_response = AsyncMock()
    mock_response.json = MagicMock(return_value=response_data)
    mock_response.raise_for_status = MagicMock()
    return mock_response


class TestVectorStoreClient:
    """Test cases for VectorStoreClient class."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock HTTP session."""
        session = AsyncMock()
        session.is_closed = False
        return session
    
    @pytest.fixture
    def client(self, mock_session):
        """Create a VectorStoreClient instance with mocked session."""
        with patch('httpx.AsyncClient', return_value=mock_session):
            return VectorStoreClient("http://localhost:8007", session=mock_session)
    
    @pytest.fixture
    def sample_chunk(self):
        """Create a sample SemanticChunk for testing."""
        return SemanticChunk(
            body="Test content",
            text="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
    
    @pytest.fixture
    def sample_chunks(self, sample_chunk):
        """Create a list of sample chunks."""
        return [sample_chunk]
    
    @pytest.mark.asyncio
    async def test_client_creation(self, mock_session):
        """Test client creation with factory method."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "uptime": 3600.0
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_session):
            client = await VectorStoreClient.create("http://localhost:8007")
            assert client.base_url == "http://localhost:8007"
            assert client.timeout == 30.0
            await client.close()
    
    @pytest.mark.asyncio
    async def test_client_creation_connection_error(self, mock_session):
        """Test client creation with connection error."""
        mock_session.post.side_effect = Exception("Connection failed")
        
        with patch('httpx.AsyncClient', return_value=mock_session):
            with pytest.raises(Exception):
                await VectorStoreClient.create("http://localhost:8007")
    
    @pytest.mark.asyncio
    async def test_health_check(self, client, mock_session):
        """Test health check."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "uptime": 360.0
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        health = await client.health_check()
        assert isinstance(health, HealthResponse)
        assert health.status == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_help(self, client, mock_session):
        """Test get help."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "commands": ["chunk_create", "search", "delete"]
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        # Call the method directly since it's inherited from BaseVectorStoreClient
        help_info = await client._execute_command("help")
        assert isinstance(help_info, dict)
        assert "commands" in help_info
    
    @pytest.mark.asyncio
    async def test_get_config(self, client, mock_session):
        """Test get config."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "config": {"timeout": 30.0}
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        config = await client.get_config()
        assert isinstance(config, dict)
        assert "config" in config
    
    @pytest.mark.asyncio
    async def test_set_config(self, client, mock_session):
        """Test set config."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "message": "Config updated"
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.set_config("timeout", 60.0)
        assert isinstance(result, dict)
        assert result.get("success") is True
    
    @pytest.mark.asyncio
    async def test_create_chunks(self, client, mock_session, sample_chunks):
        """Test create chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "uuids": ["550e8400-e29b-41d4-a716-446655440001"],
                    "created_count": 1,
                    "failed_count": 0
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.create_chunks(sample_chunks)
        assert isinstance(result, CreateChunksResponse)
        assert result.success is True
        assert len(result.uuids) == 1
    
    @pytest.mark.asyncio
    async def test_create_chunks_empty_list(self, client):
        """Test create chunks with empty list."""
        with pytest.raises(ValidationError):
            await client.create_chunks([])
    
    @pytest.mark.asyncio
    async def test_search_chunks(self, client, mock_session):
        """Test search chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.search_chunks(search_str="test query")
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], SemanticChunk)
    
    @pytest.mark.asyncio
    async def test_delete_chunks(self, client, mock_session):
        """Test delete chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "deleted_count": 1
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.delete_chunks(uuids=["550e8400-e29b-41d4-a716-446655440001"])
        assert isinstance(result, DeleteResponse)
        assert result.success is True
        assert result.deleted_count == 1
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids(self, client, mock_session):
        """Test find duplicate UUIDs."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "total_duplicates": 1,
                    "duplicates": [["uuid1", "uuid2"]]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.find_duplicate_uuids()
        assert isinstance(result, DuplicateUuidsResponse)
        assert result.success is True
        assert result.total_duplicates == 1
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids(self, client, mock_session):
        """Test force delete by UUIDs."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "deleted": 1,
                    "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440001"]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.force_delete_by_uuids(["550e8400-e29b-41d4-a716-446655440001"])
        assert isinstance(result, DeleteResponse)
        assert result.success is True
        assert result.deleted_count == 1
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids_invalid_input(self, client):
        """Test force delete by UUIDs with invalid input."""
        with pytest.raises(ValidationError):
            await client.force_delete_by_uuids([])
    
    @pytest.mark.asyncio
    async def test_search_by_text(self, client, mock_session):
        """Test search by text."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.search_by_text("test query")
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], SemanticChunk)
    
    @pytest.mark.asyncio
    async def test_search_by_text_empty_query(self, client, mock_session):
        """Test search by text with empty query."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": []
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.search_by_text("")
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_by_metadata(self, client, mock_session):
        """Test search by metadata."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.search_by_metadata({"type": "DocBlock"})
        assert isinstance(results, list)
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_search_by_ast(self, client, mock_session):
        """Test search by AST."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        ast_filter = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "eq", "value": "DocBlock"}
            ]
        }
        
        results = await client.search_by_ast(ast_filter)
        assert isinstance(results, list)
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_search_by_vector(self, client, mock_session):
        """Test search by vector."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384,
                            "metadata": {}
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.search_by_vector([0.1] * 384)
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], SemanticChunk)
    
    @pytest.mark.asyncio
    async def test_search_by_vector_invalid_vector(self, client):
        """Test search by vector with invalid vector raises ValidationError."""
        with pytest.raises(ValidationError):
            await client.search_by_vector([0.1] * 10)  # wrong length
    
    @pytest.mark.asyncio
    async def test_count_chunks(self, client, mock_session):
        """Test count chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {"count": 10}
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        count = await client.count_chunks()
        assert isinstance(count, int)
        assert count == 10
    
    @pytest.mark.asyncio
    async def test_get_chunk_statistics(self, client, mock_session):
        """Test get chunk statistics."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "total_chunks": 100,
                    "by_type": {"DocBlock": 50},
                    "by_language": {"en": 80}
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        stats = await client.get_chunk_statistics()
        assert isinstance(stats, dict)
        assert "total_chunks" in stats
        assert stats["total_chunks"] == 100
    
    @pytest.mark.asyncio
    async def test_count_chunks_by_type(self, client, mock_session):
        """Test count chunks by type."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {"count": 50}
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        counts = await client.count_chunks_by_type("DocBlock")
        assert isinstance(counts, int)
        assert counts == 50
    
    @pytest.mark.asyncio
    async def test_count_chunks_by_language(self, client, mock_session):
        """Test count chunks by language."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {"count": 80}
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        counts = await client.count_chunks_by_language("en")
        assert isinstance(counts, int)
        assert counts == 80
    
    @pytest.mark.asyncio
    async def test_delete_chunk(self, client, mock_session):
        """Test delete single chunk."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {"success": True, "deleted_count": 1},
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.delete_chunk("550e8400-e29b-41d4-a716-446655440001")
        assert isinstance(result, DeleteResponse)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_chunk_hard_delete(self, client, mock_session):
        """Test chunk hard delete."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {"success": True, "deleted_count": 1},
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.chunk_hard_delete(
            uuids=["550e8400-e29b-41d4-a716-446655440001"],
            confirm=True
        )
        assert isinstance(result, DeleteResponse)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_chunk_deferred_cleanup(self, client, mock_session):
        """Test chunk deferred cleanup."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "cleaned_count": 3,
                "total_processed": 3,
                "dry_run": False,
                "error": None
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.chunk_deferred_cleanup()
        assert isinstance(result, CleanupResponse)
        assert result.success is True
        assert result.cleaned_count == 0
    
    @pytest.mark.asyncio
    async def test_clean_faiss_orphans(self, client, mock_session):
        """Test clean FAISS orphans."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "cleaned_count": 0,
                "total_processed": 0,
                "dry_run": None,
                "error": None
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.clean_faiss_orphans()
        assert isinstance(result, CleanupResponse)
        assert result.success is True
        assert result.cleaned_count == 0
    
    @pytest.mark.asyncio
    async def test_reindex_missing_embeddings(self, client, mock_session):
        """Test reindex missing embeddings."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "reindexed_count": 0,
                "total_count": 0,
                "error": None
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.reindex_missing_embeddings()
        assert isinstance(result, ReindexResponse)
        assert result.success is True
        assert result.reindexed_count == 0
    
    @pytest.mark.asyncio
    async def test_maintenance_health_check(self, client, mock_session):
        """Test maintenance health check."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "status": "healthy",
                "maintenance_required": False,
                "orphaned_entries": 0,
                "duplicate_chunks": 0
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        health = await client.maintenance_health_check()
        assert isinstance(health, dict)
        assert health["status"] == "healthy"
        assert "maintenance_required" in health
    
    @pytest.mark.asyncio
    async def test_perform_full_maintenance(self, client, mock_session):
        """Test perform full maintenance."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "faiss_cleanup": 0,
                "reindex": 0,
                "deferred_cleanup": 0
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.perform_full_maintenance()
        assert isinstance(result, dict)
        assert "faiss_cleanup" in result
        assert "reindex" in result
        assert "deferred_cleanup" in result
    
    @pytest.mark.asyncio
    async def test_create_chunk_with_full_metadata(self, client, mock_session):
        """Test create chunk with full metadata."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "uuids": ["550e8400-e29b-41d4-a716-446655440001"]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        with patch.object(client.embedding_adapter, 'embed_text') as mock_embed:
            mock_embed.return_value = MagicMock(embedding=[0.1] * 384)
            
            chunk = await client.create_chunk_with_full_metadata(
                "Test text",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            )
            assert isinstance(chunk, SemanticChunk)
            assert chunk.body == "Test text"
            assert chunk.text == "Test text"
    
    @pytest.mark.asyncio
    async def test_create_chunks_with_full_metadata(self, client, mock_session):
        """Test create chunks with full metadata."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "uuids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        chunks_data = [
            {
                "text": "Test text 1",
                "body": "Test body 1",
                "source_id": "550e8400-e29b-41d4-a716-446655440001",
                "embedding": [0.1] * 384
            },
            {
                "text": "Test text 2",
                "body": "Test body 2",
                "source_id": "550e8400-e29b-41d4-a716-446655440002",
                "embedding": [0.1] * 384
            }
        ]
        
        chunks = await client.create_chunks_with_full_metadata(chunks_data)
        assert isinstance(chunks, list)
        assert len(chunks) == 2
        assert isinstance(chunks[0], SemanticChunk)
    
    @pytest.mark.asyncio
    async def test_export_chunks(self, client, mock_session):
        """Test export chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        export_data = await client.export_chunks(metadata_filter={"type": "DocBlock"})
        assert isinstance(export_data, str)
        # Check for JSON structure instead of "chunks" string
        assert "Test content" in export_data
        assert "550e8400-e29b-41d4-a716-446655440001" in export_data
    
    @pytest.mark.asyncio
    async def test_import_chunks(self, client, mock_session):
        """Test import chunks."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "uuids": ["550e8400-e29b-41d4-a716-446655440001"]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        # Используем валидный JSON для embedding
        embedding_str = ",".join(["0.1"] * 384)
        json_data = '[{"body": "Test", "text": "Test", "source_id": "550e8400-e29b-41d4-a716-446655440001", "embedding": [%s]}]' % embedding_str
        result = await client.import_chunks(json_data)
        assert isinstance(result, CreateChunksResponse)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_export_chunks_to_file(self, client, mock_session):
        """Test export chunks to file."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "data": {
                    "chunks": [
                        {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "body": "Test content",
                            "text": "Test content",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.write = MagicMock()
            await client.export_chunks_to_file("test.json", metadata_filter={"type": "DocBlock"})
            mock_open.assert_called_once_with("test.json", "w")
    
    @pytest.mark.asyncio
    async def test_import_chunks_from_file(self, client, mock_session):
        """Test import chunks from file."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "uuids": ["550e8400-e29b-41d4-a716-446655440001"]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        with patch('builtins.open', create=True) as mock_open:
            embedding_str = ",".join(["0.1"] * 384)
            mock_open.return_value.__enter__.return_value.read.return_value = '[{"body": "Test", "text": "Test", "source_id": "550e8400-e29b-41d4-a716-446655440001", "embedding": [%s]}]' % embedding_str
            result = await client.import_chunks_from_file("test.json")
            assert isinstance(result, CreateChunksResponse)
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_embed_text(self, client, mock_session):
        """Test embed text."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "embeddings": [[0.1] * 384]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.embed_text("Test text")
        # Check for EmbedResponse object instead of dict
        assert hasattr(result, 'embedding')
        assert len(result.embedding) == 384
    
    @pytest.mark.asyncio
    async def test_embed_batch(self, client, mock_session):
        """Test embed batch."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "embeddings": [[0.1] * 384, [0.2] * 384]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        results = await client.embed_batch(["Text 1", "Text 2"])
        assert isinstance(results, list)
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_get_embedding_models(self, client, mock_session):
        """Test get embedding models."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "models": [
                        {
                            "name": "all-MiniLM-L6-v2",
                            "dimension": 384,
                            "description": "Multilingual model for text embeddings",
                            "max_tokens": 512,
                            "supported_dimensions": [384]
                        },
                        {
                            "name": "all-mpnet-base-v2",
                            "dimension": 768,
                            "description": "Multilingual model for text embeddings",
                            "max_tokens": 512,
                            "supported_dimensions": [768]
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        result = await client.get_embedding_models()
        assert isinstance(result, ModelsResponse)
        assert "all-MiniLM-L6-v2" in result.models
        assert "all-mpnet-base-v2" in result.models
        assert result.default_model == "default"
    
    @pytest.mark.asyncio
    async def test_chunk_text(self, client, mock_session):
        """Test chunk text."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "data": {
                    "chunks": [
                        {
                            "body": "Chunk 1",
                            "text": "Chunk 1",
                            "source_id": "550e8400-e29b-41d4-a716-446655440001",
                            "embedding": [0.1] * 384
                        }
                    ]
                }
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        chunks = await client.chunk_text("Test text to chunk")
        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert isinstance(chunks[0], SemanticChunk)
    
    @pytest.mark.asyncio
    async def test_client_close(self, client, mock_session):
        """Test client close."""
        await client.close()
        mock_session.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_session):
        """Test client as context manager."""
        with patch('httpx.AsyncClient', return_value=mock_session):
            async with VectorStoreClient("http://localhost:8007") as client:
                assert client.base_url == "http://localhost:8007"
            mock_session.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_json_rpc_error_handling(self, client, mock_session):
        """Test JSON-RPC error handling."""
        response_data = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found"
            },
            "id": 1
        }
        mock_response = create_mock_response(response_data)
        mock_session.post.return_value = mock_response
        
        with pytest.raises(JsonRpcError):
            await client.health_check()
    
    @pytest.mark.asyncio
    async def test_server_error_handling(self, client, mock_session):
        """Test server error handling."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_session.post.return_value = mock_response
        
        with pytest.raises(Exception):
            await client.health_check()
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, client, mock_session):
        """Test connection error handling."""
        mock_session.post.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            await client.health_check()


class TestVectorStoreClientValidation:
    """Test validation methods."""
    
    def test_invalid_url(self):
        """Test invalid URL validation."""
        with pytest.raises(ValidationError):
            VectorStoreClient("")
    
    def test_invalid_timeout(self):
        """Test invalid timeout validation."""
        with pytest.raises(ValidationError):
            VectorStoreClient("http://localhost:8007", timeout=-1)
    
    def test_invalid_timeout_type(self):
        """Test invalid timeout type validation."""
        with pytest.raises(ValidationError):
            VectorStoreClient("http://localhost:8007", timeout="invalid")


class TestVectorStoreClientIntegration:
    """Test integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test full workflow."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_session = AsyncMock()
            mock_session.is_closed = False
            mock_client_class.return_value = mock_session

            response_data = {
                "jsonrpc": "2.0",
                "result": {"status": "healthy"},
                "id": 1
            }
            mock_response = create_mock_response(response_data)
            mock_session.post.return_value = mock_response
            
            async with VectorStoreClient("http://localhost:8007") as client:
                health = await client.health_check()
                assert health.status == "healthy"


class TestNewTypes:
    """Test new type enums."""
    
    def test_chunk_role_enum(self):
        """Test chunk role enum."""
        from vector_store_client.types import ChunkRole
        assert ChunkRole.SYSTEM == "system"
        assert ChunkRole.USER == "user"
    
    def test_block_type_enum(self):
        """Test block type enum."""
        from vector_store_client.types import BlockType
        assert BlockType.PARAGRAPH == "paragraph"
        assert BlockType.MESSAGE == "message"
    
    def test_updated_chunk_type_enum(self):
        """Test updated chunk type enum."""
        assert ChunkType.DOC_BLOCK == "DocBlock"
        assert ChunkType.DRAFT == "Draft"
        assert ChunkType.CODE_BLOCK == "CodeBlock"
    
    def test_updated_language_enum(self):
        """Test updated language enum."""
        assert LanguageEnum.EN == "en"
        assert LanguageEnum.RU == "ru"
        assert LanguageEnum.UNKNOWN == "UNKNOWN"
    
    def test_updated_chunk_status_enum(self):
        """Test updated chunk status enum."""
        assert ChunkStatus.NEW == "NEW"
        assert ChunkStatus.RAW == "RAW"
        assert ChunkStatus.CLEANED == "CLEANED"


class TestNewExceptions:
    """Test new exception classes."""
    
    def test_svo_error(self):
        """Test SVO error."""
        from vector_store_client.exceptions import SVOError
        error = SVOError("SVO service error")
        assert str(error) == "SVO service error"
    
    def test_embedding_error(self):
        """Test embedding error."""
        from vector_store_client.exceptions import EmbeddingError
        error = EmbeddingError("Embedding service error")
        assert str(error) == "Embedding service error"


class TestNewValidation:
    """Test new validation functions."""
    
    def test_validate_source_id(self):
        """Test source ID validation."""
        from vector_store_client.validation import validate_source_id
        result = validate_source_id("550e8400-e29b-41d4-a716-446655440001")
        assert result == "550e8400-e29b-41d4-a716-446655440001"
        with pytest.raises(ValidationError):
            validate_source_id("invalid-uuid")
    
    def test_validate_embedding_dimension(self):
        """Test embedding dimension validation."""
        from vector_store_client.validation import validate_embedding
        embedding = [0.1] * 384
        result = validate_embedding(embedding)
        assert result == embedding
        with pytest.raises(ValidationError):
            validate_embedding([0.1] * 100)  # Wrong dimension
    
    def test_validate_chunk_metadata(self):
        """Test chunk metadata validation."""
        from vector_store_client.validation import validate_metadata
        metadata = {"key": "value", "number": 42}
        result = validate_metadata(metadata)
        assert result == metadata
        with pytest.raises(ValidationError):
            validate_metadata({"invalid": object()})  # Invalid value type
    
    def test_validate_chunk_role(self):
        """Test chunk role validation."""
        from vector_store_client.validation import validate_chunk_role
        result = validate_chunk_role("system")
        assert result == "system"
        result = validate_chunk_role("user")
        assert result == "user"
        with pytest.raises(ValidationError):
            validate_chunk_role("invalid")
    
    def test_validate_block_type(self):
        """Test block type validation."""
        from vector_store_client.validation import validate_block_type
        result = validate_block_type("paragraph")
        assert result == "paragraph"
        result = validate_block_type("message")
        assert result == "message"
        with pytest.raises(ValidationError):
            validate_block_type("invalid")


class TestNewModels:
    """Test new model classes."""
    
    def test_embed_response(self):
        """Test embed response model."""
        from vector_store_client.models import EmbedResponse
        response = EmbedResponse(
            embedding=[0.1] * 384,
            model="text-embedding-ada-002",
            dimension=384
        )
        assert len(response.embedding) == 384
        assert response.model == "text-embedding-ada-002"
    
    def test_models_response(self):
        """Test models response model."""
        from vector_store_client.models import ModelsResponse
        response = ModelsResponse(
            models=["model1", "model2"],
            default_model="model1",
            model_configs={"model1": {"dimension": 384}}
        )
        assert len(response.models) == 2
        assert response.default_model == "model1"
    
    def test_chunk_response(self):
        """Test chunk response model."""
        from vector_store_client.models import ChunkResponse, SemanticChunk
        chunk = SemanticChunk(
            body="Test content",
            text="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        response = ChunkResponse(
            chunks=[chunk],
            total_chunks=1
        )
        assert len(response.chunks) == 1
        assert response.total_chunks == 1 

 