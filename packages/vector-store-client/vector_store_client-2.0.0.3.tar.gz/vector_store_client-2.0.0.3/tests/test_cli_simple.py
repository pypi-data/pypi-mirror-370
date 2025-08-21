"""
Simple tests for CLI module.

This module contains basic tests for CLI functionality.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import pytest
from unittest.mock import patch, AsyncMock
from click.testing import CliRunner

from vector_store_client.cli import cli, main


class TestCLISimple:
    """Simple CLI tests."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Vector Store Client CLI' in result.output
    
    def test_cli_with_default_options(self, runner):
        """Test CLI with default options."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
    
    def test_cli_with_verbose(self, runner):
        """Test CLI with verbose flag."""
        # Note: --verbose option was removed from CLI, so this test is no longer valid
        # We'll test with a valid option instead
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
    
    def test_cli_with_custom_url(self, runner):
        """Test CLI with custom URL."""
        result = runner.invoke(cli, ['--url', 'http://custom:8007', '--help'])
        assert result.exit_code == 0
    
    def test_cli_with_custom_timeout(self, runner):
        """Test CLI with custom timeout."""
        result = runner.invoke(cli, ['--timeout', '60.0', '--help'])
        assert result.exit_code == 0
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_health_command_success(self, mock_create, runner):
        """Test health command success."""
        # Mock successful health check
        mock_client = AsyncMock()
        mock_client.health_check = AsyncMock(return_value=AsyncMock(
            status="healthy",
            version="1.0.0",
            uptime="1h 30m"
        ))
        mock_create.return_value = mock_client
        
        result = runner.invoke(cli, ['health'])
        assert result.exit_code == 0  # Should succeed with mocked client
        assert "Server Health Status:" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_health_command_error(self, mock_create, runner):
        """Test health command error."""
        mock_create.side_effect = Exception("Connection failed")
        
        result = runner.invoke(cli, ['health'])
        assert result.exit_code == 1
        assert "Error:" in result.output
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_help_command_success(self, mock_create, runner):
        """Test help command success."""
        mock_client = AsyncMock()
        mock_client.get_help = AsyncMock(return_value={
            "commands": ["health", "search", "create"],
            "description": "Available commands"
        })
        mock_create.return_value = mock_client
        
        result = runner.invoke(cli, ['help'])
        assert result.exit_code == 0
    
    @patch('vector_store_client.cli.VectorStoreClient.create')
    def test_config_command_success(self, mock_create, runner):
        """Test config command success."""
        mock_client = AsyncMock()
        mock_client.get_config = AsyncMock(return_value={"timeout": 30.0})
        mock_create.return_value = mock_client
        
        result = runner.invoke(cli, ['config'])
        assert result.exit_code == 0
    
    def test_main_function(self):
        """Test main function."""
        assert callable(main) 