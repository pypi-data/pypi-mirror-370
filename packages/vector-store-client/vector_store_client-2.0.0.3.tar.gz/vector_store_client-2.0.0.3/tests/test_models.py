"""
Tests for vector_store_client.models module.

This module tests all Pydantic models used in the Vector Store client,
including request/response models and data validation.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import uuid
import pytest
from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import ValidationError

from vector_store_client.models import (
    SemanticChunk, SearchResult, JsonRpcRequest, JsonRpcResponse,
    HealthResponse, CreateChunksResponse, SearchResponse, DeleteResponse,
    HelpResponse, ConfigResponse, DuplicateUuidsResponse, EmbedResponse,
    ModelsResponse, ChunkResponse, CleanupResponse, ReindexResponse,
    MaintenanceHealthResponse, MaintenanceResultsResponse, DuplicateCleanupResponse
)
from vector_store_client.types import (
    ChunkType, LanguageEnum, ChunkStatus, SearchOrder, EmbeddingModel,
    ChunkRole, BlockType
)


class TestSemanticChunk:
    """Test SemanticChunk model."""
    
    def test_valid_chunk_creation(self):
        """Test creating a valid chunk."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        
        assert chunk.body == "Test content"
        assert chunk.source_id == "550e8400-e29b-41d4-a716-446655440001"
        assert len(chunk.embedding) == 384
        assert chunk.type == ChunkType.DOC_BLOCK
        assert chunk.language == LanguageEnum.EN
        assert chunk.role == ChunkRole.USER
        assert chunk.status.value == 'new'  # Check the actual value
    
    def test_chunk_with_optional_fields(self):
        """Test creating chunk with optional fields."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            text="Normalized text",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.RU,
            category="test",
            title="Test Title",
            project="test-project",
            year=2023,
            is_public=True,
            source="test-source"
        )
        
        assert chunk.text == "Normalized text"
        assert chunk.type == ChunkType.CODE_BLOCK
        assert chunk.language == LanguageEnum.RU
        assert chunk.category == "test"
        assert chunk.title == "Test Title"
        assert chunk.project == "test-project"
        assert chunk.year == 2023
        assert chunk.is_public is True
        assert chunk.source == "test-source"
    
    def test_chunk_with_structural_fields(self):
        """Test creating chunk with structural fields."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            ordinal=1,
            start=0,
            end=100,
            block_index=0,
            source_lines_start=1,
            source_lines_end=10,
            source_path="/path/to/file.txt",
            block_type=BlockType.MESSAGE,
            chunking_version="1.0"
        )
        
        assert chunk.ordinal == 1
        assert chunk.start == 0
        assert chunk.end == 100
        assert chunk.block_index == 0
        assert chunk.source_lines_start == 1
        assert chunk.source_lines_end == 10
        assert chunk.source_path == "/path/to/file.txt"
        assert chunk.block_type == BlockType.MESSAGE
        assert chunk.chunking_version == "1.0"
    
    def test_chunk_with_quality_metrics(self):
        """Test creating chunk with quality metrics."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            quality_score=0.8,
            coverage=0.9,
            cohesion=0.7,
            boundary_prev=0.6,
            boundary_next=0.5,
            used_in_generation=True
        )
        
        assert chunk.quality_score == 0.8
        assert chunk.coverage == 0.9
        assert chunk.cohesion == 0.7
        assert chunk.boundary_prev == 0.6
        assert chunk.boundary_next == 0.5
        assert chunk.used_in_generation is True
    
    def test_chunk_with_feedback(self):
        """Test creating chunk with feedback."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            feedback_accepted=10,
            feedback_rejected=2,
            feedback_modifications=3
        )
        
        assert chunk.feedback_accepted == 10
        assert chunk.feedback_rejected == 2
        assert chunk.feedback_modifications == 3
    
    def test_chunk_with_tags_and_links(self):
        """Test creating chunk with tags and links."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            tags=["tag1", "tag2"],
            links=["link1", "link2"]
        )
        
        assert chunk.tags == ["tag1", "tag2"]
        assert chunk.links == ["link1", "link2"]
    
    def test_chunk_validation_uuid(self):
        """Test UUID validation."""
        # Valid UUID
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            uuid="550e8400-e29b-41d4-a716-446655440002"
        )
        assert chunk.uuid == "550e8400-e29b-41d4-a716-446655440002"
        
        # Invalid UUID
        with pytest.raises(ValidationError, match="Invalid UUID"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                uuid="invalid-uuid"
            )
    
    def test_chunk_validation_source_id(self):
        """Test source_id validation."""
        # Valid source_id
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        assert chunk.source_id == "550e8400-e29b-41d4-a716-446655440001"
        
        # Invalid source_id
        with pytest.raises(ValidationError, match="source_id must be a valid UUID"):
            SemanticChunk(
                body="Test content",
                source_id="invalid-source-id",
                embedding=[0.1] * 384
            )
    
    def test_chunk_validation_embedding(self):
        """Test embedding validation."""
        # Valid embedding
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        assert len(chunk.embedding) == 384
        
        # Invalid embedding dimension
        with pytest.raises(ValidationError, match="Embedding must have exactly 384 dimensions"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 100
            )
        
        # Invalid embedding content
        with pytest.raises(ValidationError, match="Input should be a valid number"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=["invalid"] * 384
            )
    
    def test_chunk_validation_tags(self):
        """Test tags validation."""
        # Valid tags
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            tags=["tag1", "tag2", "tag3"]
        )
        assert len(chunk.tags) == 3
        
        # Too many tags
        with pytest.raises(ValidationError, match="List should have at most 32 items"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                tags=[f"tag{i}" for i in range(33)]
            )
        
        # Empty tag
        with pytest.raises(ValidationError, match="Tags must be non-empty strings"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                tags=["tag1", "", "tag3"]
            )
    
    def test_chunk_validation_links(self):
        """Test links validation."""
        # Valid links
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            links=["link1", "link2", "link3"]
        )
        assert len(chunk.links) == 3
        
        # Too many links
        with pytest.raises(ValidationError, match="List should have at most 32 items"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                links=[f"link{i}" for i in range(33)]
            )
        
        # Empty link
        with pytest.raises(ValidationError, match="Links must be non-empty strings"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                links=["link1", "", "link3"]
            )
    
    def test_chunk_content_validation(self):
        """Test content validation."""
        # Empty body
        with pytest.raises(ValidationError, match="Body cannot be empty"):
            SemanticChunk(
                body="",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            )
        
        # Body too long
        with pytest.raises(ValidationError, match="Body cannot exceed 10000 characters"):
            SemanticChunk(
                body="x" * 10001,
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384
            )
        
        # Text too long
        with pytest.raises(ValidationError, match="Text cannot exceed 10000 characters"):
            SemanticChunk(
                body="Test content",
                source_id="550e8400-e29b-41d4-a716-446655440001",
                embedding=[0.1] * 384,
                text="x" * 10001
            )
    
    def test_chunk_model_dump(self):
        """Test model_dump method."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            text="Normalized text"
        )
        
        data = chunk.model_dump()
        assert data["body"] == "Test content"
        assert data["source_id"] == "550e8400-e29b-41d4-a716-446655440001"
        assert len(data["embedding"]) == 384
        assert data["text"] == "Normalized text"
        
        # Test that None values are removed
        chunk_with_none = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384,
            uuid=None,
            text=None
        )
        data = chunk_with_none.model_dump()
        assert "uuid" not in data
        # text will be set to body in model_validator, so it won't be None
        assert "text" in data


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_valid_search_result(self):
        """Test creating a valid search result."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        
        result = SearchResult(
            chunk=chunk,
            relevance_score=0.85,
            rank=1
        )
        
        assert result.chunk == chunk
        assert result.relevance_score == 0.85
        assert result.rank == 1
    
    def test_relevance_score_validation(self):
        """Test relevance score validation."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        
        # Valid score
        result = SearchResult(chunk=chunk, relevance_score=0.5)
        assert result.relevance_score == 0.5
        
        # Score too low
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            SearchResult(chunk=chunk, relevance_score=-0.1)
        
        # Score too high
        with pytest.raises(ValidationError, match="less than or equal to 1"):
            SearchResult(chunk=chunk, relevance_score=1.1)


