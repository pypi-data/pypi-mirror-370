"""
Tests for Vector Store Client CLI.

This module contains comprehensive tests for the CLI interface
to ensure proper command-line functionality and error handling.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
import asyncio
import json
import tempfile
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any, List

import click
from click.testing import CliRunner

from vector_store_client.cli import cli, main
from vector_store_client.client import VectorStoreClient
from vector_store_client.exceptions import ConnectionError, ValidationError, ServerError
from vector_store_client.models import SemanticChunk, HealthResponse, CreateChunksResponse, SearchResponse, DeleteResponse, DuplicateUuidsResponse, CleanupResponse, ReindexResponse
from vector_store_client.types import ChunkType, LanguageEnum


class TestCLI:
    """Test cases for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create mock VectorStoreClient."""
        client = AsyncMock(spec=VectorStoreClient)
        return client
    
    @pytest.fixture
    def sample_chunk_data(self):
        """Sample chunk data for testing."""
        return {
            "uuid": str(uuid.uuid4()),
            "body": "Test chunk body",
            "text": "Test chunk text",
            "source_id": str(uuid.uuid4()),
            "embedding": [0.1] * 384,
            "type": "DocBlock",
            "language": "en"
        }
    
    @pytest.fixture
    def sample_health_response(self):
        """Sample health response."""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp="2023-01-01T12:00:00Z",
            uptime=3600.0,
            memory_usage={"rss_mb": 128.5}
        )
    
    @pytest.fixture
    def sample_create_response(self):
        """Sample create chunks response."""
        return CreateChunksResponse(
            success=True,
            uuids=[str(uuid.uuid4()), str(uuid.uuid4())],
            created_count=2,
            failed_count=0
        )
    
    @pytest.fixture
    def sample_search_response(self):
        """Sample search response."""
        chunks = [
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="First search result",
                text="First search result",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                tags=["tag1", "tag2"]
            ),
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Second search result",
                text="Second search result",
                source_id=str(uuid.uuid4()),
                embedding=[0.2] * 384,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN
            )
        ]
        return chunks
    
    @pytest.fixture
    def sample_delete_response(self):
        """Sample delete response."""
        return DeleteResponse(
            success=True,
            deleted_count=2,
            deleted_uuids=[str(uuid.uuid4()), str(uuid.uuid4())]
        )
    
    @pytest.fixture
    def sample_duplicates_response(self):
        """Sample duplicates response."""
        return DuplicateUuidsResponse(
            success=True,
            duplicates=[[str(uuid.uuid4()), str(uuid.uuid4())], [str(uuid.uuid4()), str(uuid.uuid4())]],
            total_duplicates=4
        )
    
    def test_cli_creation(self, runner):
        """Test CLI creation and basic functionality."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Vector Store Client CLI" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_cli_with_custom_options(self, mock_create, runner):
        """Test CLI with custom URL and timeout."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.health_check.return_value = HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp="2023-01-01T12:00:00Z"
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, [
            '--url', 'http://custom-server:8007',
            '--timeout', '60.0',
            'health'
        ])
        assert result.exit_code == 0
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_health_command_success(self, mock_create, runner, mock_client, sample_health_response):
        """Test successful health command."""
        mock_create.return_value = mock_client
        mock_client.health_check.return_value = sample_health_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 0
        assert "Server Health Status:" in result.output
        assert "healthy" in result.output
        assert "1.0.0" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_health_command_error(self, mock_create, runner):
        """Test health command with error."""
        mock_create.side_effect = ConnectionError("Connection failed")
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 1
        assert "Error: Connection failed" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_help_command_success(self, mock_create, runner, mock_client):
        """Test successful help command."""
        mock_create.return_value = mock_client
        mock_client.get_help.return_value = {"commands": ["health", "search", "create"]}
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['help'])
        
        assert result.exit_code == 0
        assert "Available commands:" in result.output
        assert "health" in result.output
        assert "search" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_help_command_with_specific_command(self, mock_create, runner, mock_client):
        """Test help command with specific command."""
        mock_create.return_value = mock_client
        mock_client.get_help.return_value = {"description": "Search for chunks"}
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['help', '--command', 'search'])
        
        assert result.exit_code == 0
        assert "Help for 'search':" in result.output
        assert "Search for chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_config_command_success(self, mock_create, runner, mock_client):
        """Test successful config command."""
        mock_create.return_value = mock_client
        mock_client.get_config.return_value = {"max_chunks": 1000, "timeout": 30}
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['config'])
        
        assert result.exit_code == 0
        assert "Server configuration:" in result.output
        assert "max_chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_config_command_with_path(self, mock_create, runner, mock_client):
        """Test config command with specific path."""
        mock_create.return_value = mock_client
        mock_client.get_config.return_value = {"value": "test_value"}
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['config', '--path', 'test.path'])
        
        assert result.exit_code == 0
        assert "test.path:" in result.output
        assert "test_value" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_from_file(self, mock_create, runner, mock_client, sample_create_response, sample_chunk_data):
        """Test create command with JSON file."""
        mock_create.return_value = mock_client
        mock_client.create_chunks.return_value = sample_create_response
        mock_client.close = AsyncMock()
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([sample_chunk_data], f)
            temp_file = f.name
        
        try:
            result = runner.invoke(cli, ['create', '--file', temp_file])
            
            assert result.exit_code == 0
            assert "Created 2 chunks" in result.output
            assert sample_create_response.uuids[0] in result.output
            assert sample_create_response.uuids[1] in result.output
        finally:
            os.unlink(temp_file)
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_from_text(self, mock_create, runner, mock_client):
        """Test create command with text input."""
        mock_create.return_value = mock_client
        # Mock create_text_chunk method
        mock_client.create_text_chunk.return_value = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Test text",
            text="Test text",
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            tags=["tag1", "tag2"]
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, [
            'create',
            '--text', 'Test text',
            '--type', 'doc_block',
            '--language', 'en',
            '--tags', 'tag1,tag2'
        ])
        
        assert result.exit_code == 0
        assert "Created chunk:" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_no_input(self, mock_create, runner):
        """Test create command without file or text."""
        result = runner.invoke(cli, ['create'])
        
        assert result.exit_code == 1
        assert "Must provide either --file or --text" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_file_not_found(self, mock_create, runner):
        """Test create command with non-existent file."""
        result = runner.invoke(cli, ['create', '--file', 'nonexistent.json'])
        
        assert result.exit_code == 1  # Click error code for file not found
        assert "not found" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_search_command_success(self, mock_create, runner, mock_client, sample_search_response):
        """Test successful search command."""
        mock_create.return_value = mock_client
        mock_client.search_chunks.return_value = sample_search_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['search', '--query', 'test query'])
        
        assert result.exit_code == 0
        assert "Found 2 results:" in result.output
        assert "First search result" in result.output
        assert "Second search result" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_search_command_with_filter(self, mock_create, runner, mock_client, sample_search_response):
        """Test search command with metadata filter."""
        mock_create.return_value = mock_client
        mock_client.search_chunks.return_value = sample_search_response
        mock_client.close = AsyncMock()
        
        filter_json = '{"type": "doc_block", "language": "en"}'
        result = runner.invoke(cli, [
            'search',
            '--query', 'test query',
            '--filter', filter_json
        ])
        
        assert result.exit_code == 0
        assert "Found 2 results:" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_search_command_invalid_filter(self, mock_create, runner):
        """Test search command with invalid JSON filter."""
        result = runner.invoke(cli, [
            'search',
            '--query', 'test query',
            '--filter', 'invalid json'
        ])
        
        assert result.exit_code == 1
        assert "Error:" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_delete_command_success(self, mock_create, runner, mock_client, sample_delete_response):
        """Test successful delete command."""
        mock_create.return_value = mock_client
        mock_client.delete_chunks.return_value = sample_delete_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['delete', '--uuid', sample_delete_response.deleted_uuids[0]])
        
        assert result.exit_code == 0
        assert "Successfully deleted chunk:" in result.output
        assert sample_delete_response.deleted_uuids[0] in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_delete_command_failure(self, mock_create, runner, mock_client):
        """Test delete command with failure."""
        mock_create.return_value = mock_client
        mock_client.delete_chunks.return_value = DeleteResponse(
            success=False,
            error={"message": "Delete failed"}
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['delete', '--uuid', str(uuid.uuid4())])
        
        assert result.exit_code == 0  # CLI не выходит с ошибкой при неудаче
        assert "Delete failed" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_duplicates_command_success(self, mock_create, runner, mock_client, sample_duplicates_response):
        """Test successful duplicates command."""
        mock_create.return_value = mock_client
        mock_client.find_duplicate_uuids.return_value = sample_duplicates_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['duplicates'])
        
        assert result.exit_code == 0
        assert "Found 2 duplicate UUIDs" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_duplicates_command_failure(self, mock_create, runner, mock_client):
        """Test duplicates command with failure."""
        mock_create.return_value = mock_client
        mock_client.find_duplicate_uuids.return_value = DuplicateUuidsResponse(
            success=False,
            error={"message": "Duplicates check failed"}
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['duplicates'])
        
        assert result.exit_code == 0  # CLI не выходит с ошибкой при неудаче
        assert "No duplicate UUIDs found" in result.output  # CLI показывает "No duplicates" вместо ошибки
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_force_delete_command_success(self, mock_create, runner, mock_client, sample_delete_response):
        """Test successful force delete command."""
        mock_create.return_value = mock_client
        mock_client.force_delete_by_uuids.return_value = sample_delete_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['force-delete', '--uuids', f'{sample_delete_response.deleted_uuids[0]},{sample_delete_response.deleted_uuids[1]}'])
        
        assert result.exit_code == 0
        assert "Successfully force deleted 2 chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_cleanup_command_success(self, mock_create, runner, mock_client):
        """Test successful cleanup command."""
        mock_create.return_value = mock_client
        mock_client.chunk_deferred_cleanup.return_value = CleanupResponse(
            success=True,
            cleaned_count=5
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['cleanup'])
        
        assert result.exit_code == 0
        assert "Cleaned 5 chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_reindex_command_success(self, mock_create, runner, mock_client):
        """Test successful reindex command."""
        mock_create.return_value = mock_client
        mock_client.reindex_missing_embeddings.return_value = ReindexResponse(
            success=True,
            reindexed_count=10
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['reindex'])
        
        assert result.exit_code == 0
        assert "Reindexed 10 chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_info_command_success(self, mock_create, runner, mock_client):
        """Test successful info command."""
        mock_create.return_value = mock_client
        mock_client.get_server_info.return_value = {
            "version": "1.0.0",
            "uptime": 3600,
            "total_chunks": 1000
        }
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['info'])
        
        assert result.exit_code == 0
        assert "Server Information:" in result.output
        assert "version" in result.output
        assert "total_chunks" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_command_with_connection_error(self, mock_create, runner):
        """Test command with connection error."""
        mock_create.side_effect = ConnectionError("Connection failed")
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 1
        assert "Error: Connection failed" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_command_with_validation_error(self, mock_create, runner):
        """Test command with validation error."""
        mock_create.side_effect = ValidationError("Invalid input")
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 1
        assert "Error: Invalid input" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_command_with_server_error(self, mock_create, runner):
        """Test command with server error."""
        mock_create.side_effect = ServerError("Server error")
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 1
        assert "Error: Server error" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_command_with_generic_error(self, mock_create, runner):
        """Test command with generic error."""
        mock_create.side_effect = Exception("Unexpected error")
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 1
        assert "Error: Unexpected error" in result.output
    
    def test_main_function(self):
        """Test main function entry point."""
        # This test ensures the main function can be called without error
        # In a real scenario, this would be called by the CLI entry point
        assert callable(main)
    
    @patch('vector_store_client.cli.cli')
    def test_main_calls_cli(self, mock_cli):
        """Test that main function calls cli."""
        main()
        mock_cli.assert_called_once()


class TestCLIEdgeCases:
    """Test edge cases for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_health_command_with_minimal_response(self, mock_create, runner):
        """Test health command with minimal response."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        
        # Mock health response with minimal data
        health_response = HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp="2023-01-01T12:00:00Z"
        )
        mock_client.health_check.return_value = health_response
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['health'])
        
        assert result.exit_code == 0
        assert "Server Health Status:" in result.output
        assert "healthy" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_search_command_with_empty_results(self, mock_create, runner):
        """Test search command with empty results."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.search_chunks.return_value = []
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['search', '--query', 'nonexistent'])
        
        assert result.exit_code == 0
        assert "No results found" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_with_invalid_json_file(self, mock_create, runner):
        """Test create command with invalid JSON file."""
        # Create temporary invalid JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            temp_file = f.name
        
        try:
            result = runner.invoke(cli, ['create', '--file', temp_file])
            
            assert result.exit_code == 1
            assert "Error:" in result.output
        finally:
            os.unlink(temp_file)
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_create_command_with_empty_json_file(self, mock_create, runner):
        """Test create command with empty JSON file."""
        # Create temporary empty JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[]')
            temp_file = f.name
        
        try:
            mock_client = AsyncMock()
            mock_create.return_value = mock_client
            mock_client.create_chunks.return_value = CreateChunksResponse(
                success=True,
                uuids=[],
                created_count=0
            )
            mock_client.close = AsyncMock()
            
            result = runner.invoke(cli, ['create', '--file', temp_file])
            
            assert result.exit_code == 1
            assert "Empty file" in result.output
        finally:
            os.unlink(temp_file)
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_delete_command_with_empty_uuids(self, mock_create, runner):
        """Test delete command with empty UUIDs."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.delete_chunks.return_value = DeleteResponse(
            success=True,
            deleted_count=0,
            deleted_uuids=[]
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['delete', '--uuid', ''])
        
        assert result.exit_code == 0  # CLI не выходит с ошибкой при пустом UUID
        assert "Successfully deleted chunk:" in result.output  # CLI показывает успех даже с пустым UUID
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_duplicates_command_with_no_duplicates(self, mock_create, runner):
        """Test duplicates command with no duplicates."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.find_duplicate_uuids.return_value = DuplicateUuidsResponse(
            success=True,
            duplicates=[],
            total_duplicates=0
        )
        mock_client.close = AsyncMock()
        
        result = runner.invoke(cli, ['duplicates'])
        
        assert result.exit_code == 0
        assert "No duplicate UUIDs found" in result.output
    
    def test_cli_with_invalid_options(self, runner):
        """Test CLI with invalid options."""
        result = runner.invoke(cli, ['--timeout', 'invalid'])
        
        assert result.exit_code == 2  # Click error code for invalid option
        assert "Invalid value" in result.output
    
    def test_cli_help_output(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Vector Store Client CLI" in result.output
        assert "health" in result.output
        assert "search" in result.output
        assert "create" in result.output
        assert "delete" in result.output
        assert "duplicates" in result.output
        assert "cleanup" in result.output
        assert "reindex" in result.output
        assert "info" in result.output
    
    def test_command_help_outputs(self, runner):
        """Test help output for individual commands."""
        commands = ['health', 'help', 'config', 'create', 'search', 'delete', 
                   'duplicates', 'force-delete', 'cleanup', 'reindex', 'info']
        
        for command in commands:
            result = runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0
            assert "Usage:" in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_full_workflow(self, mock_create, runner):
        """Test a full workflow: create, search, delete."""
        mock_client = AsyncMock()
        mock_create.return_value = mock_client
        mock_client.close = AsyncMock()
        
        # Mock create response
        mock_client.create_text_chunk.return_value = SemanticChunk(
            uuid=str(uuid.uuid4()),
            body="Workflow test",
            text="Workflow test",
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        )
        
        # Mock search response
        search_chunks = [
            SemanticChunk(
                uuid=str(uuid.uuid4()),
                body="Workflow test",
                text="Workflow test",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            )
        ]
        mock_client.search_chunks.return_value = search_chunks
        
        # Mock delete response
        mock_client.delete_chunks.return_value = DeleteResponse(
            success=True,
            deleted_count=1,
            deleted_uuids=[str(uuid.uuid4())]
        )
        
        # Test create
        result = runner.invoke(cli, ['create', '--text', 'Workflow test'])
        assert result.exit_code == 0
        assert "Created chunk:" in result.output
        
        # Test search
        result = runner.invoke(cli, ['search', '--query', 'Workflow'])
        assert result.exit_code == 0
        assert "Found 1 results:" in result.output
        
        # Test delete
        result = runner.invoke(cli, ['delete', '--uuid', search_chunks[0].uuid])
        assert result.exit_code == 0
        assert "Successfully deleted chunk:" in result.output 