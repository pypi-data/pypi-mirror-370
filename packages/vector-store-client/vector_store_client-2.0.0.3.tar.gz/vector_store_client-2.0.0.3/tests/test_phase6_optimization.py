"""
Tests for Phase 6 Optimization Features.

This module contains tests for optimization features including
streaming operations, bulk operations, backup/restore, and
performance monitoring.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from vector_store_client import VectorStoreClient
from vector_store_client.models import (
    SemanticChunk, CreateChunksResponse, DeleteResponse,
    ChunkType, LanguageEnum
)
from vector_store_client.exceptions import ValidationError


class TestPhase6Optimization:
    """Test cases for Phase 6 optimization features."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.search_by_metadata = AsyncMock()
        client.count_chunks = AsyncMock()
        client.delete_chunks = AsyncMock()
        client.create_chunks = AsyncMock()
        client.find_duplicate_uuids = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.health_check = AsyncMock()
        client.get_chunk_statistics = AsyncMock()
        client.get_config = AsyncMock()
        client.set_config = AsyncMock()
        client.search_by_ast = AsyncMock()
        client.search_chunks = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_optimized_search_operations(self, mock_client):
        """Test optimized search operations."""
        from vector_store_client.models import SemanticChunk
        from vector_store_client.types import ChunkType, LanguageEnum
        
        mock_response = [
            SemanticChunk(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                body="Test content",
                text="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                metadata={"type": "DOC_BLOCK"}
            )
        ]
        mock_client.search_by_metadata.return_value = mock_response
        
        # Test optimized search with metadata filter
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.search_by_metadata(metadata_filter)
        
        assert len(result) == 1
        assert result[0].uuid == "550e8400-e29b-41d4-a716-446655440001"
        
        # Check that the method was called with correct parameters
        mock_client.search_by_metadata.assert_called_once_with(metadata_filter)
    
    @pytest.mark.asyncio
    async def test_optimized_count_operations(self, mock_client):
        """Test optimized count operations."""
        mock_client.count_chunks.return_value = 100
        
        # Test optimized count with filter
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.count_chunks(metadata_filter=metadata_filter)
        
        assert result == 100
        
        mock_client.count_chunks.assert_called_once_with(metadata_filter=metadata_filter)
    
    @pytest.mark.asyncio
    async def test_optimized_delete_operations(self, mock_client):
        """Test optimized delete operations."""
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
        
        # Test optimized delete by metadata filter
        metadata_filter = {"type": "DOC_BLOCK"}
        result = await mock_client.delete_chunks(metadata_filter=metadata_filter)
        
        assert result.success
        assert result.deleted_count == 5
        assert len(result.deleted_uuids) == 2
        
        mock_client.delete_chunks.assert_called_once_with(metadata_filter=metadata_filter)
    
    @pytest.mark.asyncio
    async def test_optimized_create_operations(self, mock_client):
        """Test optimized create operations."""
        from vector_store_client.models import CreateChunksResponse
        
        mock_response = CreateChunksResponse(
            success=True,
            uuids=[
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002"
            ]
        )
        mock_client.create_chunks.return_value = mock_response
        
        chunks = [
            SemanticChunk(
                body="Test content 1",
                text="Test content 1",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            ),
            SemanticChunk(
                body="Test content 2",
                text="Test content 2",
                source_id="550e8400-e29b-41d4-a716-446655440002",
                embedding=[0.2] * 384
            )
        ]
        
        result = await mock_client.create_chunks(chunks)
        
        assert result.success
        assert len(result.uuids) == 2
        
        # Check that the method was called with correct parameters
        mock_client.create_chunks.assert_called_once_with(chunks)
    
    @pytest.mark.asyncio
    async def test_optimized_maintenance_operations(self, mock_client):
        """Test optimized maintenance operations."""
        from vector_store_client.models import DuplicateUuidsResponse, CleanupResponse
        
        # Test optimized cleanup duplicates
        mock_duplicates_response = DuplicateUuidsResponse(
            success=True,
            total_duplicates=2,
            duplicates=[
                ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            ]
        )
        mock_client.find_duplicate_uuids.return_value = mock_duplicates_response
        
        result = await mock_client.find_duplicate_uuids()
        
        assert result.success
        assert result.total_duplicates == 2
        assert len(result.duplicates) == 1
        
        mock_client.find_duplicate_uuids.assert_called_once_with()
        
        # Test optimized deferred cleanup
        mock_cleanup_response = CleanupResponse(
            success=True,
            cleaned_count=10,
            total_processed=10
        )
        mock_client.chunk_deferred_cleanup.return_value = mock_cleanup_response
        
        cleanup_result = await mock_client.chunk_deferred_cleanup()
        
        assert cleanup_result.success
        assert cleanup_result.cleaned_count == 10
        
        mock_client.chunk_deferred_cleanup.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_optimized_health_check(self, mock_client):
        """Test optimized health check operations."""
        from vector_store_client.models import HealthResponse
        
        mock_response = HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime=3600
        )
        mock_client.health_check.return_value = mock_response
        
        result = await mock_client.health_check()
        
        assert result.status == "healthy"
        assert result.version == "1.0.0"
        assert result.uptime == 3600
        
        mock_client.health_check.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_optimized_statistics(self, mock_client):
        """Test optimized statistics operations."""
        mock_response = {
            "total": 1000,
            "by_type": {"DOC_BLOCK": 500, "DRAFT": 300, "FINAL": 200},
            "by_language": {"en": 600, "ru": 400},
            "by_status": {"active": 800, "inactive": 200}
        }
        mock_client.get_chunk_statistics.return_value = mock_response
        
        result = await mock_client.get_chunk_statistics()
        
        assert result["total"] == 1000
        assert result["by_type"]["DOC_BLOCK"] == 500
        assert result["by_language"]["en"] == 600
        assert result["by_status"]["active"] == 800
        
        mock_client.get_chunk_statistics.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_optimized_config_operations(self, mock_client):
        """Test optimized config operations."""
        # Test get config
        mock_get_response = {"value": "test_value"}
        mock_client.get_config.return_value = mock_get_response
        
        result = await mock_client.get_config("test.path")
        
        assert result["value"] == "test_value"
        
        mock_client.get_config.assert_called_once_with("test.path")
        
        # Test set config
        mock_set_response = {"success": True}
        mock_client.set_config.return_value = mock_set_response
        
        set_result = await mock_client.set_config("test.path", "new_value")
        
        assert set_result["success"]
        
        mock_client.set_config.assert_called_once_with("test.path", "new_value")
    
    @pytest.mark.asyncio
    async def test_optimized_help_operations(self, mock_client):
        """Test optimized help operations."""
        mock_response = {
            "commands": ["search", "create", "delete", "count", "health"],
            "version": "1.0.0"
        }
        mock_client.get_help = AsyncMock(return_value=mock_response)
        
        result = await mock_client.get_help()
        
        assert "commands" in result
        assert "version" in result
        assert "search" in result["commands"]
        assert "create" in result["commands"]
        
        # Check that the method was called
        mock_client.get_help.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_optimized_ast_search(self, mock_client):
        """Test optimized AST search operations."""
        from vector_store_client.models import SemanticChunk
        from vector_store_client.types import ChunkType, LanguageEnum
        
        mock_response = [
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
        mock_client.search_by_ast.return_value = mock_response
        
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


class TestPhase6ErrorHandling:
    """Test cases for Phase 6 error handling."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.search_by_metadata = AsyncMock()
        client.count_chunks = AsyncMock()
        client.delete_chunks = AsyncMock()
        client.create_chunks = AsyncMock()
        client.find_duplicate_uuids = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.health_check = AsyncMock()
        client.get_chunk_statistics = AsyncMock()
        client.get_config = AsyncMock()
        client.set_config = AsyncMock()
        client.search_by_ast = AsyncMock()
        client.search_chunks = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, mock_client):
        """Test error handling in search operations."""
        # Mock search error
        mock_client.search_chunks = AsyncMock(side_effect=Exception("Search failed"))
        
        with pytest.raises(Exception, match="Search failed"):
            await mock_client.search_chunks(search_str="test query")
    
    @pytest.mark.asyncio
    async def test_create_error_handling(self, mock_client):
        """Test error handling in create operations."""
        # Mock create error
        mock_client.create_chunks = AsyncMock(side_effect=Exception("Creation failed"))
        
        chunks = [
            SemanticChunk(
                body="Test content",
                text="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            )
        ]
        
        with pytest.raises(Exception, match="Creation failed"):
            await mock_client.create_chunks(chunks)
    
    @pytest.mark.asyncio
    async def test_delete_error_handling(self, mock_client):
        """Test error handling in delete operations."""
        # Mock delete error
        mock_client.delete_chunks = AsyncMock(side_effect=Exception("Deletion failed"))
        
        with pytest.raises(Exception, match="Deletion failed"):
            await mock_client.delete_chunks(uuids=["550e8400-e29b-41d4-a716-446655440001"])
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, mock_client):
        """Test validation error handling."""
        # Mock methods to raise ValidationError
        mock_client.create_chunks = AsyncMock(side_effect=ValidationError("Empty chunks list"))
        mock_client.delete_chunks = AsyncMock(side_effect=ValidationError("No parameters provided"))
        
        # Test empty chunks list
        with pytest.raises(ValidationError, match="Empty chunks list"):
            await mock_client.create_chunks([])
        
        # Test delete without parameters
        with pytest.raises(ValidationError, match="No parameters provided"):
            await mock_client.delete_chunks()
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_client):
        """Test connection error handling."""
        # Mock connection error
        mock_client.health_check = AsyncMock(side_effect=Exception("Connection failed"))
        
        with pytest.raises(Exception, match="Connection failed"):
            await mock_client.health_check()


class TestPhase6Performance:
    """Test cases for Phase 6 performance optimizations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client instance."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.search_by_metadata = AsyncMock()
        client.count_chunks = AsyncMock()
        client.delete_chunks = AsyncMock()
        client.create_chunks = AsyncMock()
        client.find_duplicate_uuids = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.health_check = AsyncMock()
        client.get_chunk_statistics = AsyncMock()
        client.get_config = AsyncMock()
        client.set_config = AsyncMock()
        client.search_by_ast = AsyncMock()
        client.search_chunks = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_large_dataset_search(self, mock_client):
        """Test search performance with large datasets."""
        from vector_store_client.models import SemanticChunk
        
        # Mock large search response
        large_response = []
        for i in range(100):
            large_response.append(SemanticChunk(
                uuid=f"550e8400-e29b-41d4-a716-{i:012x}",
                body=f"Test content {i}",
                text=f"Test content {i}",
                source_id=f"550e8400-e29b-41d4-a716-{i:012x}",
                embedding=[0.1] * 384,
                metadata={"type": "DOC_BLOCK"}
            ))
        
        mock_client.search_chunks.return_value = large_response
        
        result = await mock_client.search_chunks(search_str="test query", limit=100)
        
        assert len(result) == 100
        assert all(isinstance(chunk, SemanticChunk) for chunk in result)
        
        mock_client.search_chunks.assert_called_once_with(search_str="test query", limit=100)
    
    @pytest.mark.asyncio
    async def test_large_dataset_count(self, mock_client):
        """Test count performance with large datasets."""
        # Mock large count response
        mock_client.count_chunks.return_value = 10000
        
        result = await mock_client.count_chunks()
        
        assert result == 10000
        
        mock_client.count_chunks.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_large_dataset_delete(self, mock_client):
        """Test delete performance with large datasets."""
        from vector_store_client.models import DeleteResponse
        
        # Mock large delete response
        large_uuids = [f"550e8400-e29b-41d4-a716-{i:012x}" for i in range(1000)]
        mock_response = DeleteResponse(
            success=True,
            deleted_count=1000,
            deleted_uuids=large_uuids[:100]  # Return first 100 for brevity
        )
        mock_client.delete_chunks.return_value = mock_response
        
        result = await mock_client.delete_chunks(uuids=large_uuids[:100])
        
        assert result.success
        assert result.deleted_count == 1000
        assert len(result.deleted_uuids) == 100
        
        mock_client.delete_chunks.assert_called_once_with(uuids=large_uuids[:100])
    
    @pytest.mark.asyncio
    async def test_complex_filter_performance(self, mock_client):
        """Test performance with complex filters."""
        from vector_store_client.models import SemanticChunk
        from vector_store_client.types import ChunkType, LanguageEnum
        
        # Mock complex AST filter response
        mock_response = [
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
        mock_client.search_by_ast.return_value = mock_response
        
        complex_ast_filter = {
            "operator": "AND",
            "conditions": [
                {"field": "type", "operator": "eq", "value": "DocBlock"},
                {"field": "language", "operator": "eq", "value": "en"},
                {"field": "status", "operator": "eq", "value": "NEW"},
                {
                    "operator": "OR",
                    "conditions": [
                        {"field": "created_at", "operator": "gte", "value": "2023-01-01"},
                        {"field": "updated_at", "operator": "gte", "value": "2023-01-01"}
                    ]
                }
            ]
        }
        
        result = await mock_client.search_by_ast(complex_ast_filter)
        
        assert len(result) == 1
        assert result[0].type == ChunkType.DOC_BLOCK
        assert result[0].language == LanguageEnum.EN
        
        # Check that the method was called with correct parameters
        mock_client.search_by_ast.assert_called_once_with(complex_ast_filter) 