class TestJsonRpcRequest:
    """Test JsonRpcRequest model."""
    
    def test_valid_request(self):
        """Test creating a valid JSON-RPC request."""
        request = JsonRpcRequest(
            method="test_method",
            params={"key": "value"},
            id="request-1"
        )
        
        assert request.jsonrpc == "2.0"
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.id == "request-1"
    
    def test_request_without_params(self):
        """Test creating request without parameters."""
        request = JsonRpcRequest(method="test_method")
        
        assert request.jsonrpc == "2.0"
        assert request.method == "test_method"
        assert request.params is None
        assert request.id == 1
    
    def test_jsonrpc_version_validation(self):
        """Test JSON-RPC version validation."""
        # Valid version
        request = JsonRpcRequest(method="test_method", jsonrpc="2.0")
        assert request.jsonrpc == "2.0"
        
        # Invalid version
        with pytest.raises(ValidationError, match="must be '2.0'"):
            JsonRpcRequest(method="test_method", jsonrpc="1.0")
    
    def test_method_validation(self):
        """Test method validation."""
        # Valid method
        request = JsonRpcRequest(method="test_method")
        assert request.method == "test_method"
        
        # Empty method
        with pytest.raises(ValidationError, match="Method name cannot be empty"):
            JsonRpcRequest(method="")
        
        # Whitespace method
        with pytest.raises(ValidationError, match="Method name cannot be empty"):
            JsonRpcRequest(method="   ")


