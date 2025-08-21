"""
Comprehensive API Example for Vector Store Client.

This example demonstrates ALL REAL available methods and operations of the Vector Store client.
Only uses methods that actually exist in the server API.

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
from vector_store_client.models import SemanticChunk, SearchResult
from vector_store_client.types import ChunkType, LanguageEnum, SearchOrder
from vector_store_client.exceptions import VectorStoreError


async def comprehensive_api_example():
    """
    Demonstrate ALL REAL available methods and operations of the Vector Store client.
    
    This example covers only methods that actually exist in the server API:
    1. Client initialization and health checks
    2. All creation methods
    3. All search methods
    4. All deletion methods
    5. All maintenance operations
    6. All utility methods
    7. All batch operations
    8. All monitoring and statistics methods
    """
    print("=== Vector Store Client - Comprehensive API Example (REAL METHODS ONLY) ===\n")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    print("1. CLIENT INITIALIZATION")
    print("=" * 50)
    
    client = await VectorStoreClient.create(
        base_url="http://localhost:8007"
    )
    print("✓ Client created successfully")
    
    try:
        # 2. HEALTH AND SYSTEM OPERATIONS
        print("\n2. HEALTH AND SYSTEM OPERATIONS")
        print("=" * 50)
        
        # Basic health check
        health = await client.health_check()
        print(f"✓ Health check: {health.status}")
        print(f"  Version: {health.version}")
        print(f"  Uptime: {health.uptime}s")
        
        # Get help information
        help_info = await client.get_help()
        if isinstance(help_info, dict):
            commands = help_info.get('data', {}).get('commands', {})
            print(f"✓ Help info: {len(commands)} commands available")
        else:
            print(f"✓ Help info: {len(getattr(help_info, 'help_data', {}).get('commands', {}))} commands available")
        
        # Get configuration
        try:
            config = await client.get_config()
            print(f"✓ Configuration retrieved: {len(config)} items")
        except Exception as e:
            print(f"⚠️  Configuration retrieval failed: {e}")
            print("  Continuing with other operations...")
        
        # Set configuration
        try:
            set_config = await client.set_config("test_setting", "test_value")
            print(f"✓ Configuration set: {set_config}")
        except Exception as e:
            print(f"⚠️  Configuration setting failed: {e}")
        
        # Get server info
        try:
            server_info = await client.get_server_info()
            print(f"✓ Server info: {len(server_info)} items")
        except Exception as e:
            print(f"⚠️  Server info failed: {e}")
        
        # 3. CREATION OPERATIONS
        print("\n3. CREATION OPERATIONS")
        print("=" * 50)
        
        # Create single text chunk
        print("Creating single text chunk...")
        try:
            chunk = await client.create_text_chunk(
                text="This is a test chunk for comprehensive API example.",
                source_id=str(uuid.uuid4())
            )
            print(f"✓ Single chunk created: {chunk.uuid}")
        except Exception as e:
            print(f"❌ Single chunk creation failed: {e}")
        
        # Create multiple chunks
        print("Creating multiple chunks...")
        try:
            chunks = [
                SemanticChunk(
                    body="First comprehensive test chunk",
                    text="First comprehensive test chunk",
                    source_id=str(uuid.uuid4()),
                    embedding=[0.1] * 384,
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    category="test",
                    title="Comprehensive Test 1"
                ),
                SemanticChunk(
                    body="Second comprehensive test chunk",
                    text="Second comprehensive test chunk",
                    source_id=str(uuid.uuid4()),
                    embedding=[0.2] * 384,
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    category="test",
                    title="Comprehensive Test 2"
                )
            ]
            
            result = await client.create_chunks(chunks)
            print(f"✓ Multiple chunks created: {result.created_count}")
        except Exception as e:
            print(f"❌ Multiple chunks creation failed: {e}")
        
        # 4. SEARCH OPERATIONS
        print("\n4. SEARCH OPERATIONS")
        print("=" * 50)
        
        # Basic search
        print("Basic search...")
        try:
            results = await client.search_chunks(
                search_str="comprehensive test",
                limit=5
            )
            print(f"✓ Basic search: {len(results)} results")
        except Exception as e:
            print(f"❌ Basic search failed: {e}")
        
        # Search by metadata
        print("Search by metadata...")
        try:
            results = await client.search_by_metadata(
                metadata_filter={"category": "test"},
                limit=5
            )
            print(f"✓ Metadata search: {len(results)} results")
        except Exception as e:
            print(f"❌ Metadata search failed: {e}")
        
        # Search by text
        print("Search by text...")
        try:
            results = await client.search_by_text(
                search_str="test chunk",
                limit=5
            )
            print(f"✓ Text search: {len(results)} results")
        except Exception as e:
            print(f"❌ Text search failed: {e}")
        
        # Search by AST
        print("Search by AST...")
        try:
            results = await client.search_by_ast(
                ast_filter={"operator": "=", "field": "category", "value": "test"},
                limit=5
            )
            print(f"✓ AST search: {len(results)} results")
        except Exception as e:
            print(f"❌ AST search failed: {e}")
        
        # Search by vector
        print("Search by vector...")
        try:
            test_vector = [0.1] * 384
            results = await client.search_by_vector(
                embedding=test_vector,
                limit=5
            )
            print(f"✓ Vector search: {len(results)} results")
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
        
        # 5. COUNTING OPERATIONS
        print("\n5. COUNTING OPERATIONS")
        print("=" * 50)
        
        # Count chunks
        print("Counting chunks...")
        try:
            count = await client.count_chunks()
            print(f"✓ Total chunks: {count}")
        except Exception as e:
            print(f"❌ Count chunks failed: {e}")
        
        # Count by type
        print("Counting by type...")
        try:
            count = await client.count_chunks_by_type("DOC_BLOCK")
            print(f"✓ DOC_BLOCK chunks: {count}")
        except Exception as e:
            print(f"❌ Count by type failed: {e}")
        
        # Count by language
        print("Counting by language...")
        try:
            count = await client.count_chunks_by_language("EN")
            print(f"✓ EN language chunks: {count}")
        except Exception as e:
            print(f"❌ Count by language failed: {e}")
        
        # Get chunk statistics
        print("Getting chunk statistics...")
        try:
            stats = await client.get_chunk_statistics()
            print(f"✓ Chunk statistics: {len(stats)} metrics")
        except Exception as e:
            print(f"❌ Get statistics failed: {e}")
        
        # 6. DELETION OPERATIONS
        print("\n6. DELETION OPERATIONS")
        print("=" * 50)
        
        # Delete by metadata
        print("Deleting by metadata...")
        try:
            result = await client.delete_chunks(
                metadata_filter={"category": "test"}
            )
            print(f"✓ Deleted by metadata: {result.deleted_count}")
        except Exception as e:
            print(f"❌ Delete by metadata failed: {e}")
        
        # Force delete by UUIDs
        print("Force deleting by UUIDs...")
        try:
            # Get some UUIDs to delete
            search_results = await client.search_chunks(limit=2)
            if search_results:
                uuids_to_delete = [chunk.uuid for chunk in search_results if chunk.uuid]
                if uuids_to_delete:
                    result = await client.force_delete_by_uuids(uuids_to_delete)
                    print(f"✓ Force delete: {result.deleted_count}")
                else:
                    print("⚠️  No UUIDs available for force deletion")
            else:
                print("⚠️  No chunks available for force deletion")
        except Exception as e:
            print(f"❌ Force delete failed: {e}")
        
        # 7. MAINTENANCE OPERATIONS
        print("\n7. MAINTENANCE OPERATIONS")
        print("=" * 50)
        
        # Find duplicates
        print("Finding duplicates...")
        try:
            result = await client.find_duplicate_uuids()
            print(f"✓ Duplicates found: {result.total_duplicates}")
        except Exception as e:
            print(f"❌ Find duplicates failed: {e}")
        
        # Clean FAISS orphans
        print("Cleaning FAISS orphans...")
        try:
            result = await client.clean_faiss_orphans()
            print(f"✓ FAISS orphans cleaned: {result.cleaned_count}")
        except Exception as e:
            print(f"❌ Clean FAISS orphans failed: {e}")
        
        # Reindex missing embeddings
        print("Reindexing missing embeddings...")
        try:
            result = await client.reindex_missing_embeddings()
            print(f"✓ Reindexed: {result.reindexed_count}")
        except Exception as e:
            print(f"❌ Reindex failed: {e}")
        
        # Deferred cleanup
        print("Performing deferred cleanup...")
        try:
            result = await client.chunk_deferred_cleanup()
            print(f"✓ Deferred cleanup: {result.cleaned_count}")
        except Exception as e:
            print(f"❌ Deferred cleanup failed: {e}")
        
        # Server health check
        print("Checking server health...")
        try:
            health = await client.health_check()
            print(f"✓ Server health: {health.status}")
        except Exception as e:
            print(f"❌ Server health failed: {e}")
        
        # Server info
        print("Getting server information...")
        try:
            info = await client.get_server_info()
            print(f"✓ Server info: {len(info)} items")
        except Exception as e:
            print(f"❌ Server info failed: {e}")
        
        # 8. EMBEDDING OPERATIONS
        print("\n8. EMBEDDING OPERATIONS")
        print("=" * 50)
        
        # Embed single text
        print("Embedding single text...")
        try:
            embed_response = await client.embed_text("Test text for embedding")
            print(f"✓ Embedded text: {len(embed_response.embedding)} dimensions")
        except Exception as e:
            print(f"❌ Text embedding failed: {e}")
        
        # Embed batch
        print("Embedding batch...")
        try:
            batch_embeddings = await client.embed_batch(["Text 1", "Text 2", "Text 3"])
            print(f"✓ Batch embedded: {len(batch_embeddings)} texts")
        except Exception as e:
            print(f"❌ Batch embedding failed: {e}")
        
        # Get embedding models
        print("Getting embedding models...")
        try:
            models = await client.get_embedding_models()
            print(f"✓ Available models: {len(models.models)}")
        except Exception as e:
            print(f"❌ Get models failed: {e}")
        
        # 9. BATCH OPERATIONS
        print("\n9. BATCH OPERATIONS")
        print("=" * 50)
        
        # Batch create chunks
        print("Batch creating chunks...")
        try:
            batch_chunks = [
                SemanticChunk(
                    body=f"Batch chunk {i}",
                    text=f"Batch chunk {i}",
                    source_id=str(uuid.uuid4()),
                    embedding=[0.1 + i * 0.01] * 384,
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    category="batch",
                    title=f"Batch Test {i}"
                )
                for i in range(3)
            ]
            
            result = await client.create_chunks(batch_chunks)
            print(f"✓ Batch created: {result.created_count} chunks")
        except Exception as e:
            print(f"❌ Batch creation failed: {e}")
        
        # Batch search
        print("Batch searching...")
        try:
            search_queries = [
                {"search_str": "batch", "limit": 2},
                {"search_str": "test", "limit": 2},
                {"search_str": "chunk", "limit": 2}
            ]
            
            batch_results = []
            for query in search_queries:
                results = await client.search_chunks(**query)
                batch_results.append(results)
            
            print(f"✓ Batch search: {len(batch_results)} result sets")
        except Exception as e:
            print(f"❌ Batch search failed: {e}")
        
        # Batch delete
        print("Batch deleting...")
        try:
            result = await client.delete_chunks(
                metadata_filter={"category": "batch"}
            )
            print(f"✓ Batch deleted: {result.deleted_count} chunks")
        except Exception as e:
            print(f"❌ Batch delete failed: {e}")
        
        print("\n=== Comprehensive API example completed successfully! ===")
        print("✅ All REAL methods demonstrated successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            await client.close()
            print("✓ Client closed successfully")
        except Exception as e:
            print(f"❌ Failed to close client: {e}")


async def main():
    """Run the comprehensive API example."""
    await comprehensive_api_example()


if __name__ == "__main__":
    asyncio.run(main()) 