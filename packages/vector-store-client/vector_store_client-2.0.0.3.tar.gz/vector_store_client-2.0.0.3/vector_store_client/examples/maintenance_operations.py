"""
Maintenance Operations Examples.

This module demonstrates how to use the maintenance operations
for vector store management and cleanup using real services.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from typing import Dict, Any, List
import uuid

from vector_store_client import VectorStoreClient
from vector_store_client.models import SemanticChunk


async def example_find_duplicates():
    """Example: Find duplicate UUIDs in the vector store."""
    print("🔍 Finding duplicate UUIDs...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Basic duplicate detection
        duplicates_result = await client.execute_command("find_duplicate_uuids", {})
        print(f"Found {duplicates_result.get('total_duplicates', 0)} duplicate chunks")
        
        if duplicates_result.get('duplicates'):
            print("Duplicate groups:")
            for i, group in enumerate(duplicates_result['duplicates'], 1):
                print(f"  Group {i}: {group}")
    
        # Duplicate detection with metadata filter
        metadata_filter = {"type": "Draft"}
        filtered_result = await client.execute_command("find_duplicate_uuids", {
            "metadata_filter": metadata_filter
        })
        print(f"Found {filtered_result.get('total_duplicates', 0)} duplicates in Draft chunks")
        
    except Exception as e:
        print(f"⚠️  Error finding duplicates: {e}")
        metadata_filter = {"type": "Draft"}
        filtered_result = await client.execute_command("find_duplicate_uuids", {
            "metadata_filter": metadata_filter
        })
        print(f"Found {filtered_result.get('total_duplicates', 0)} duplicates in Draft chunks")
        
    except Exception as e:
        print(f"⚠️  Error finding duplicates: {e}")


async def example_cleanup_duplicates():
    """Example: Clean up duplicate chunks."""
    print("🧹 Cleaning up duplicates...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # First, find duplicates
        duplicates_result = await client.find_duplicate_uuids()
        
        if hasattr(duplicates_result, 'duplicates') and duplicates_result.duplicates:
            print(f"Found {len(duplicates_result.duplicates)} duplicate UUIDs")
            
            print("Duplicate UUIDs found:")
            for i, uuid in enumerate(duplicates_result.duplicates[:5], 1):
                print(f"  {i}. {uuid}")
        else:
            print("No duplicates found to clean")
            
    except Exception as e:
        print(f"⚠️  Error cleaning duplicates: {e}")


async def example_cleanup_operations():
    """Example: Perform various cleanup operations."""
    print("🧹 Performing cleanup operations...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Clean FAISS orphans
        print("Cleaning FAISS orphans...")
        orphans_result = await client.execute_command("clean_faiss_orphans", {})
        print(f"Cleaned {orphans_result.get('cleaned_count', 0)} orphaned FAISS entries")
        
        # Deferred cleanup
        print("Performing deferred cleanup...")
        deferred_result = await client.execute_command("chunk_deferred_cleanup", {})
        print(f"Cleaned {deferred_result.get('cleaned_count', 0)} deferred chunks")
        
    except Exception as e:
        print(f"⚠️  Error during cleanup operations: {e}")


async def example_reindex_operations():
    """Example: Reindex missing embeddings."""
    print("🔄 Reindexing missing embeddings...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        reindex_result = await client.execute_command("reindex_missing_embeddings", {})
        print(f"Reindexed {reindex_result.get('reindexed_count', 0)} chunks with missing embeddings")
        
    except Exception as e:
        print(f"⚠️  Error during reindexing: {e}")


async def example_force_delete():
    """Example: Force delete chunks by UUIDs."""
    print("🗑️ Force deleting chunks...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # First, get some existing UUIDs to delete
        search_result = await client.search_chunks(limit=2)
        
        if search_result:
            uuids_to_delete = [chunk.uuid for chunk in search_result[:2]]
            print(f"Will force delete UUIDs: {uuids_to_delete}")
            
            delete_result = await client.execute_command("force_delete_by_uuids", {
                "uuids": uuids_to_delete
            })
            print(f"Force deleted {delete_result.get('deleted_count', 0)} chunks")
            print(f"Deleted UUIDs: {delete_result.get('deleted_uuids', [])}")
        else:
            print("No chunks found to delete")
            
    except Exception as e:
        print(f"⚠️  Error during force delete: {e}")


async def example_maintenance_health_check():
    """Example: Check maintenance system health."""
    print("🏥 Checking maintenance system health...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Check general health
        health = await client.health_check()
        print(f"Server health: {health.status}")
        print(f"Version: {health.version}")
        print(f"Uptime: {health.uptime}s")
        
        # Check specific maintenance operations
        print("\nMaintenance Health Status:")
        
        # Check duplicates
        try:
            duplicates_result = await client.find_duplicate_uuids()
            if hasattr(duplicates_result, 'duplicates'):
                print(f"  Duplicates: {len(duplicates_result.duplicates)} found")
            else:
                print(f"  Duplicates: 0 found")
        except Exception as e:
            print(f"  Duplicates: Error - {e}")
        
        # Check FAISS orphans
        try:
            orphans_result = await client.clean_faiss_orphans()
            cleaned_count = getattr(orphans_result, 'cleaned_count', 0)
            print(f"  FAISS Orphans: {cleaned_count} cleaned")
        except Exception as e:
            print(f"  FAISS Orphans: Error - {e}")
        
    except Exception as e:
        print(f"⚠️  Error checking maintenance health: {e}")


async def example_full_maintenance():
    """Example: Perform full maintenance cycle."""
    print("🔧 Performing full maintenance cycle...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        print("Maintenance Results:")
        
        # 1. Find duplicates
        print("  1. Finding duplicates...")
        try:
            duplicates_result = await client.execute_command("find_duplicate_uuids", {})
            total_duplicates = duplicates_result.get('total_duplicates', 0)
            print(f"     Found {total_duplicates} duplicates")
        except Exception as e:
            print(f"     Failed: {e}")
        
        # 2. Clean FAISS orphans
        print("  2. Cleaning FAISS orphans...")
        try:
            orphans_result = await client.execute_command("clean_faiss_orphans", {})
            cleaned_count = orphans_result.get('cleaned_count', 0)
            print(f"     Cleaned {cleaned_count} orphans")
        except Exception as e:
            print(f"     Failed: {e}")
        
        # 3. Deferred cleanup
        print("  3. Performing deferred cleanup...")
        try:
            deferred_result = await client.execute_command("chunk_deferred_cleanup", {})
            cleaned_count = deferred_result.get('cleaned_count', 0)
            print(f"     Cleaned {cleaned_count} deferred chunks")
        except Exception as e:
            print(f"     Failed: {e}")
        
        # 4. Reindex missing embeddings
        print("  4. Reindexing missing embeddings...")
        try:
            reindex_result = await client.execute_command("reindex_missing_embeddings", {})
            reindexed_count = reindex_result.get('reindexed_count', 0)
            print(f"     Reindexed {reindexed_count} chunks")
        except Exception as e:
            print(f"     Failed: {e}")
        
    except Exception as e:
        print(f"⚠️  Error during full maintenance: {e}")


async def example_maintenance_with_filters():
    """Example: Maintenance operations with filters."""
    print("🔍 Maintenance with filters...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Find duplicates in specific type
        metadata_filter = {"type": "Draft"}
        duplicates_result = await client.execute_command("find_duplicate_uuids", {
            "metadata_filter": metadata_filter
        })
        total_duplicates = duplicates_result.get('total_duplicates', 0)
        print(f"Found {total_duplicates} duplicates in Draft chunks")
        
        if total_duplicates > 0:
            print("Would clean duplicates with filter:")
            for i, group in enumerate(duplicates_result.get('duplicates', []), 1):
                print(f"  Group {i}: {group}")
        
    except Exception as e:
        print(f"⚠️  Error during maintenance with filters: {e}")


async def example_create_test_data():
    """Create test data for maintenance examples."""
    print("📝 Creating test data for maintenance examples...")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create some test chunks that might have duplicates
        test_chunks = [
            SemanticChunk(
                body="Test chunk 1 for maintenance",
                text="Test chunk 1 for maintenance",
                type="Draft",
                language="en",
                source_id=str(uuid.uuid4()),
                embedding=[0.1] * 384
            ),
            SemanticChunk(
                body="Test chunk 2 for maintenance", 
                text="Test chunk 2 for maintenance",
                type="Draft",
                language="en",
                source_id=str(uuid.uuid4()),
                embedding=[0.2] * 384
            ),
            SemanticChunk(
                body="Test chunk 3 for maintenance",
                text="Test chunk 3 for maintenance", 
                type="DocBlock",
                language="ru",
                source_id=str(uuid.uuid4()),
                embedding=[0.3] * 384
            )
        ]
        
        create_result = await client.create_chunks(test_chunks)
        print(f"Created {len(create_result.uuids)} test chunks")
        print(f"UUIDs: {create_result.uuids}")
        
    except Exception as e:
        print(f"⚠️  Error creating test data: {e}")


async def main():
    """Run all maintenance operation examples."""
    print("🚀 Vector Store Maintenance Operations Examples")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    try:
        # Create test data first
        await example_create_test_data()
        print()
        
        await example_find_duplicates()
        print()
        
        await example_cleanup_duplicates()
        print()
        
        await example_cleanup_operations()
        print()
        
        await example_reindex_operations()
        print()
        
        await example_force_delete()
        print()
        
        await example_maintenance_health_check()
        print()
        
        await example_full_maintenance()
        print()
        
        await example_maintenance_with_filters()
        print()
        
        print("✅ All maintenance operation examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during maintenance operations: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 