class TestJsonRpcResponse:
    """Test JsonRpcResponse model."""
    
    def test_success_response(self):
        """Test creating a success response."""
        response = JsonRpcResponse(
            result={"status": "success"},
            id="request-1"
        )
        
        assert response.jsonrpc == "2.0"
        assert response.result == {"status": "success"}
        assert response.error is None
        assert response.id == "request-1"
    
    def test_error_response(self):
        """Test creating an error response."""
        response = JsonRpcResponse(
            error={"code": -32601, "message": "Method not found"},
            id="request-1"
        )
        
        assert response.jsonrpc == "2.0"
        assert response.result is None
        assert response.error == {"code": -32601, "message": "Method not found"}
        assert response.id == "request-1"
    
    def test_jsonrpc_version_validation(self):
        """Test JSON-RPC version validation."""
        # Valid version
        response = JsonRpcResponse(result={}, id=1, jsonrpc="2.0")
        assert response.jsonrpc == "2.0"
        
        # Invalid version
        with pytest.raises(ValidationError, match="must be '2.0'"):
            JsonRpcResponse(result={}, id=1, jsonrpc="1.0")
    
    def test_response_validation(self):
        """Test response validation."""
        # Both result and error
        with pytest.raises(ValidationError, match="Response cannot have both result and error"):
            JsonRpcResponse(
                result={"status": "success"},
                error={"code": -1, "message": "error"},
                id=1
            )
        
        # Neither result nor error
        with pytest.raises(ValidationError, match="Response must have either result or error"):
            JsonRpcResponse(id=1)


class TestHealthResponse:
    """Test HealthResponse model."""
    
    def test_valid_health_response(self):
        """Test creating a valid health response."""
        response = HealthResponse(
            status="healthy",
            timestamp="2023-01-01T00:00:00Z",
            version="1.0.0",
            uptime=3600.0,
            memory_usage={"used": 1024, "total": 2048},
            disk_usage={"used": 512, "total": 1024}
        )
        
        assert response.status == "healthy"
        assert response.timestamp == "2023-01-01T00:00:00Z"
        assert response.version == "1.0.0"
        assert response.uptime == 3600.0
        assert response.memory_usage == {"used": 1024, "total": 2048}
        assert response.disk_usage == {"used": 512, "total": 1024}
    
    def test_status_validation(self):
        """Test status validation."""
        # Valid statuses
        for status in ["healthy", "unhealthy", "degraded"]:
            response = HealthResponse(status=status)
            assert response.status == status
        
        # Invalid status
        with pytest.raises(ValidationError, match="Status must be one of"):
            HealthResponse(status="invalid")


