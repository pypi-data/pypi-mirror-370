"""
Tests for Phase 3 Vector Store Operations.

This module contains tests for enhanced deletion operations and
advanced search capabilities added in phase 3.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from vector_store_client import VectorStoreClient
from vector_store_client.models import (
    SemanticChunk, DeleteResponse, DuplicateUuidsResponse,
    ChunkType, LanguageEnum
)
from vector_store_client.exceptions import ValidationError


class TestEnhancedDeletionOperations:
    """Test cases for enhanced deletion operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.delete_chunks = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.chunk_hard_delete = AsyncMock()
        client.find_duplicate_uuids = AsyncMock()
        client.search_by_ast = AsyncMock()
        client.search_by_metadata = AsyncMock()
        client.count_chunks = AsyncMock()
        client.get_chunk_statistics = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_delete_by_metadata_filter(self, mock_client):
        """Test deletion by metadata filter."""
        from vector_store_client.models import DeleteResponse
        
        mock_response = DeleteResponse(
            success=True,
            deleted_count=5,
            deleted_uuids=[
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002"
            ]
        )
        mock_client.delete_chunks.return_value = mock_response
        
        metadata_filter = {"type": "DOC_BLOCK", "language": "en"}
        result = await mock_client.delete_chunks(metadata_filter=metadata_filter)
        
        assert result.success
        assert result.deleted_count == 5
        assert len(result.deleted_uuids) == 2
        
        # Verify the method was called with correct parameters
        mock_client.delete_chunks.assert_called_once_with(metadata_filter=metadata_filter)
    
    @pytest.mark.asyncio
    async def test_delete_by_ast_filter(self, mock_client):
        """Test deletion by AST filter."""
        from vector_store_client.models import DeleteResponse
        
        mock_response = DeleteResponse(
            success=True,
            deleted_count=3,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001"]
        )
        mock_client.delete_chunks.return_value = mock_response
        
        ast_filter = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "eq", "value": "DOC_BLOCK"},
                {"field": "language", "operator": "eq", "value": "en"}
            ]
        }
        
        # Use search_by_ast to get chunks, then delete by UUIDs
        mock_search_response = [
            SemanticChunk(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                body="Test content",
                text="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            )
        ]
        mock_client.search_by_ast.return_value = mock_search_response
        
        # Get chunks by AST filter
        chunks = await mock_client.search_by_ast(ast_filter)
        uuids = [chunk.uuid for chunk in chunks]
        
        # Delete the found chunks
        result = await mock_client.delete_chunks(uuids=uuids)
        
        assert result.success
        assert result.deleted_count == 3
        assert len(result.deleted_uuids) == 1
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids(self, mock_client):
        """Test force deletion by UUIDs."""
        from vector_store_client.models import DeleteResponse
        
        mock_response = DeleteResponse(
            success=True,
            deleted_count=2,
            deleted_uuids=[
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002"
            ]
        )
        mock_client.force_delete_by_uuids.return_value = mock_response
        
        uuids = [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002"
        ]
        result = await mock_client.force_delete_by_uuids(uuids)
        
        assert result.success
        assert result.deleted_count == 2
        assert len(result.deleted_uuids) == 2
        
        mock_client.force_delete_by_uuids.assert_called_once_with(uuids)
    
    @pytest.mark.asyncio
    async def test_hard_delete_chunks(self, mock_client):
        """Test hard deletion of chunks."""
        from vector_store_client.models import DeleteResponse
        
        mock_response = DeleteResponse(
            success=True,
            deleted_count=1,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001"]
        )
        mock_client.chunk_hard_delete.return_value = mock_response
        
        uuids = ["550e8400-e29b-41d4-a716-446655440001"]
        result = await mock_client.chunk_hard_delete(uuids, confirm=True)
        
        assert result.success
        assert result.deleted_count == 1
        assert len(result.deleted_uuids) == 1
        
        mock_client.chunk_hard_delete.assert_called_once_with(uuids, confirm=True)
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids(self, mock_client):
        """Test finding duplicate UUIDs."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        mock_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        result = await mock_client.find_duplicate_uuids()
        
        assert result.success
        assert result.total_duplicates == 2
        assert len(result.duplicates) == 1
        
        mock_client.find_duplicate_uuids.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids_with_filter(self, mock_client):
        """Test finding duplicate UUIDs with metadata filter."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        mock_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=1,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.find_duplicate_uuids(metadata_filter=metadata_filter)
        
        assert result.success
        assert result.total_duplicates == 1
        assert len(result.duplicates) == 1
        
        mock_client.find_duplicate_uuids.assert_called_once_with(metadata_filter=metadata_filter)
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates(self, mock_client):
        """Test cleanup of duplicate chunks."""
        # Mock find_duplicate_uuids
        mock_duplicates_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        mock_client.find_duplicate_uuids = AsyncMock(return_value=mock_duplicates_response)
        
        # Mock force_delete_by_uuids
        mock_delete_response = DeleteResponse(
            success=True,
            deleted_count=1,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440002"]
        )
        mock_client.force_delete_by_uuids = AsyncMock(return_value=mock_delete_response)
        
        result = await mock_client.cleanup_duplicates(dry_run=False)
        
        assert result["success"]
        assert "deleted_count" in result
        assert result["deleted_count"] == 1
        
        # Verify force_delete_by_uuids was called for each duplicate group
        mock_client.force_delete_by_uuids.assert_called_once_with(
            ["550e8400-e29b-41d4-a716-446655440002"]
        )
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_dry_run(self, mock_client):
        """Test cleanup of duplicate chunks in dry run mode."""
        mock_duplicates_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]]
        )
        mock_client.find_duplicate_uuids = AsyncMock(return_value=mock_duplicates_response)
        mock_client.force_delete_by_uuids = AsyncMock()
        
        result = await mock_client.cleanup_duplicates(dry_run=True)
        
        assert result["success"]
        assert result.get("dry_run", False) is True
        assert result.get("deleted_count", 0) == 0
        
        # Verify force_delete_by_uuids was not called in dry run mode
        mock_client.force_delete_by_uuids.assert_not_called()


