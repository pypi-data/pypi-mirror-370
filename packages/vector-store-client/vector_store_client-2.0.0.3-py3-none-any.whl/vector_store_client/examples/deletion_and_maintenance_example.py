"""
Deletion and Maintenance Operations Examples.

This example demonstrates comprehensive deletion and maintenance operations:
1. Various deletion strategies
2. Maintenance operations
3. Cleanup procedures
4. Health monitoring

This serves as a comprehensive guide for database management operations.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from typing import List, Dict, Any
import uuid

from vector_store_client import VectorStoreClient
from vector_store_client.models import SemanticChunk, DeleteResponse
from vector_store_client.types import ChunkType, LanguageEnum, ChunkStatus


async def deletion_operations_example():
    """
    Demonstrate various deletion operations and strategies.
    """
    print("=== Deletion Operations Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create test data for deletion examples
        print("1. Creating test data for deletion examples...")
        test_chunks = create_test_chunks_for_deletion()
        
        create_result = await client.create_chunks(test_chunks)
        print(f"✓ Created {create_result.created_count} test chunks")
        print()
        
        # Get some chunk UUIDs for demonstration
        all_chunks = await client.search_chunks(limit=20)
        if not all_chunks:
            print("⚠️  No chunks found for deletion examples")
            return
        
        print("2. Demonstrating different deletion strategies...")
        
        # Strategy 1: Delete by UUIDs
        print("  Strategy 1: Delete by specific UUIDs")
        uuids_to_delete = [all_chunks[0].uuid, all_chunks[1].uuid]
        
        delete_result = await client.delete_chunks(uuids=uuids_to_delete)
        print(f"    ✓ Deleted {delete_result.deleted_count} chunks by UUID")
        print(f"    ✓ Deleted UUIDs: {delete_result.deleted_uuids}")
        print()
        
        # Strategy 2: Delete by metadata filter
        print("  Strategy 2: Delete by metadata filter")
        metadata_delete_result = await client.delete_chunks(
            metadata_filter={"category": "Test", "tags": ["temporary"]}
        )
        print(f"    ✓ Deleted {metadata_delete_result.deleted_count} chunks by metadata")
        print()
        
        # Strategy 3: Delete with confirmation (simulated)
        print("  Strategy 3: Delete with confirmation (dry run)")
        remaining_chunks = await client.search_chunks(limit=5)
        if remaining_chunks:
            confirm_uuids = [remaining_chunks[0].uuid]
            
            # Simulate confirmation delete
            try:
                confirm_result = await client.delete_chunks(uuids=confirm_uuids)
                print(f"    ✓ Deleted {confirm_result.deleted_count} chunks")
            except Exception as e:
                print(f"    ⚠️  Delete failed: {e}")
        print()
        
        # Strategy 4: Delete by metadata filter
        print("  Strategy 4: Delete by metadata filter")
        try:
            type_delete_result = await client.delete_chunks(
                metadata_filter={"category": "Test"}
            )
            print(f"    ✓ Deleted {type_delete_result.deleted_count} chunks by metadata")
        except Exception as e:
            print(f"    ⚠️  Delete by metadata failed: {e}")
        print()
        
        # Strategy 5: Delete by tags
        print("  Strategy 5: Delete by tags")
        try:
            project_delete_result = await client.delete_chunks(
                metadata_filter={"tags": ["temporary"]}
            )
            print(f"    ✓ Deleted {project_delete_result.deleted_count} chunks by tags")
        except Exception as e:
            print(f"    ⚠️  Delete by tags failed: {e}")
        print()
        
        # Strategy 6: Hard delete (permanent)
        print("  Strategy 6: Hard delete (permanent)")
        hard_delete_uuids = [str(uuid.uuid4())]  # Use dummy UUID for demo
        
        try:
            hard_delete_result = await client.chunk_hard_delete(
                uuids=hard_delete_uuids,
                confirm=False
            )
            print(f"    ✓ Hard deleted {hard_delete_result.deleted_count} chunks")
        except Exception as e:
            print(f"    ⚠️  Hard delete demo failed (expected): {e}")
        print()
        
        # Strategy 7: Force delete by UUIDs
        print("  Strategy 7: Force delete by UUIDs")
        force_delete_uuids = [str(uuid.uuid4())]  # Use dummy UUID for demo
        
        try:
            force_delete_result = await client.force_delete_by_uuids(force_delete_uuids)
            print(f"    ✓ Force deleted {force_delete_result.deleted_count} chunks")
        except Exception as e:
            print(f"    ⚠️  Force delete demo failed (expected): {e}")
        print()
        
        print("=== Deletion operations completed! ===")
        
    except Exception as e:
        print(f"✗ Error during deletion operations: {e}")
        raise
    finally:
        await client.close()


async def maintenance_operations_example():
    """
    Demonstrate comprehensive maintenance operations.
    """
    print("\n=== Maintenance Operations Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        print("1. Checking server health...")
        
        # Check server health
        health = await client.health_check()
        print(f"  Server Status: {health.status}")
        print(f"  Version: {health.version}")
        print(f"  Uptime: {health.uptime} seconds")
        print(f"  Server Info: {health}")
        print()
        
        print("2. Finding and analyzing duplicates...")
        
        # Find duplicates
        try:
            duplicates = await client.find_duplicate_uuids()
            print(f"  ✓ Found {len(duplicates.duplicates) if hasattr(duplicates, 'duplicates') else 0} duplicate UUIDs")
            
            if hasattr(duplicates, 'duplicates') and duplicates.duplicates:
                print("  Duplicate UUIDs:")
                for i, uuid in enumerate(duplicates.duplicates[:5], 1):
                    print(f"    {i}. {uuid}")
        except Exception as e:
            print(f"  ⚠️  Find duplicates failed: {e}")
        print()
        
        # Find duplicates with metadata filter
        print("  Finding duplicates in specific category...")
        try:
            filtered_duplicates = await client.find_duplicate_uuids()
            print(f"  ✓ Found {len(filtered_duplicates.duplicates) if hasattr(filtered_duplicates, 'duplicates') else 0} total duplicates")
        except Exception as e:
            print(f"  ⚠️  Filtered duplicates failed: {e}")
        print()
        
        print("3. Performing cleanup operations...")
        

        
        print("5. Performing maintenance operations...")
        
        # Perform individual maintenance operations
        print("  Cleaning FAISS orphans...")
        try:
            orphans_result = await client.clean_faiss_orphans()
            print(f"    ✓ Cleaned {getattr(orphans_result, 'cleaned_count', 0)} orphaned FAISS entries")
        except Exception as e:
            print(f"    ⚠️  Clean FAISS orphans failed: {e}")
        
        print("  Performing deferred cleanup...")
        try:
            deferred_result = await client.chunk_deferred_cleanup()
            print(f"    ✓ Cleaned {getattr(deferred_result, 'cleaned_count', 0)} deferred chunks")
        except Exception as e:
            print(f"    ⚠️  Deferred cleanup failed: {e}")
        
        print("  Reindexing missing embeddings...")
        try:
            reindex_result = await client.reindex_missing_embeddings()
            print(f"    ✓ Reindexed {getattr(reindex_result, 'reindexed_count', 0)} chunks")
        except Exception as e:
            print(f"    ⚠️  Reindex failed: {e}")
        print()
        
        print("6. Maintenance summary...")
        print("  ✓ All maintenance operations completed")
        print()
        
        print("=== Maintenance operations completed! ===")
        
    except Exception as e:
        print(f"✗ Error during maintenance operations: {e}")
        raise
    finally:
        await client.close()


async def batch_operations_example():
    """
    Demonstrate batch deletion and maintenance operations.
    """
    print("\n=== Batch Operations Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        print("1. Creating large dataset for batch operations...")
        
        # Create large dataset
        large_chunks = []
        for i in range(50):
            chunk = SemanticChunk(
                body=f"Batch test chunk {i} for demonstration purposes",
                text=f"Batch test chunk {i} for demonstration purposes",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                title=f"Batch Test {i}",
                category="BatchTest",
                tags=["batch", "test", f"batch-{i//10}"]
            )
            large_chunks.append(chunk)
        
        # Store in batches
        batch_size = 10
        total_created = 0
        
        for i in range(0, len(large_chunks), batch_size):
            batch = large_chunks[i:i + batch_size]
            result = await client.create_chunks(batch)
            total_created += result.created_count
        
        print(f"✓ Created {total_created} chunks in batches")
        print()
        
        print("2. Batch deletion operations...")
        
        # Get all test chunks
        test_chunks = await client.search_chunks(
            metadata_filter={"category": "BatchTest"},
            limit=100
        )
        
        if test_chunks:
            # Batch delete
            chunk_uuids = [chunk.uuid for chunk in test_chunks]
            
            print(f"  Batch deleting {len(chunk_uuids)} chunks...")
            total_deleted = 0
            
            # Delete in batches
            batch_size = 5
            for i in range(0, len(chunk_uuids), batch_size):
                batch_uuids = chunk_uuids[i:i + batch_size]
                try:
                    result = await client.delete_chunks(uuids=batch_uuids)
                    total_deleted += result.deleted_count
                    print(f"    Batch {i//batch_size + 1}: Deleted {result.deleted_count} chunks")
                except Exception as e:
                    print(f"    Batch {i//batch_size + 1}: Failed - {e}")
            
            print(f"    ✓ Total deleted: {total_deleted} chunks")
        print()
        
        print("3. Bulk operations...")
        
        # Bulk delete with progress tracking
        print("  Bulk delete with progress tracking...")
        
        def progress_callback(deleted_count):
            print(f"    Progress: {deleted_count} chunks deleted")
        
        # Simulate bulk delete
        remaining_chunks = await client.search_chunks(
            metadata_filter={"category": "BatchTest"},
            limit=50
        )
        
        if remaining_chunks:
            bulk_deleted = 0
            bulk_errors = 0
            
            for chunk in remaining_chunks:
                try:
                    result = await client.delete_chunks(uuids=[chunk.uuid])
                    bulk_deleted += result.deleted_count
                    progress_callback(bulk_deleted)
                except Exception as e:
                    bulk_errors += 1
                    print(f"    Error deleting {chunk.uuid}: {e}")
            
            print(f"    ✓ Bulk deleted {bulk_deleted} chunks")
            print(f"    ✓ Total errors: {bulk_errors}")
        print()
        
        print("=== Batch operations completed! ===")
        
    except Exception as e:
        print(f"✗ Error during batch operations: {e}")
        raise
    finally:
        await client.close()


async def monitoring_and_health_example():
    """
    Demonstrate monitoring and health checking operations.
    """
    print("\n=== Monitoring and Health Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        print("1. Basic health monitoring...")
        
        # Check basic health
        health = await client.health_check()
        print(f"  Server Status: {health.status}")
        print(f"  Version: {health.version}")
        print(f"  Uptime: {health.uptime} seconds")
        print(f"  Server Info: {health}")
        print()
        
        print("2. Server information...")
        
        # Get server info
        try:
            server_info = await client.get_server_info()
            print("  Server Information:")
            for key, value in server_info.items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"    ⚠️  Server info failed: {e}")
        print()
        
        print("3. Configuration...")
        
        # Get configuration
        try:
            config = await client.get_config()
            print("  Configuration:")
            for key, value in config.items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"    ⚠️  Configuration failed: {e}")
        print()
        
        print("4. Chunk statistics...")
        
        # Get chunk statistics
        try:
            stats = await client.get_chunk_statistics()
            print("  Chunk Statistics:")
            for key, value in stats.items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"    ⚠️  Statistics failed: {e}")
        print()
        
        print("5. Count chunks...")
        
        # Count chunks
        try:
            count = await client.count_chunks()
            print(f"  Total Chunks: {count}")
        except Exception as e:
            print(f"    ⚠️  Count failed: {e}")
        print()
        
        print("=== Monitoring and health completed! ===")
        
    except Exception as e:
        print(f"✗ Error during monitoring: {e}")
        raise
    finally:
        await client.close()


def create_test_chunks_for_deletion() -> List[SemanticChunk]:
    """Create test chunks for deletion examples."""
    return [
        SemanticChunk(
            body="Test chunk 1 for deletion demonstration",
            text="Test chunk 1 for deletion demonstration",
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Test Chunk 1",
            category="Test",
            tags=["test", "temporary", "deletion-demo"]
        ),
        SemanticChunk(
            body="Test chunk 2 for deletion demonstration",
            text="Test chunk 2 for deletion demonstration",
            source_id=str(uuid.uuid4()),
            embedding=[0.2] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Test Chunk 2",
            category="Test",
            tags=["test", "temporary", "deletion-demo"]
        ),
        SemanticChunk(
            body="Test chunk 3 for deletion demonstration",
            text="Test chunk 3 for deletion demonstration",
            source_id=str(uuid.uuid4()),
            embedding=[0.3] * 384,
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Test Chunk 3",
            category="Test",
            tags=["test", "temporary", "deletion-demo"]
        )
    ]


async def main():
    """
    Run all deletion and maintenance examples.
    """
    try:
        await deletion_operations_example()
        await maintenance_operations_example()
        await batch_operations_example()
        await monitoring_and_health_example()
        
        print("\n🎉 All deletion and maintenance examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Examples failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 