"""
Tests for Phase 4: Maintenance Operations.

This module contains tests for the maintenance operations including
duplicate detection, cleanup, reindexing, and health checks.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from vector_store_client import VectorStoreClient
from vector_store_client.models import (
    SemanticChunk, DuplicateUuidsResponse, CleanupResponse, 
    ReindexResponse, DeleteResponse
)
from vector_store_client.exceptions import ValidationError
from vector_store_client.types import ChunkType, LanguageEnum


class TestDuplicateOperations:
    """Test cases for duplicate detection and cleanup operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids_basic(self, mock_client):
        """Test basic duplicate UUID detection."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        mock_response = DuplicateUuidsResponse(
            success=True,
            duplicates=[
                ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
                ["550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440004"]
            ],
            total_duplicates=4
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        result = await mock_client.find_duplicate_uuids()
        
        assert isinstance(result, DuplicateUuidsResponse)
        assert result.success is True
        assert result.total_duplicates == 4
        assert len(result.duplicates) == 2
        mock_client.find_duplicate_uuids.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids_with_filter(self, mock_client):
        """Test duplicate UUID detection with metadata filter."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        mock_response = DuplicateUuidsResponse(
            success=True,
            duplicates=[
                ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            ],
            total_duplicates=2
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        metadata_filter = {"type": "Draft"}
        result = await mock_client.find_duplicate_uuids(metadata_filter=metadata_filter)
        
        assert result.success is True
        assert result.total_duplicates == 2
        mock_client.find_duplicate_uuids.assert_called_once_with(metadata_filter=metadata_filter)
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids_with_ast_filter(self, mock_client):
        """Test duplicate UUID detection with AST filter."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        mock_response = DuplicateUuidsResponse(
            success=True,
            duplicates=[],
            total_duplicates=0
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        ast_filter = {"operator": "AND", "conditions": [{"field": "type", "value": "Draft"}]}
        result = await mock_client.find_duplicate_uuids(ast_filter=ast_filter)
        
        assert result.success is True
        assert result.total_duplicates == 0
        mock_client.find_duplicate_uuids.assert_called_once_with(ast_filter=ast_filter)
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_dry_run(self, mock_client):
        """Test duplicate cleanup in dry run mode."""
        mock_response = {
            "success": True,
            "dry_run": True,
            "total_duplicates": 2,
            "duplicate_groups": 1
        }
        mock_client.cleanup_duplicates.return_value = mock_response
        
        result = await mock_client.cleanup_duplicates(dry_run=True)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["total_duplicates"] == 2
        assert result["duplicate_groups"] == 1
        mock_client.cleanup_duplicates.assert_called_once_with(dry_run=True)
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_actual(self, mock_client):
        """Test actual duplicate cleanup."""
        mock_response = {
            "success": True,
            "dry_run": False,
            "total_duplicates": 2,
            "deleted_count": 1,
            "deleted_uuids": ["550e8400-e29b-41d4-a716-446655440002"]
        }
        mock_client.cleanup_duplicates.return_value = mock_response
        
        result = await mock_client.cleanup_duplicates(dry_run=False)
        
        assert result["success"] is True
        assert result["dry_run"] is False
        assert result["total_duplicates"] == 2
        assert result["deleted_count"] == 1
        assert "550e8400-e29b-41d4-a716-446655440002" in result["deleted_uuids"]
        mock_client.cleanup_duplicates.assert_called_once_with(dry_run=False)


class TestCleanupOperations:
    """Test cases for cleanup operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_clean_faiss_orphans(self, mock_client):
        """Test FAISS orphans cleanup."""
        from vector_store_client.models import CleanupResponse
        
        mock_response = CleanupResponse(
            success=True,
            cleaned_count=5,
            total_processed=5
        )
        mock_client.clean_faiss_orphans.return_value = mock_response
        
        result = await mock_client.clean_faiss_orphans()
        
        assert isinstance(result, CleanupResponse)
        assert result.success is True
        assert result.cleaned_count == 5
        mock_client.clean_faiss_orphans.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_chunk_deferred_cleanup(self, mock_client):
        """Test deferred chunk cleanup."""
        from vector_store_client.models import CleanupResponse
        
        mock_response = CleanupResponse(
            success=True,
            cleaned_count=10,
            total_processed=10
        )
        mock_client.chunk_deferred_cleanup.return_value = mock_response
        
        result = await mock_client.chunk_deferred_cleanup()
        
        assert isinstance(result, CleanupResponse)
        assert result.success is True
        assert result.cleaned_count == 10
        mock_client.chunk_deferred_cleanup.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids(self, mock_client):
        """Test force delete by UUIDs."""
        from vector_store_client.models import DeleteResponse
        
        mock_response = DeleteResponse(
            success=True,
            deleted_count=2,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        )
        mock_client.force_delete_by_uuids.return_value = mock_response
        
        uuids = ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        result = await mock_client.force_delete_by_uuids(uuids)
        
        assert isinstance(result, DeleteResponse)
        assert result.success is True
        assert result.deleted_count == 2
        assert len(result.deleted_uuids) == 2
        mock_client.force_delete_by_uuids.assert_called_once_with(uuids)
    
    @pytest.mark.asyncio
    async def test_force_delete_by_uuids_invalid(self, mock_client):
        """Test force delete by UUIDs with invalid UUIDs."""
        # Mock the method to raise ValidationError
        mock_client.force_delete_by_uuids = AsyncMock(side_effect=ValidationError("UUID at index 0: Chunk ID must be a valid UUID format"))
        
        with pytest.raises(ValidationError, match="UUID at index 0: Chunk ID must be a valid UUID format"):
            await mock_client.force_delete_by_uuids(["invalid-uuid"])