class TestCreateChunksResponse:
    """Test CreateChunksResponse model."""
    
    def test_successful_response(self):
        """Test successful response."""
        response = CreateChunksResponse(
            success=True,
            uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
            created_count=2,
            failed_count=0
        )
        
        assert response.success is True
        assert response.uuids == ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        assert response.created_count == 2
        assert response.failed_count == 0
        assert response.error is None
    
    def test_failed_response(self):
        """Test failed response."""
        response = CreateChunksResponse(
            success=False,
            error={"message": "Creation failed"},
            created_count=0,
            failed_count=2
        )
        
        assert response.success is False
        assert response.error == {"message": "Creation failed"}
        assert response.created_count == 0
        assert response.failed_count == 2
        assert response.uuids is None
    
    def test_uuid_validation(self):
        """Test UUID validation."""
        # Valid UUIDs
        response = CreateChunksResponse(
            success=True,
            uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        )
        assert len(response.uuids) == 2
        
        # Invalid UUID
        with pytest.raises(ValidationError, match="Invalid UUID"):
            CreateChunksResponse(
                success=True,
                uuids=["invalid-uuid"]
            )
    
    def test_response_validation(self):
        """Test response validation."""
        # Success without UUIDs
        with pytest.raises(ValidationError, match="Successful response must include UUIDs"):
            CreateChunksResponse(success=True)
        
        # Failed without error
        with pytest.raises(ValidationError, match="Failed response must include error information"):
            CreateChunksResponse(success=False)


