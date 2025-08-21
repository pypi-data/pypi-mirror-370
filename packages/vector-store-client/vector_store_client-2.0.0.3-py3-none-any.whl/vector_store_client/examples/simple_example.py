"""
Simple Example for Vector Store Client.

A minimal example showing the most common operations:
- Client initialization
- Creating chunks
- Searching chunks
- Basic operations

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from vector_store_client import VectorStoreClient, SemanticChunk, ChunkType, LanguageEnum, ChunkStatus, ChunkRole
from vector_store_client.utils import generate_uuid


async def main():
    """Simple example demonstrating basic operations."""
    print("=== Vector Store Client - Simple Example ===")
    
    # Create client
    client = await VectorStoreClient.create("http://localhost:8007")
    print("✓ Client created")
    
    try:
        # 1. Health check
        health = await client.health_check()
        print(f"✓ Server health: {health.status}")
        
        # 2. Create a simple chunk
        chunk = await client.create_text_chunk(
            text="Hello, this is a simple test chunk!",
            source_id=generate_uuid()
        )
        print(f"✓ Created chunk: {chunk.uuid}")
        
        # 3. Create multiple chunks
        chunks = [
            SemanticChunk(
                body="First chunk with custom embedding",
                text="First chunk with custom embedding",
                source_id=generate_uuid(),
                embedding=[0.1] * 384,  # 384-dimensional vector
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                status=ChunkStatus.NEW,
                role=ChunkRole.USER,
                category="example",
                title="Example Chunk 1"
            ),
            SemanticChunk(
                body="Second chunk with custom embedding", 
                text="Second chunk with custom embedding",
                source_id=generate_uuid(),
                embedding=[0.2] * 384,  # 384-dimensional vector
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                status=ChunkStatus.NEW,
                role=ChunkRole.USER,
                category="example",
                title="Example Chunk 2"
            )
        ]
        
        result = await client.create_chunks(chunks)
        print(f"✓ Created {result.created_count} chunks")
        
        # 4. Search chunks
        results = await client.search_chunks(
            search_str="simple test",
            limit=5
        )
        print(f"✓ Found {len(results)} matching chunks")
        
        # 5. Count chunks
        count = await client.count_chunks()
        print(f"✓ Total chunks in store: {count}")
        
        # 6. Clean up - delete test chunks
        delete_result = await client.delete_chunks(
            metadata_filter={"category": "example"}
        )
        print(f"✓ Cleaned up {delete_result.deleted_count} test chunks")
        
        print("\n=== Simple example completed successfully! ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()
        print("✓ Client closed")


if __name__ == "__main__":
    asyncio.run(main()) 