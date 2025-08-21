"""
Error handling examples for Vector Store Client.

This module demonstrates comprehensive error handling patterns
and best practices for using the Vector Store client.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
)
from vector_store_client.exceptions import (
    VectorStoreError,
    ConnectionError,
    ValidationError,
    JsonRpcError,
    ServerError,
    NotFoundError,
    DuplicateError,
)
from vector_store_client.utils import setup_logging, retry_with_backoff


async def comprehensive_error_handling_example():
    """
    Demonstrate comprehensive error handling for all operation types.
    """
    print("=== Comprehensive Error Handling Example ===")
    
    # Setup detailed logging for debugging
    logger = setup_logging(level="DEBUG")
    
    try:
        client = await VectorStoreClient.create("http://localhost:8007", logger=logger)
        
        # Test various error scenarios
        await test_connection_errors(client)
        await test_validation_errors(client)
        await test_server_errors(client)
        await test_json_rpc_errors(client)
        await test_not_found_errors(client)
        await test_duplicate_errors(client)
        
    except Exception as e:
        print(f"Unexpected error in main: {e}")
        logger.exception("Unexpected error")
    finally:
        if 'client' in locals():
            await client.close()


async def test_connection_errors(client: VectorStoreClient):
    """Test connection-related error handling."""
    print("\n--- Connection Error Handling ---")
    
    # Test connection to non-existent server
    try:
        print("Testing connection to non-existent server...")
        bad_client = await VectorStoreClient.create("http://localhost:9999")
        await bad_client.health_check()
    except ConnectionError as e:
        print(f"✓ ConnectionError caught: {e}")
        print(f"  Base URL: {e.base_url}")
        print(f"  Timeout: {e.timeout}")
        print(f"  Retry count: {e.retry_count}")
        if e.original_error:
            print(f"  Original error: {e.original_error}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test timeout scenarios
    try:
        print("Testing timeout scenario...")
        timeout_client = await VectorStoreClient.create("http://localhost:8007", timeout=0.001)
        await timeout_client.health_check()
    except ConnectionError as e:
        print(f"✓ Timeout error caught: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_validation_errors(client: VectorStoreClient):
    """Test validation error handling."""
    print("\n--- Validation Error Handling ---")
    
    # Test invalid chunk creation
    try:
        print("Testing invalid chunk (empty text)...")
        invalid_chunk = SemanticChunk(
            body="",
            text="",
            type=ChunkType.DOC_BLOCK
        )
        await client.create_chunks([invalid_chunk])
    except ValidationError as e:
        print(f"✓ ValidationError caught: {e}")
        print(f"  Field errors: {e.field_errors}")
        print(f"  Data: {e.data}")
        print(f"  Validation rules: {e.validation_rules}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid search parameters
    try:
        print("Testing invalid search parameters...")
        await client.search_chunks(limit=-1)
    except ValidationError as e:
        print(f"✓ Search validation error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid embedding dimensions
    try:
        print("Testing invalid embedding dimensions...")
        invalid_embedding_chunk = SemanticChunk(
            body="Test content",
            text="Test content",
            type=ChunkType.DOC_BLOCK,
            embedding=[0.1, 0.2, 0.3]  # Wrong dimension
        )
        await client.create_chunks([invalid_embedding_chunk])
    except ValidationError as e:
        print(f"✓ Embedding validation error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_server_errors(client: VectorStoreClient):
    """Test server error handling."""
    print("\n--- Server Error Handling ---")
    
    # Test invalid command
    try:
        print("Testing invalid command...")
        await client._execute_command("invalid_command_that_does_not_exist")
    except ServerError as e:
        print(f"✓ ServerError caught: {e}")
        print(f"  Status code: {e.status_code}")
        print(f"  Server message: {e.server_message}")
        print(f"  Server error code: {e.server_error_code}")
        print(f"  Response data: {e.response_data}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test server configuration errors
    try:
        print("Testing invalid configuration path...")
        await client.get_config("invalid.config.path.that.does.not.exist")
    except ServerError as e:
        print(f"✓ Configuration error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_json_rpc_errors(client: VectorStoreClient):
    """Test JSON-RPC error handling."""
    print("\n--- JSON-RPC Error Handling ---")
    
    # Test malformed request
    try:
        print("Testing malformed JSON-RPC request...")
        # This would require accessing internal methods or simulating malformed requests
        # For demonstration, we'll test with invalid parameters
        await client._execute_command("health", {"invalid": "parameters"})
    except JsonRpcError as e:
        print(f"✓ JsonRpcError caught: {e}")
        print(f"  Method: {e.method}")
        print(f"  Error code: {e.error_code}")
        print(f"  Error data: {e.error_data}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_not_found_errors(client: VectorStoreClient):
    """Test not found error handling."""
    print("\n--- Not Found Error Handling ---")
    
    # Test searching for non-existent content
    try:
        print("Testing search for non-existent content...")
        results = await client.search_chunks(
            search_str="this_content_definitely_does_not_exist_in_any_chunk",
            limit=1
        )
        if not results:
            print("✓ No results found (expected behavior)")
        else:
            print("✗ Unexpected results found")
    except NotFoundError as e:
        print(f"✓ NotFoundError caught: {e}")
        print(f"  Resource type: {e.resource_type}")
        print(f"  Resource ID: {e.resource_id}")
        print(f"  Search criteria: {e.search_criteria}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_duplicate_errors(client: VectorStoreClient):
    """Test duplicate error handling."""
    print("\n--- Duplicate Error Handling ---")
    
    # Create a chunk first
    try:
        print("Creating initial chunk...")
        chunk = SemanticChunk(
            body="Test content for duplicate detection",
            text="Test content for duplicate detection",
            type=ChunkType.DOC_BLOCK,
            uuid="test-uuid-12345-67890-abcdef"  # Fixed UUID
        )
        await client.create_chunks([chunk])
        print("✓ Initial chunk created")
        
        # Try to create duplicate
        print("Attempting to create duplicate chunk...")
        duplicate_chunk = SemanticChunk(
            body="Duplicate content",
            text="Duplicate content",
            type=ChunkType.DOC_BLOCK,
            uuid="test-uuid-12345-67890-abcdef"  # Same UUID
        )
        await client.create_chunks([duplicate_chunk])
    except DuplicateError as e:
        print(f"✓ DuplicateError caught: {e}")
        print(f"  Resource type: {e.resource_type}")
        print(f"  Resource ID: {e.resource_id}")
        print(f"  Existing resource: {e.existing_resource}")
        print(f"  Conflict fields: {e.conflict_fields}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def retry_pattern_example():
    """
    Demonstrate retry patterns for handling transient errors.
    """
    print("\n=== Retry Pattern Example ===")
    
    # Define operation that might fail
    async def unreliable_operation(attempt: int = 0):
        """Simulate an unreliable operation."""
        import random
        
        # Simulate different failure scenarios
        failure_chance = 0.8 if attempt < 2 else 0.1  # More likely to fail early
        
        if random.random() < failure_chance:
            error_type = random.choice([
                ConnectionError("Simulated connection error", "http://localhost:8007", 30.0),
                ServerError("Simulated server error", 500, {}, "Internal server error"),
                JsonRpcError("Simulated JSON-RPC error", "test_method")
            ])
            raise error_type
        
        return f"Operation succeeded on attempt {attempt + 1}"
    
    # Test retry with different strategies
    print("Testing retry with exponential backoff...")
    
    try:
        result = await retry_with_backoff(
            unreliable_operation,
            max_retries=5,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            exceptions=(ConnectionError, ServerError, JsonRpcError)
        )
        print(f"✓ Retry successful: {result}")
    except Exception as e:
        print(f"✗ Retry failed: {e}")


async def graceful_degradation_example():
    """
    Demonstrate graceful degradation when services are unavailable.
    """
    print("\n=== Graceful Degradation Example ===")
    
    async def robust_operation():
        """Perform operation with graceful degradation."""
        try:
            # Try primary operation
            client = await VectorStoreClient.create("http://localhost:8007")
            health = await client.health_check()
            await client.close()
            return f"Primary operation successful: {health.status}"
            
        except ConnectionError:
            print("Primary service unavailable, using fallback...")
            return "Fallback operation completed"
            
        except ServerError as e:
            if e.status_code >= 500:
                print("Server error, using cached data...")
                return "Using cached data"
            else:
                raise  # Re-raise client errors
    
    try:
        result = await robust_operation()
        print(f"✓ Operation result: {result}")
    except Exception as e:
        print(f"✗ Operation failed: {e}")


async def error_recovery_example():
    """
    Demonstrate error recovery strategies.
    """
    print("\n=== Error Recovery Example ===")
    
    async def recoverable_operation():
        """Perform operation with recovery strategies."""
        client = None
        try:
            # Attempt operation
            client = await VectorStoreClient.create("http://localhost:8007")
            
            # Create chunks
            chunks = [
                SemanticChunk(
                    body=f"Recovery test chunk {i}",
                    text=f"Recovery test chunk {i}",
                    type=ChunkType.DOC_BLOCK
                )
                for i in range(5)
            ]
            
            result = await client.create_chunks(chunks)
            return f"Successfully created {result.created_count} chunks"
            
        except ValidationError as e:
            print(f"Validation error, attempting to fix data...")
            # Try to fix validation issues
            fixed_chunks = []
            for chunk in chunks:
                if not chunk.body or not chunk.text:
                    chunk.body = "Default content"
                    chunk.text = "Default content"
                fixed_chunks.append(chunk)
            
            result = await client.create_chunks(fixed_chunks)
            return f"Recovered and created {result.created_count} chunks"
            
        except ConnectionError as e:
            print(f"Connection error, attempting reconnection...")
            # Try to reconnect
            await asyncio.sleep(1)
            client = await VectorStoreClient.create("http://localhost:8007")
            
            result = await client.create_chunks(chunks)
            return f"Reconnected and created {result.created_count} chunks"
            
        except ServerError as e:
            if e.status_code == 429:  # Rate limit
                print("Rate limited, waiting before retry...")
                await asyncio.sleep(5)
                result = await client.create_chunks(chunks)
                return f"Rate limit recovered, created {result.created_count} chunks"
            else:
                raise
                
        finally:
            if client:
                await client.close()
    
    try:
        result = await recoverable_operation()
        print(f"✓ Recovery result: {result}")
    except Exception as e:
        print(f"✗ Recovery failed: {e}")


async def logging_and_monitoring_example():
    """
    Demonstrate logging and monitoring for error tracking.
    """
    print("\n=== Logging and Monitoring Example ===")
    
    # Setup comprehensive logging
    logger = setup_logging(
        level="DEBUG",
        format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_file="vector_store_errors.log"
    )
    
    # Add custom error tracking
    error_count = 0
    error_types = {}
    
    async def monitored_operation():
        """Perform operation with error monitoring."""
        nonlocal error_count, error_types
        
        try:
            client = await VectorStoreClient.create("http://localhost:8007", logger=logger)
            
            # Perform various operations
            await client.health_check()
            await client.get_help()
            
            # Simulate some errors
            await client.search_chunks(limit=-1)  # Should fail validation
            
        except ValidationError as e:
            error_count += 1
            error_types['ValidationError'] = error_types.get('ValidationError', 0) + 1
            logger.warning(f"Validation error #{error_count}: {e}")
            raise
            
        except ConnectionError as e:
            error_count += 1
            error_types['ConnectionError'] = error_types.get('ConnectionError', 0) + 1
            logger.error(f"Connection error #{error_count}: {e}")
            raise
            
        except Exception as e:
            error_count += 1
            error_types['Other'] = error_types.get('Other', 0) + 1
            logger.exception(f"Unexpected error #{error_count}: {e}")
            raise
            
        finally:
            if 'client' in locals():
                await client.close()
    
    try:
        await monitored_operation()
    except Exception:
        pass  # Expected to fail
    
    # Report error statistics
    print(f"Error monitoring results:")
    print(f"  Total errors: {error_count}")
    print(f"  Error types: {error_types}")


async def main():
    """Run all error handling examples."""
    print("Vector Store Client - Error Handling Examples")
    print("=" * 50)
    
    try:
        await comprehensive_error_handling_example()
        await retry_pattern_example()
        await graceful_degradation_example()
        await error_recovery_example()
        await logging_and_monitoring_example()
        
        print("\nAll error handling examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 