class TestSearchResponse:
    """Test SearchResponse model."""
    
    def test_valid_search_response(self):
        """Test creating a valid search response."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        result = SearchResult(chunk=chunk, relevance_score=0.8)
        
        response = SearchResponse(
            results=[result],
            total_count=1,
            query_time=0.1,
            search_params={"query": "test"}
        )
        
        assert len(response.results) == 1
        assert response.total_count == 1
        assert response.query_time == 0.1
        assert response.search_params == {"query": "test"}
    
    def test_total_count_validation(self):
        """Test total count validation."""
        # Valid count
        response = SearchResponse(total_count=0)
        assert response.total_count == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Total count cannot be negative"):
            SearchResponse(total_count=-1)
    
    def test_query_time_validation(self):
        """Test query time validation."""
        # Valid time
        response = SearchResponse(query_time=0.5)
        assert response.query_time == 0.5
        
        # Negative time
        with pytest.raises(ValidationError, match="Query time cannot be negative"):
            SearchResponse(query_time=-0.1)


class TestDeleteResponse:
    """Test DeleteResponse model."""
    
    def test_successful_delete(self):
        """Test successful delete response."""
        response = DeleteResponse(
            success=True,
            deleted_count=2,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        )
        
        assert response.success is True
        assert response.deleted_count == 2
        assert response.deleted_uuids == ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
        assert response.error is None
    
    def test_failed_delete(self):
        """Test failed delete response."""
        response = DeleteResponse(
            success=False,
            error={"message": "Delete failed"},
            deleted_count=0
        )
        
        assert response.success is False
        assert response.error == {"message": "Delete failed"}
        assert response.deleted_count == 0
        assert response.deleted_uuids is None
    
    def test_deleted_count_validation(self):
        """Test deleted count validation."""
        # Valid count
        response = DeleteResponse(success=True, deleted_count=0)
        assert response.deleted_count == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Deleted count cannot be negative"):
            DeleteResponse(success=True, deleted_count=-1)
    
    def test_deleted_uuids_validation(self):
        """Test deleted UUIDs validation."""
        # Valid UUIDs
        response = DeleteResponse(
            success=True,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001"]
        )
        assert len(response.deleted_uuids) == 1
        
        # Invalid UUID
        with pytest.raises(ValidationError, match="Invalid UUID"):
            DeleteResponse(
                success=True,
                deleted_uuids=["invalid-uuid"]
            )


class TestHelpResponse:
    """Test HelpResponse model."""
    
    def test_successful_help(self):
        """Test successful help response."""
        response = HelpResponse(
            success=True,
            help_data={"commands": ["search", "create"]}
        )
        
        assert response.success is True
        assert response.help_data == {"commands": ["search", "create"]}
        assert response.error is None
    
    def test_failed_help(self):
        """Test failed help response."""
        response = HelpResponse(
            success=False,
            error={"message": "Help not available"}
        )
        
        assert response.success is False
        assert response.error == {"message": "Help not available"}
        assert response.help_data is None
    
    def test_help_data_validation(self):
        """Test help data validation."""
        # Valid data
        response = HelpResponse(help_data={"key": "value"})
        assert response.help_data == {"key": "value"}
        
        # Invalid data type
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            HelpResponse(help_data="not a dict")


class TestConfigResponse:
    """Test ConfigResponse model."""
    
    def test_successful_config(self):
        """Test successful config response."""
        response = ConfigResponse(
            success=True,
            config={"timeout": 30},
            path="server.timeout",
            value=30,
            old_value=60
        )
        
        assert response.success is True
        assert response.config == {"timeout": 30}
        assert response.path == "server.timeout"
        assert response.value == 30
        assert response.old_value == 60
    
    def test_failed_config(self):
        """Test failed config response."""
        response = ConfigResponse(
            success=False,
            error={"message": "Config not found"}
        )
        
        assert response.success is False
        assert response.error == {"message": "Config not found"}
    
    def test_path_validation(self):
        """Test path validation."""
        # Valid path
        response = ConfigResponse(path="server.timeout")
        assert response.path == "server.timeout"
        
        # Invalid path type
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            ConfigResponse(path=123)


class TestDuplicateUuidsResponse:
    """Test DuplicateUuidsResponse model."""
    
    def test_successful_duplicates(self):
        """Test successful duplicates response."""
        response = DuplicateUuidsResponse(
            success=True,
            duplicates=[["uuid1", "uuid2"], ["uuid3", "uuid4"]],
            total_duplicates=4
        )
        
        assert response.success is True
        assert len(response.duplicates) == 2
        assert response.total_duplicates == 4
        assert response.error is None
    
    def test_failed_duplicates(self):
        """Test failed duplicates response."""
        response = DuplicateUuidsResponse(
            success=False,
            error={"message": "Search failed"}
        )
        
        assert response.success is False
        assert response.error == {"message": "Search failed"}
        assert response.duplicates is None
    
    def test_duplicates_validation(self):
        """Test duplicates validation."""
        # Valid duplicates
        response = DuplicateUuidsResponse(
            duplicates=[["uuid1", "uuid2"]]
        )
        assert len(response.duplicates) == 1
        
        # Invalid structure
        with pytest.raises(ValidationError, match="Input should be a valid list"):
            DuplicateUuidsResponse(
                duplicates=[["uuid1"], "not a list"]
            )
    
    def test_total_duplicates_validation(self):
        """Test total duplicates validation."""
        # Valid count
        response = DuplicateUuidsResponse(total_duplicates=0)
        assert response.total_duplicates == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="total_duplicates must be non-negative"):
            DuplicateUuidsResponse(total_duplicates=-1)
    
    def test_response_validation(self):
        """Test response validation."""
        # Success with error
        with pytest.raises(ValidationError, match="Cannot have both success=True and error"):
            DuplicateUuidsResponse(
                success=True,
                error={"message": "error"}
            )
        
        # Failed without error
        with pytest.raises(ValidationError, match="Must have error when success=False"):
            DuplicateUuidsResponse(success=False)


class TestEmbedResponse:
    """Test EmbedResponse model."""
    
    def test_valid_embed_response(self):
        """Test creating a valid embed response."""
        response = EmbedResponse(
            embedding=[0.1] * 384,
            model="text-embedding-ada-002",
            dimension=384,
            metadata={"model_version": "1.0"}
        )
        
        assert len(response.embedding) == 384
        assert response.model == "text-embedding-ada-002"
        assert response.dimension == 384
        assert response.metadata == {"model_version": "1.0"}
    
    def test_embedding_validation(self):
        """Test embedding validation."""
        # Valid embedding
        response = EmbedResponse(
            embedding=[0.1, 0.2, 0.3],
            model="test",
            dimension=3
        )
        assert len(response.embedding) == 3
        
        # Invalid embedding content
        with pytest.raises(ValidationError, match="Input should be a valid number"):
            EmbedResponse(
                embedding=["invalid", 0.2, 0.3],
                model="test",
                dimension=3
            )
    
    def test_dimension_validation(self):
        """Test dimension validation."""
        # Valid dimension
        response = EmbedResponse(
            embedding=[0.1],
            model="test",
            dimension=1
        )
        assert response.dimension == 1
        
        # Zero dimension
        with pytest.raises(ValidationError, match="Dimension must be positive"):
            EmbedResponse(
                embedding=[],
                model="test",
                dimension=0
            )
        
        # Negative dimension
        with pytest.raises(ValidationError, match="Dimension must be positive"):
            EmbedResponse(
                embedding=[],
                model="test",
                dimension=-1
            )


class TestModelsResponse:
    """Test ModelsResponse model."""
    
    def test_valid_models_response(self):
        """Test creating a valid models response."""
        response = ModelsResponse(
            models=["model1", "model2", "model3"],
            default_model="model1",
            model_configs={
                "model1": {"dimension": 384},
                "model2": {"dimension": 768}
            }
        )
        
        assert len(response.models) == 3
        assert response.default_model == "model1"
        assert len(response.model_configs) == 2
    
    def test_models_validation(self):
        """Test models validation."""
        # Valid models
        response = ModelsResponse(
            models=["model1"],
            default_model="model1",
            model_configs={}
        )
        assert len(response.models) == 1
    
        # Empty models list - this should work now as validation was removed
        response = ModelsResponse(
            models=[],
            default_model="model1",
            model_configs={}
        )
        assert len(response.models) == 0
        
        # Invalid model name - this should work now as validation was removed
        response = ModelsResponse(
            models=["model1", "model2"],
            default_model="model1",
            model_configs={}
        )
        assert len(response.models) == 2
    
    def test_default_model_validation(self):
        """Test default model validation."""
        # Valid default model
        response = ModelsResponse(
            models=["model1"],
            default_model="model1",
            model_configs={}
        )
        assert response.default_model == "model1"
        
        # Empty default model - this should work now as validation was removed
        response = ModelsResponse(
            models=["model1"],
            default_model="",
            model_configs={}
        )
        assert response.default_model == "default"  # Default value is 'default'
        
        # Whitespace default model - this should work now as validation was removed
        response = ModelsResponse(
            models=["model1"],
            default_model="   ",
            model_configs={}
        )
        assert response.default_model == "default"  # Whitespace is replaced with default


class TestChunkResponse:
    """Test ChunkResponse model."""
    
    def test_valid_chunk_response(self):
        """Test creating a valid chunk response."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        
        response = ChunkResponse(
            chunks=[chunk],
            total_chunks=1,
            chunking_metadata={"version": "1.0"}
        )
        
        assert len(response.chunks) == 1
        assert response.total_chunks == 1
        assert response.chunking_metadata == {"version": "1.0"}
    
    def test_total_chunks_validation(self):
        """Test total chunks validation."""
        # Valid count
        response = ChunkResponse(chunks=[], total_chunks=0)
        assert response.total_chunks == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Total chunks cannot be negative"):
            ChunkResponse(chunks=[], total_chunks=-1)
    
    def test_chunks_consistency_validation(self):
        """Test chunks consistency validation."""
        chunk = SemanticChunk(
            body="Test content",
            source_id="550e8400-e29b-41d4-a716-446655440001",
            embedding=[0.1] * 384
        )
        
        # Inconsistent count
        with pytest.raises(ValidationError, match="Chunks list length must match total_chunks"):
            ChunkResponse(
                chunks=[chunk],
                total_chunks=2
            )


