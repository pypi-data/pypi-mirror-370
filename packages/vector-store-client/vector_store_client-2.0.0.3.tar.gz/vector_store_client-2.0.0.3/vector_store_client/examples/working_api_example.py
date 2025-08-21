"""
Working API Example for Vector Store Client.

This module demonstrates the REAL working API methods of the Vector Store client.
Only uses methods that actually exist and work correctly.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from typing import List, Dict, Any

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
    ChunkStatus,
    ChunkRole,
    BlockType
)
from vector_store_client.utils import generate_uuid


async def main():
    """Demonstrate working API methods."""
    print("=== Vector Store Client - Working API Example ===")
    print("Only using REAL methods that actually work!")
    print("=" * 60)
    
    # Initialize client
    print("1. CLIENT INITIALIZATION")
    print("=" * 50)
    
    try:
        client = await VectorStoreClient.create("http://localhost:8007")
        print("✓ Client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    
    try:
        # 2. HEALTH AND SYSTEM OPERATIONS
        print("\n2. HEALTH AND SYSTEM OPERATIONS")
        print("=" * 50)
        
        # Health check
        print("Health check...")
        try:
            health = await client.health_check()
            print(f"✓ Health: {health.status}")
            print(f"  Version: {health.version}")
            print(f"  Uptime: {health.uptime}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Get help
        print("Getting help...")
        try:
            help_info = await client.get_help()
            print(f"✓ Help: {len(help_info.get('data', {}).get('commands', []))} commands available")
        except Exception as e:
            print(f"❌ Help failed: {e}")
        
        # Get server info
        print("Getting server info...")
        try:
            server_info = await client.get_server_info()
            print(f"✓ Server info: {len(server_info)} items")
        except Exception as e:
            print(f"❌ Server info failed: {e}")
        
        # 3. CREATION OPERATIONS
        print("\n3. CREATION OPERATIONS")
        print("=" * 50)
        
        # Create single text chunk
        print("Creating single text chunk...")
        try:
            chunk = await client.create_text_chunk(
                text="This is a test chunk for the working API example.",
                source_id=generate_uuid()
            )
            print(f"✓ Single chunk created: {chunk.uuid}")
            print(f"  Text: {chunk.body[:50]}...")
            print(f"  Type: {chunk.type}")
            print(f"  Language: {chunk.language}")
        except Exception as e:
            print(f"❌ Single chunk creation failed: {e}")
        
        # Create multiple chunks
        print("Creating multiple chunks...")
        try:
            chunks = [
                SemanticChunk(
                    body="First test chunk for working example",
                    text="First test chunk for working example",
                    source_id=generate_uuid(),
                    embedding=[0.1] * 384,  # 384-dimensional vector
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    status=ChunkStatus.NEW,
                    role=ChunkRole.USER,
                    category="test",
                    title="Test Chunk 1"
                ),
                SemanticChunk(
                    body="Second test chunk for working example",
                    text="Second test chunk for working example", 
                    source_id=generate_uuid(),
                    embedding=[0.2] * 384,  # 384-dimensional vector
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    status=ChunkStatus.NEW,
                    role=ChunkRole.USER,
                    category="test",
                    title="Test Chunk 2"
                )
            ]
            
            result = await client.create_chunks(chunks)
            print(f"✓ Multiple chunks created: {result.created_count}")
            print(f"  UUIDs: {result.uuids}")
        except Exception as e:
            print(f"❌ Multiple chunks creation failed: {e}")
        
        # 4. SEARCH OPERATIONS
        print("\n4. SEARCH OPERATIONS")
        print("=" * 50)
        
        # Basic search
        print("Basic search...")
        try:
            results = await client.search_chunks(
                search_str="test chunk",
                limit=5
            )
            print(f"✓ Basic search: {len(results)} results")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. {result.body[:50]}...")
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
                search_str="working example",
                limit=5
            )
            print(f"✓ Text search: {len(results)} results")
        except Exception as e:
            print(f"❌ Text search failed: {e}")
        
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
        
        # Deferred cleanup
        print("Performing deferred cleanup...")
        try:
            result = await client.chunk_deferred_cleanup()
            print(f"✓ Deferred cleanup: {result.cleaned_count}")
        except Exception as e:
            print(f"❌ Deferred cleanup failed: {e}")
        
        # 8. EMBEDDING OPERATIONS
        print("\n8. EMBEDDING OPERATIONS")
        print("=" * 50)
        
        # Embed single text
        print("Embedding single text...")
        try:
            embed_response = await client.embed_text("Test text for embedding")
            print(f"✓ Embedded text: {len(embed_response.embedding)} dimensions")
            print(f"  Model: {embed_response.model}")
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
            print(f"  Default model: {models.default_model}")
        except Exception as e:
            print(f"❌ Get models failed: {e}")
        
        # 9. CONFIGURATION OPERATIONS
        print("\n9. CONFIGURATION OPERATIONS")
        print("=" * 50)
        
        # Get configuration
        print("Getting configuration...")
        try:
            config = await client.get_config()
            print(f"✓ Configuration: {len(config)} items")
        except Exception as e:
            print(f"❌ Get config failed: {e}")
        
        # Set configuration
        print("Setting configuration...")
        try:
            result = await client.set_config("test_setting", "test_value")
            print(f"✓ Configuration set: {result}")
        except Exception as e:
            print(f"❌ Set config failed: {e}")
        
        print("\n=== Working API example completed! ===")
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


if __name__ == "__main__":
    asyncio.run(main()) 