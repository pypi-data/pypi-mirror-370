"""
Phase 6: Optimization and Expansion Examples.

This module provides comprehensive examples of the new optimization
features including streaming, bulk operations, backup/restore, and monitoring.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import tempfile
import uuid
from typing import List, Dict, Any
from datetime import datetime

from ..client import VectorStoreClient
from ..models import SemanticChunk
from ..plugins import (
    TextPreprocessorPlugin, EmbeddingOptimizerPlugin, 
    MetadataEnricherPlugin, QualityCheckerPlugin
)
from ..middleware import (
    LoggingMiddleware, CachingMiddleware, 
    RetryMiddleware, MetricsMiddleware
)


async def example_streaming_large_datasets():
    """
    Example: Streaming large datasets efficiently.
    
    Demonstrates how to process large datasets without loading
    everything into memory at once.
    """
    print("=== Streaming Large Datasets Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Stream chunks in batches
        total_processed = 0
        async for batch in client.stream_chunks(
            batch_size=1000
        ):
            # Process each batch
            for chunk in batch:
                # Do something with each chunk
                if chunk.body:
                    processed_text = chunk.body.upper()
                    # Process the text...
            
            total_processed += len(batch)
            print(f"Processed batch of {len(batch)} chunks. Total: {total_processed}")
        
        print(f"Finished processing {total_processed} chunks")
        
    except Exception as e:
        print(f"Error during streaming: {e}")


async def example_bulk_operations():
    """
    Example: Bulk operations with progress tracking.
    
    Demonstrates bulk creation and deletion with progress callbacks.
    """
    print("=== Bulk Operations Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Create test chunks with valid UUIDs
        test_chunks = [
            SemanticChunk(
                body=f"Test chunk {i}",
                text=f"Test chunk {i}",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            )
            for i in range(100)
        ]
        
        # Progress callback
        def progress_callback(progress: float):
            print(f"Progress: {progress:.1%}")
        
        # Bulk create chunks
        print("Creating chunks in bulk...")
        create_result = await client.bulk_create_chunks(
            chunks=test_chunks,
            batch_size=20,
            progress_callback=progress_callback
        )
        
        print(f"Created {create_result['created_count']} chunks")
        print(f"Failed {create_result['failed_count']} chunks")
        
        # Bulk delete chunks
        print("Deleting chunks in bulk...")
        try:
            # Get chunks to delete
            chunks_to_delete = await client.search_chunks(limit=10)
            if chunks_to_delete:
                chunk_uuids = [chunk.uuid for chunk in chunks_to_delete]
                delete_result = await client.delete_chunks(uuids=chunk_uuids)
                print(f"Deleted {delete_result.deleted_count} chunks")
            else:
                print("No chunks found to delete")
        except Exception as e:
            print(f"Bulk delete failed: {e}")
        
    except Exception as e:
        print(f"Error during bulk operations: {e}")


async def example_backup_and_restore():
    """
    Example: Backup and restore functionality.
    
    Demonstrates creating backups and restoring data.
    """
    print("=== Backup and Restore Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Create some test data with valid UUIDs
        test_chunks = [
            SemanticChunk(
                body=f"Backup test chunk {i}",
                text=f"Backup test chunk {i}",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            )
            for i in range(10)
        ]
        
        # Create chunks
        await client.create_chunks(test_chunks)
        
        # Export chunks (simulate backup)
        print("Exporting chunks (simulating backup)...")
        try:
            # Search for chunks to export
            chunks_to_export = await client.search_chunks(
                metadata_filter={"source_id": "backup-test"},
                limit=10
            )
            
            if chunks_to_export:
                print(f"Found {len(chunks_to_export)} chunks to export")
                
                # Export chunks data
                export_data = []
                for chunk in chunks_to_export:
                    export_data.append(chunk.model_dump())
                
                print(f"Exported {len(export_data)} chunks")
                print(f"Export data size: {len(str(export_data))} characters")
                
                # Simulate import (validate data)
                print("Validating exported data...")
                valid_count = 0
                for chunk_data in export_data:
                    try:
                        # Validate chunk data
                        SemanticChunk(**chunk_data)
                        valid_count += 1
                    except Exception as e:
                        print(f"Validation error: {e}")
                
                print(f"Validated {valid_count} chunks")
                print(f"Validation errors: {len(export_data) - valid_count}")
                
            else:
                print("No chunks found for export")
                
        except Exception as e:
            print(f"Export failed: {e}")
        
    except Exception as e:
        print(f"Error during backup/restore: {e}")


async def example_data_migration():
    """
    Example: Data migration between clients.
    
    Demonstrates migrating data from one vector store to another.
    """
    print("=== Data Migration Example ===")
    
    # Initialize source and target clients
    source_client = VectorStoreClient("http://localhost:8007")
    target_client = VectorStoreClient("http://localhost:8007")  # Same server for demo
    
    try:
        # Progress callback
        def migration_progress(migrated_count: int):
            print(f"Migrated {migrated_count} chunks")
        
        # Get chunks from source
        print("Getting chunks from source...")
        source_chunks = await source_client.search_chunks(
            metadata_filter={"source_id": "migration-test"},
            limit=10
        )
        
        if source_chunks:
            print(f"Found {len(source_chunks)} chunks to migrate")
            
            # Migrate data (copy to target)
            migrated_count = 0
            errors = 0
            
            for chunk in source_chunks:
                try:
                    # Create new chunk in target with modified source_id
                    new_chunk = SemanticChunk(
                        body=chunk.body,
                        text=chunk.text,
                        source_id=f"{chunk.source_id}-migrated",
                        embedding=chunk.embedding,
                        type=chunk.type,
                        language=chunk.language,
                        category=chunk.category,
                        title=f"{chunk.title} (Migrated)"
                    )
                    
                    result = await target_client.create_chunks([new_chunk])
                    if result.success:
                        migrated_count += 1
                        migration_progress(migrated_count)
                    else:
                        errors += 1
                        
                except Exception as e:
                    print(f"Error migrating chunk {chunk.uuid}: {e}")
                    errors += 1
            
            print(f"Migration completed:")
            print(f"  Total migrated: {migrated_count}")
            print(f"  Total errors: {errors}")
            print(f"  Success: {migrated_count > 0}")
        else:
            print("No chunks found for migration")
        
    except Exception as e:
        print(f"Error during migration: {e}")


async def example_performance_monitoring():
    """
    Example: Performance monitoring and metrics.
    
    Demonstrates collecting and analyzing performance metrics.
    """
    print("=== Performance Monitoring Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Get server info
        server_info = await client.get_server_info()
        
        print("Server Information:")
        for key, value in server_info.items():
            print(f"  {key}: {value}")
        
        # Get chunk statistics
        stats = await client.get_chunk_statistics()
        
        print("\nChunk Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Monitor search operation with timing
        print("\nMonitoring search operation...")
        import time
        
        start_time = time.time()
        search_results = await client.search_chunks(
            search_str="test",
            limit=5
        )
        search_time = time.time() - start_time
        
        print(f"  Operation: search")
        print(f"  Execution Time: {search_time:.3f}s")
        print(f"  Results Found: {len(search_results)}")
        
        # Monitor create operation with timing
        print("\nMonitoring create operation...")
        test_chunk = SemanticChunk(
            body="Performance test chunk",
            text="Performance test chunk",
            source_id="perf-test",
            embedding=[0.1] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN
        )
        
        start_time = time.time()
        create_result = await client.create_chunks([test_chunk])
        create_time = time.time() - start_time
        
        print(f"  Operation: create")
        print(f"  Execution Time: {create_time:.3f}s")
        print(f"  Chunks Created: {create_result.created_count}")
        
        # Performance comparison
        print(f"\nPerformance Summary:")
        print(f"  Search: {search_time:.3f}s for {len(search_results)} results")
        print(f"  Create: {create_time:.3f}s for {create_result.created_count} chunks")
        print(f"  Search efficiency: {len(search_results)/search_time:.1f} results/second")
        print(f"  Create efficiency: {create_result.created_count/create_time:.1f} chunks/second")
        
    except Exception as e:
        print(f"Error during performance monitoring: {e}")


async def example_fallback_strategies():
    """
    Example: Fallback strategies for reliability.
    
    Demonstrates using fallback strategies for improved reliability.
    """
    print("=== Fallback Strategies Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Search with fallback strategy (simulated)
        print("Trying primary search...")
        try:
            primary_results = await client.search_chunks(
                search_str="primary query",
                limit=10,
                level_of_relevance=0.8
            )
            print(f"Primary search successful: {len(primary_results)} results")
            results = primary_results
        except Exception as e:
            print(f"Primary search failed: {e}")
            print("Trying fallback search...")
            
            try:
                fallback_results = await client.search_chunks(
                    search_str="fallback query",
                    limit=20,
                    level_of_relevance=0.5
                )
                print(f"Fallback search successful: {len(fallback_results)} results")
                results = fallback_results
            except Exception as e2:
                print(f"Fallback search also failed: {e2}")
                results = []
        
        print(f"Final search completed with {len(results)} results")
        
        # Create with retry logic (simulated)
        test_chunk = SemanticChunk(
            body="Test chunk with retry",
            text="Test chunk with retry",
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN
        )
        
        max_retries = 3
        retry_count = 0
        create_success = False
        
        while retry_count < max_retries and not create_success:
            try:
                create_result = await client.create_chunks([test_chunk])
                if create_result.success:
                    print(f"Chunk created successfully after {retry_count + 1} attempts")
                    print(f"  Created UUIDs: {create_result.uuids}")
                    create_success = True
                else:
                    retry_count += 1
                    print(f"Create failed, retry {retry_count}/{max_retries}")
            except Exception as e:
                retry_count += 1
                print(f"Create error, retry {retry_count}/{max_retries}: {e}")
        
        if not create_success:
            print(f"Chunk creation failed after {max_retries} retries")
        
    except Exception as e:
        print(f"Error during fallback strategies: {e}")


async def example_plugin_usage():
    """
    Example: Using plugins for enhanced functionality.
    
    Demonstrates using the plugin system for text preprocessing,
    embedding optimization, metadata enrichment, and quality checking.
    """
    print("=== Plugin Usage Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Initialize plugins
        text_preprocessor = TextPreprocessorPlugin({
            "remove_html": True,
            "normalize_whitespace": True,
            "lowercase": False
        })
        
        embedding_optimizer = EmbeddingOptimizerPlugin({
            "normalize_vectors": True,
            "check_quality": True,
            "min_quality_score": 0.5
        })
        
        metadata_enricher = MetadataEnricherPlugin({
            "auto_generate_metadata": True,
            "detect_language": True,
            "extract_keywords": True
        })
        
        quality_checker = QualityCheckerPlugin({
            "check_content_quality": True,
            "check_embedding_quality": True,
            "filter_low_quality": False
        })
        
        # Register plugins
        client.register_plugin("text_preprocessor", text_preprocessor)
        client.register_plugin("embedding_optimizer", embedding_optimizer)
        client.register_plugin("metadata_enricher", metadata_enricher)
        client.register_plugin("quality_checker", quality_checker)
        
        # Process text with plugins
        raw_text = """
        <html>
            <body>
                <p>This is a test document with some content.</p>
                <p>It contains multiple paragraphs and formatting.</p>
            </body>
        </html>
        """
        
        # Execute plugins
        processed_data = await client.execute_plugins(
            data={"text": raw_text},
            plugin_names=["text_preprocessor", "metadata_enricher"]
        )
        
        print("Plugin processing results:")
        print(f"  Original text length: {len(raw_text)}")
        print(f"  Processed text length: {len(processed_data['text'])}")
        print(f"  Text processed: {processed_data.get('text_processed', False)}")
        
        # Create chunk with plugins
        chunk = SemanticChunk(
            body=processed_data["text"],
            text=processed_data["text"],
                            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        )
        
        # Process chunk with quality checker
        quality_data = await client.execute_plugins(
            data={"chunk": chunk.model_dump()},
            plugin_names=["quality_checker"]
        )
        
        if "quality_results" in quality_data:
            quality_results = quality_data["quality_results"]
            print(f"Quality check results:")
            print(f"  Overall quality: {quality_results.get('overall_quality', 0)}")
            print(f"  Passes quality check: {quality_results.get('passes_quality_check', False)}")
        
    except Exception as e:
        print(f"Error during plugin usage: {e}")


async def example_middleware_usage():
    """
    Example: Using middleware for cross-cutting concerns.
    
    Demonstrates using middleware for logging, caching, retry logic,
    and metrics collection.
    """
    print("=== Middleware Usage Example ===")
    
    # Initialize client
    client = VectorStoreClient("http://localhost:8007")
    
    try:
        # Initialize middleware
        logging_middleware = LoggingMiddleware(log_level="INFO", include_body=False)
        caching_middleware = CachingMiddleware(ttl=300, max_size=100)
        retry_middleware = RetryMiddleware(max_retries=3, base_delay=1.0)
        metrics_middleware = MetricsMiddleware()
        
        # Add middleware to client
        client.add_middleware(logging_middleware)
        client.add_middleware(caching_middleware)
        client.add_middleware(retry_middleware)
        client.add_middleware(metrics_middleware)
        
        # Execute operations with middleware
        print("Executing operations with middleware...")
        
        # Search operation
        search_results = await client.search_chunks(
            search_str="test query",
            limit=5
        )
        print(f"Search completed with {len(search_results)} results")
        
        # Get middleware metrics
        metrics = metrics_middleware.get_summary_metrics()
        print(f"Middleware metrics: {metrics}")
        
        # Get cache stats
        cache_stats = caching_middleware.get_cache_stats()
        print(f"Cache stats: {cache_stats}")
        
    except Exception as e:
        print(f"Error during middleware usage: {e}")


async def main():
    """
    Run all Phase 6 examples.
    """
    print("Phase 6: Optimization and Expansion Examples")
    print("=" * 50)
    
    # Run examples
    await example_streaming_large_datasets()
    print()
    
    await example_bulk_operations()
    print()
    
    await example_backup_and_restore()
    print()
    
    await example_data_migration()
    print()
    
    await example_performance_monitoring()
    print()
    
    await example_fallback_strategies()
    print()
    
    await example_plugin_usage()
    print()
    
    await example_middleware_usage()
    print()
    
    print("All Phase 6 examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 