class TestCleanupResponse:
    """Test CleanupResponse model."""
    
    def test_successful_cleanup(self):
        """Test successful cleanup response."""
        response = CleanupResponse(
            success=True,
            cleaned_count=10
        )
        
        assert response.success is True
        assert response.cleaned_count == 10
        assert response.error is None
    
    def test_failed_cleanup(self):
        """Test failed cleanup response."""
        response = CleanupResponse(
            success=False,
            error={"message": "Cleanup failed"}
        )
        
        assert response.success is False
        assert response.error == {"message": "Cleanup failed"}
        assert response.cleaned_count is None
    
    def test_cleaned_count_validation(self):
        """Test cleaned count validation."""
        # Valid count
        response = CleanupResponse(success=True, cleaned_count=0)
        assert response.cleaned_count == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Cleaned count cannot be negative"):
            CleanupResponse(success=True, cleaned_count=-1)


class TestReindexResponse:
    """Test ReindexResponse model."""
    
    def test_successful_reindex(self):
        """Test successful reindex response."""
        response = ReindexResponse(
            success=True,
            reindexed_count=5
        )
        
        assert response.success is True
        assert response.reindexed_count == 5
        assert response.error is None
    
    def test_failed_reindex(self):
        """Test failed reindex response."""
        response = ReindexResponse(
            success=False,
            error={"message": "Reindex failed"}
        )
        
        assert response.success is False
        assert response.error == {"message": "Reindex failed"}
        assert response.reindexed_count is None
    
    def test_reindexed_count_validation(self):
        """Test reindexed count validation."""
        # Valid count
        response = ReindexResponse(success=True, reindexed_count=0)
        assert response.reindexed_count == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Reindexed count must be non-negative"):
            ReindexResponse(success=True, reindexed_count=-1)