class TestReindexOperations:
    """Test cases for reindexing operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_reindex_missing_embeddings(self, mock_client):
        """Test reindexing missing embeddings."""
        from vector_store_client.models import ReindexResponse
        
        mock_response = ReindexResponse(
            success=True,
            reindexed_count=15,
            total_count=15
        )
        mock_client.reindex_missing_embeddings.return_value = mock_response
        
        result = await mock_client.reindex_missing_embeddings()
        
        assert isinstance(result, ReindexResponse)
        assert result.success is True
        assert result.reindexed_count == 15
        mock_client.reindex_missing_embeddings.assert_called_once_with()


class TestMaintenanceHealthOperations:
    """Test cases for maintenance health check operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_maintenance_health_check(self, mock_client):
        """Test maintenance health check."""
        mock_response = {
            "status": "healthy",
            "duplicate_chunks": 0,
            "orphaned_entries": 0,
            "maintenance_required": False
        }
        mock_client.maintenance_health_check.return_value = mock_response
        
        result = await mock_client.maintenance_health_check()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "duplicate_chunks" in result
        assert "orphaned_entries" in result
        assert "maintenance_required" in result
        
        # Check health status
        assert result["status"] == "healthy"
        assert result["duplicate_chunks"] == 0
        mock_client.maintenance_health_check.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_perform_full_maintenance(self, mock_client):
        """Test full maintenance cycle."""
        mock_response = {
            "faiss_cleanup": 5,
            "deferred_cleanup": 10,
            "reindex": 15
        }
        mock_client.perform_full_maintenance.return_value = mock_response
        
        result = await mock_client.perform_full_maintenance()
        
        assert isinstance(result, dict)
        assert "faiss_cleanup" in result
        assert "deferred_cleanup" in result
        assert "reindex" in result
        
        # Check operation results
        assert result["faiss_cleanup"] == 5
        assert result["deferred_cleanup"] == 10
        assert result["reindex"] == 15
        mock_client.perform_full_maintenance.assert_called_once_with()


class TestMaintenanceErrorHandling:
    """Test cases for maintenance operation error handling."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_maintenance_health_check_with_errors(self, mock_client):
        """Test maintenance health check with errors."""
        mock_response = {
            "status": "unhealthy",
            "error": "Service unavailable",
            "duplicate_chunks": 0,
            "orphaned_entries": 0,
            "maintenance_required": True
        }
        mock_client.maintenance_health_check.return_value = mock_response
        
        result = await mock_client.maintenance_health_check()
        
        assert isinstance(result, dict)
        assert result["status"] == "unhealthy"
        assert "error" in result
        mock_client.maintenance_health_check.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_perform_full_maintenance_with_errors(self, mock_client):
        """Test full maintenance cycle with errors."""
        mock_response = {
            "faiss_cleanup": 0,
            "deferred_cleanup": 10,
            "reindex": 0,
            "errors": ["Orphan cleanup failed", "Reindexing failed"]
        }
        mock_client.perform_full_maintenance.return_value = mock_response
        
        result = await mock_client.perform_full_maintenance()
        
        assert isinstance(result, dict)
        assert "faiss_cleanup" in result
        assert "deferred_cleanup" in result
        assert "reindex" in result
        assert "errors" in result
        
        # Check operation results
        assert result["faiss_cleanup"] == 0
        assert result["deferred_cleanup"] == 10
        assert result["reindex"] == 0
        assert len(result["errors"]) == 2
        mock_client.perform_full_maintenance.assert_called_once_with()


class TestMaintenanceValidation:
    """Test cases for maintenance operation validation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock VectorStoreClient."""
        client = VectorStoreClient("http://localhost:8007")
        # Mock the chunk_operations methods
        client.chunk_operations = AsyncMock()
        client.chunk_operations._execute_command = AsyncMock()
        
        # Mock the client methods that delegate to chunk_operations
        client.find_duplicate_uuids = AsyncMock()
        client.cleanup_duplicates = AsyncMock()
        client.clean_faiss_orphans = AsyncMock()
        client.chunk_deferred_cleanup = AsyncMock()
        client.force_delete_by_uuids = AsyncMock()
        client.reindex_missing_embeddings = AsyncMock()
        client.maintenance_health_check = AsyncMock()
        client.perform_full_maintenance = AsyncMock()
        
        return client
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates_invalid_filter(self, mock_client):
        """Test duplicate cleanup with invalid filter."""
        # Mock the cleanup_duplicates method to raise ValidationError
        mock_client.cleanup_duplicates = AsyncMock(side_effect=ValidationError("Invalid metadata filter"))
        
        with pytest.raises(ValidationError):
            await mock_client.cleanup_duplicates(metadata_filter="invalid")
    
    @pytest.mark.asyncio
    async def test_find_duplicate_uuids_invalid_ast_filter(self, mock_client):
        """Test duplicate detection with invalid AST filter."""
        from vector_store_client.models import DuplicateUuidsResponse
        
        invalid_ast_filter = {"invalid": "structure"}
        
        # Mock error response
        mock_response = DuplicateUuidsResponse(
            success=False,
            duplicates=[],
            total_duplicates=0,
            error={"message": "Invalid AST filter", "code": "INVALID_FILTER"}
        )
        mock_client.find_duplicate_uuids.return_value = mock_response
        
        result = await mock_client.find_duplicate_uuids(ast_filter=invalid_ast_filter)
        assert result.success is False
        assert result.error is not None
        mock_client.find_duplicate_uuids.assert_called_once_with(ast_filter=invalid_ast_filter) 