class TestAdvancedSearchOperations:
    """Test cases for advanced search operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.delete_chunks = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.chunk_hard_delete = AsyncMock()
        client.find_duplicate_uuids = AsyncMock()
        client.search_by_ast = AsyncMock()
        client.search_by_metadata = AsyncMock()
        client.count_chunks = AsyncMock()
        client.get_chunk_statistics = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_search_by_ast_filter(self, mock_client):
        """Test search using AST filter."""
        mock_search_response = [
            SemanticChunk(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                body="Test content",
                text="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN
            )
        ]
        mock_client.search_by_ast.return_value = mock_search_response
        
        ast_filter = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "eq", "value": "DocBlock"},
                {"field": "language", "operator": "eq", "value": "en"}
            ]
        }
        
        result = await mock_client.search_by_ast(ast_filter)
        
        assert len(result) == 1
        assert result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        assert result[0].type == ChunkType.DOC_BLOCK
        
        # Check that the method was called with correct parameters
        mock_client.search_by_ast.assert_called_once_with(ast_filter)
    
    @pytest.mark.asyncio
    async def test_search_by_metadata_filter(self, mock_client):
        """Test search using metadata filter."""
        mock_search_response = [
            SemanticChunk(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                body="Test content",
                text="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                metadata={"type": "DOC_BLOCK"}
            )
        ]
        mock_client.search_by_metadata.return_value = mock_search_response
        
        metadata_filter = {"type": "DOC_BLOCK", "language": "en"}
        result = await mock_client.search_by_metadata(metadata_filter)
        
        assert len(result) == 1
        assert result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        
        # Check that the method was called with correct parameters
        mock_client.search_by_metadata.assert_called_once_with(metadata_filter)
    
    @pytest.mark.asyncio
    async def test_count_chunks_with_filters(self, mock_client):
        """Test counting chunks with various filters."""
        mock_client.count_chunks.return_value = 5
        
        # Test with metadata filter
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.count_chunks(metadata_filter=metadata_filter)
        
        assert result == 5
        mock_client.count_chunks.assert_called_once_with(metadata_filter=metadata_filter)
        
        # Reset mock for next test
        mock_client.count_chunks.reset_mock()
        
        # Test with AST filter
        ast_filter = {"operator": "AND", "conditions": [{"field": "type", "operator": "eq", "value": "DOC_BLOCK"}]}
        result = await mock_client.count_chunks(ast_filter=ast_filter)
        
        assert result == 5
        mock_client.count_chunks.assert_called_once_with(ast_filter=ast_filter)
    
    @pytest.mark.asyncio
    async def test_get_chunk_statistics(self, mock_client):
        """Test getting chunk statistics."""
        mock_response = {
            "total": 100,
            "by_type": {"DOC_BLOCK": 50, "DRAFT": 30, "FINAL": 20},
            "by_language": {"en": 60, "ru": 40},
            "by_status": {"active": 80, "inactive": 20}
        }
        mock_client.get_chunk_statistics.return_value = mock_response
        
        result = await mock_client.get_chunk_statistics()
        
        assert result["total"] == 100
        assert result["by_type"]["DOC_BLOCK"] == 50
        assert result["by_language"]["en"] == 60
        assert result["by_status"]["active"] == 80
        
        mock_client.get_chunk_statistics.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_get_chunk_statistics_with_filter(self, mock_client):
        """Test getting chunk statistics with metadata filter."""
        mock_response = {
            "total": 25,
            "by_type": {"DOC_BLOCK": 25},
            "by_language": {"en": 25},
            "by_status": {"active": 25}
        }
        mock_client.get_chunk_statistics.return_value = mock_response
        
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.get_chunk_statistics(metadata_filter=metadata_filter)
        
        assert result["total"] == 25
        assert result["by_type"]["DOC_BLOCK"] == 25
        
        mock_client.get_chunk_statistics.assert_called_once_with(metadata_filter=metadata_filter) 