class TestMaintenanceHealthResponse:
    """Test MaintenanceHealthResponse model."""
    
    def test_valid_maintenance_health(self):
        """Test creating a valid maintenance health response."""
        response = MaintenanceHealthResponse(
            duplicates={"status": "healthy", "count": 0},
            orphans={"status": "healthy", "count": 0},
            deleted={"status": "healthy", "count": 0},
            embeddings={"status": "healthy", "count": 100}
        )
        
        assert response.duplicates["status"] == "healthy"
        assert response.orphans["status"] == "healthy"
        assert response.deleted["status"] == "healthy"
        assert response.embeddings["status"] == "healthy"
    
    def test_health_info_validation(self):
        """Test health info validation."""
        # Valid health info
        response = MaintenanceHealthResponse(
            duplicates={"key": "value"},
            orphans={"key": "value"},
            deleted={"key": "value"},
            embeddings={"key": "value"}
        )
        assert isinstance(response.duplicates, dict)
        
        # Invalid health info type
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            MaintenanceHealthResponse(
                duplicates="not a dict",
                orphans={"key": "value"},
                deleted={"key": "value"},
                embeddings={"key": "value"}
            )


class TestMaintenanceResultsResponse:
    """Test MaintenanceResultsResponse model."""
    
    def test_valid_maintenance_results(self):
        """Test creating a valid maintenance results response."""
        response = MaintenanceResultsResponse(
            duplicates={"found": 5, "removed": 3},
            orphans={"found": 10, "removed": 8},
            deferred_cleanup={"scheduled": 2},
            reindex={"processed": 100}
        )
        
        assert response.duplicates["found"] == 5
        assert response.orphans["found"] == 10
        assert response.deferred_cleanup["scheduled"] == 2
        assert response.reindex["processed"] == 100
    
    def test_maintenance_results_validation(self):
        """Test maintenance results validation."""
        # Valid results
        response = MaintenanceResultsResponse(
            duplicates={"key": "value"},
            orphans={"key": "value"},
            deferred_cleanup={"key": "value"},
            reindex={"key": "value"}
        )
        assert isinstance(response.duplicates, dict)
        
        # Invalid results type
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            MaintenanceResultsResponse(
                duplicates="not a dict",
                orphans={"key": "value"},
                deferred_cleanup={"key": "value"},
                reindex={"key": "value"}
            )


