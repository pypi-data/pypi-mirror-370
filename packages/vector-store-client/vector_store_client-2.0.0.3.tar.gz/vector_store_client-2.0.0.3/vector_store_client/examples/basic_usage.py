"""
Basic usage example for Vector Store Client.

This example demonstrates basic operations with the Vector Store client
including connection, health check, chunk creation via SVO Chunker, and search.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
import uuid
from typing import List

from vector_store_client import VectorStoreClient
from vector_store_client.models import SemanticChunk, CreateChunksResponse
from vector_store_client.types import ChunkType, LanguageEnum


async def basic_usage_example():
    """
    Demonstrate basic usage of Vector Store client.
    
    This example shows:
    1. Creating a client connection
    2. Checking server health
    3. Creating chunks via SVO Chunker
    4. Saving chunks to Vector Store
    5. Searching chunks
    6. Getting help information
    """
    print("=== Vector Store Client - Basic Usage Example ===\n")
    
    # Setup logging - only show INFO and above, suppress DEBUG messages
    logging.basicConfig(level=logging.INFO)
    # Suppress debug messages from httpx and httpcore
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("vector_store_client.base_client").setLevel(logging.WARNING)
    
    # Create client
    print("1. Creating client connection...")
    client = await VectorStoreClient.create("http://localhost:8007")
    print("✓ Client created successfully\n")
    
    try:
        # Check server health
        print("2. Checking server health...")
        health = await client.health_check()
        print(f"✓ Server status: {health.status}")
        print(f"✓ Server version: {health.version}")
        print(f"✓ Uptime: {health.uptime} seconds")
        print()
        
        # Get help information
        print("3. Getting help information...")
        help_info = await client.get_help()
        print(f"✓ Help data received: {help_info.get('success', True)}")
        if help_info and 'commands' in help_info:
            commands = help_info['commands']
            print(f"✓ Available commands: {len(commands)}")
            print("✓ Command list:")
            for cmd_name, cmd_info in list(commands.items())[:5]:  # Show first 5 commands
                print(f"  - {cmd_name}: {cmd_info.get('summary', 'No description')}")
            print("...\n")
        else:
            print("✓ Help data structure:", help_info)
            print()
        
        # Create sample chunks via SVO Chunker
        print("4. Creating sample chunks via SVO Chunker...")
        
        # Sample texts
        texts = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            "Vector databases store and retrieve high-dimensional vector embeddings for similarity search and AI applications."
        ]
        
        print("📝 Sample texts to create:")
        for i, text in enumerate(texts, 1):
            print(f"  {i}. {text}")
        print()
        
        all_chunks = []
        for i, text in enumerate(texts):
            print(f"  Processing text {i+1}: {text[:50]}...")
            
            # Create chunks via SVO Chunker
            chunks_response = await client.svo_adapter.chunk_text(
                text=text
            )
            
            print(f"    ✓ Created {len(chunks_response)} chunks")
            if chunks_response:
                chunk = chunks_response[0]
                print(f"    📄 Chunk text: {chunk.text[:80]}...")
                print(f"    🔢 Embedding length: {len(chunk.embedding) if chunk.embedding else 'None'}")
                print(f"    🆔 UUID: {chunk.uuid}")
            all_chunks.extend(chunks_response)
        
        print(f"✓ Total chunks created: {len(all_chunks)}")
        
        # Save chunks to Vector Store
        print("5. Saving chunks to Vector Store...")
        if all_chunks:
            # Convert SVO chunks to Vector Store format
            chunks_data = []
            for chunk in all_chunks:
                chunk_dict = chunk.model_dump()
                # Ensure required fields
                chunk_dict['body'] = chunk_dict.get('body', chunk_dict.get('text', ''))
                chunk_dict['text'] = chunk_dict.get('text', chunk_dict.get('body', ''))
                
                # Remove fields that Vector Store doesn't expect
                chunk_dict.pop('role', None)  # Vector Store doesn't expect role
                chunk_dict.pop('status', None)  # Vector Store doesn't expect status
                chunk_dict.pop('block_type', None)  # Vector Store doesn't expect block_type
                
                chunks_data.append(chunk_dict)
            
            # Try to save to Vector Store
            try:
                print(f"💾 Saving {len(chunks_data)} chunks to Vector Store...")
                response = await client.execute_command("chunk_create", {"chunks": chunks_data})
                if response.get("success"):
                    print(f"✓ Successfully saved {len(chunks_data)} chunks to Vector Store")
                    print(f"📊 Response: {response}")
                else:
                    print(f"⚠ Warning: Could not save chunks to Vector Store: {response.get('error')}")
                    print("  This is expected if Vector Store server has issues")
            except Exception as e:
                print(f"⚠ Warning: Vector Store save failed: {e}")
                print("  This is expected if Vector Store server has issues")
        else:
            print("⚠ No chunks to save")
        
        print()
        
        # Search chunks
        print("6. Searching chunks...")
        search_query = "programming language"
        print(f"🔍 Searching for: '{search_query}'")
        search_results = await client.search_chunks(
            search_str=search_query,
            limit=5
        )
        print(f"✓ Found {len(search_results)} relevant chunks")
        
        for i, chunk in enumerate(search_results, 1):
            print(f"  {i}. {chunk.title or 'No title'}")
            print(f"     Type: {chunk.type.value}")
            print(f"     Language: {chunk.language.value}")
            print(f"     Text: {chunk.text[:100]}...")
            print()
        
        # Search with metadata filter
        print("7. Searching with metadata filter...")
        metadata_filter = {"category": "Programming"}
        print(f"🔍 Searching with metadata filter: {metadata_filter}")
        filtered_results = await client.search_chunks(
            metadata_filter=metadata_filter,
            limit=3
        )
        print(f"✓ Found {len(filtered_results)} programming-related chunks")
        
        for chunk in filtered_results:
            print(f"  - {chunk.title or 'No title'} ({chunk.category})")
        
        print("\n=== Example completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Error during example: {e}")
        raise
    finally:
        # Clean up
        await client.close()
        print("✓ Client connection closed")


async def simple_text_chunk_example():
    """
    Demonstrate creating a simple text chunk.
    
    This example shows the simplified interface for creating
    individual text chunks.
    """
    print("\n=== Simple Text Chunk Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create a simple text chunk via SVO Chunker
        print("Creating a simple text chunk via SVO Chunker...")
        chunks = await client.svo_adapter.chunk_text(
            text="This is a simple text chunk created using the SVO Chunker interface."
        )
        
        if chunks:
            chunk = chunks[0]  # Take first chunk
            print(f"✓ Created chunk with UUID: {chunk.uuid}")
            print(f"✓ Text: {chunk.text}")
            print(f"✓ Embedding dimension: {len(chunk.embedding)}")
            
            # Try to save to Vector Store
            try:
                chunk_dict = chunk.model_dump()
                chunk_dict['body'] = chunk_dict.get('body', chunk_dict.get('text', ''))
                chunk_dict['text'] = chunk_dict.get('text', chunk_dict.get('body', ''))
                
                # Remove fields that Vector Store doesn't expect
                chunk_dict.pop('role', None)  # Vector Store doesn't expect role
                chunk_dict.pop('status', None)  # Vector Store doesn't expect status
                chunk_dict.pop('block_type', None)  # Vector Store doesn't expect block_type
                
                response = await client.execute_command("chunk_create", {"chunks": [chunk_dict]})
                if response.get("success"):
                    print("✓ Successfully saved to Vector Store")
                else:
                    print(f"⚠ Warning: Could not save to Vector Store: {response.get('error')}")
            except Exception as e:
                print(f"⚠ Warning: Vector Store save failed: {e}")
        else:
            print("✗ No chunks created")
        
        print("\n=== Simple example completed! ===")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        await client.close()


async def search_by_text_example():
    """
    Demonstrate the simplified search by text interface.
    
    This example shows how to use the search_by_text method
    which provides a simpler interface for text-based search.
    """
    print("\n=== Search by Text Example ===\n")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Search using the simplified interface
        search_queries = [
            "machine learning",
            "artificial intelligence", 
            "computers learn",
            "subset",
            "intelligence"
        ]
        
        for search_query in search_queries:
            print(f"🔍 Searching for: '{search_query}'")
            results = await client.search_by_text(
                search_str=search_query,
                limit=3
            )
            
            # Also try with lower relevance threshold
            print(f"🔍 Searching for: '{search_query}' (low threshold)")
            results_low = await client.search_chunks(
                search_str=search_query,
                limit=3,
                level_of_relevance=0.0  # Accept any relevance
            )
                
            print(f"✓ Found {len(results)} results (search_by_text):")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title or 'No title'}")
                print(f"     Text: {result.text[:80]}...")
                
            print(f"✓ Found {len(results_low)} results (search_chunks, low threshold):")
            for i, chunk in enumerate(results_low, 1):
                print(f"  {i}. {chunk.title or 'No title'}")
                print(f"     Text: {chunk.text[:80]}...")
            print()
        
        print("=== Search example completed! ===")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        await client.close()


async def main():
    """
    Run all basic usage examples.
    """
    try:
        await basic_usage_example()
        await simple_text_chunk_example()
        await search_by_text_example()
    except Exception as e:
        print(f"Example failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 