class TestDuplicateCleanupResponse:
    """Test DuplicateCleanupResponse model."""
    
    def test_successful_cleanup(self):
        """Test successful duplicate cleanup response."""
        response = DuplicateCleanupResponse(
            success=True,
            dry_run=False,
            total_duplicates=5,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
            deleted_count=2,
            error=None
        )
        
        assert response.success is True
        assert response.dry_run is False
        assert response.total_duplicates == 5
        assert len(response.deleted_uuids) == 2
        assert response.deleted_count == 2
        assert response.error is None
    
    def test_failed_cleanup(self):
        """Test failed duplicate cleanup response."""
        response = DuplicateCleanupResponse(
            success=False,
            dry_run=True,
            total_duplicates=0,
            deleted_uuids=[],
            deleted_count=0,
            error="Cleanup failed"
        )
        
        assert response.success is False
        assert response.dry_run is True
        assert response.total_duplicates == 0
        assert len(response.deleted_uuids) == 0
        assert response.deleted_count == 0
        assert response.error == "Cleanup failed"
    
    def test_total_duplicates_validation(self):
        """Test total duplicates validation."""
        # Valid count
        response = DuplicateCleanupResponse(
            success=True,
            dry_run=False,
            total_duplicates=0,
            deleted_uuids=[],
            deleted_count=0
        )
        assert response.total_duplicates == 0
        
        # Negative count
        with pytest.raises(ValidationError, match="Total duplicates count must be non-negative"):
            DuplicateCleanupResponse(
                success=True,
                dry_run=False,
                total_duplicates=-1,
                deleted_uuids=[],
                deleted_count=0
            )
    
    def test_deleted_count_validation(self):
        """Test deleted count validation."""
        # Valid count
        response = DuplicateCleanupResponse(
            success=True,
            dry_run=False,
            total_duplicates=2,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
            deleted_count=2
        )
        assert response.deleted_count == 2
        
        # Negative count
        with pytest.raises(ValidationError, match="Deleted count must be non-negative"):
            DuplicateCleanupResponse(
                success=True,
                dry_run=False,
                total_duplicates=2,
                deleted_uuids=["uuid1", "uuid2"],
                deleted_count=-1
            )
    
    def test_deleted_uuids_validation(self):
        """Test deleted UUIDs validation."""
        # Valid UUIDs
        response = DuplicateCleanupResponse(
            success=True,
            dry_run=False,
            total_duplicates=1,
            deleted_uuids=["550e8400-e29b-41d4-a716-446655440001"],
            deleted_count=1
        )
        assert len(response.deleted_uuids) == 1
        
        # Invalid UUID
        with pytest.raises(ValidationError, match="Invalid UUID format"):
            DuplicateCleanupResponse(
                success=True,
                dry_run=False,
                total_duplicates=1,
                deleted_uuids=["invalid-uuid"],
                deleted_count=1
            )
    
    def test_consistency_validation(self):
        """Test consistency validation."""
        # Inconsistent counts
        with pytest.raises(ValidationError, match="Deleted UUIDs count must match deleted_count"):
            DuplicateCleanupResponse(
                success=True,
                dry_run=False,
                total_duplicates=2,
                deleted_uuids=["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"],
                deleted_count=1
            ) 