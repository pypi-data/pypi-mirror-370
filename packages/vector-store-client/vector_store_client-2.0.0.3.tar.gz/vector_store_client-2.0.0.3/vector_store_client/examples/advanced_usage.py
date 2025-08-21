"""
Advanced usage examples for Vector Store Client.

This module demonstrates advanced features and patterns for using
the Vector Store client, including batch operations, error handling,
and complex search scenarios with real chunking.

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
    SearchResult,
    ChunkType,
    LanguageEnum,
    ChunkStatus,
    SearchOrder,
    EmbeddingModel,
)
from vector_store_client.exceptions import (
    VectorStoreError,
    ConnectionError,
    ValidationError,
    ServerError,
    SVOError,
)
from vector_store_client.utils import (
    setup_logging,
    process_batch_concurrent,
    retry_with_backoff,
    generate_uuid,
)


async def batch_operations_example():
    """
    Demonstrate efficient batch operations for large datasets with real chunking.
    """
    print("=== Batch Operations Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create large batch of texts for chunking
        sample_texts = [
            "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions.",
            "Vector databases store and retrieve high-dimensional vector embeddings for similarity search and AI applications. They are essential for modern AI systems that require semantic search capabilities.",
            "Natural language processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and human language. It enables machines to understand, interpret, and generate human language.",
            "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision and natural language processing.",
            "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data.",
            "Cloud computing provides on-demand access to computing resources over the internet. It enables scalable and flexible deployment of applications and services.",
            "DevOps is a set of practices that combines software development and IT operations. It aims to shorten the development lifecycle and provide continuous delivery of high-quality software.",
            "Microservices architecture is a design pattern where applications are built as a collection of loosely coupled, independently deployable services. Each service implements a specific business capability.",
            "Containerization is a lightweight alternative to full machine virtualization that involves encapsulating an application in a container with its own operating environment."
        ]
        
        # Process texts through SVO chunker in batches
        batch_size = 3
        all_chunks = []
        total_created = 0
        
        print(f"Processing {len(sample_texts)} texts through SVO chunker...")
        
        for i in range(0, len(sample_texts), batch_size):
            batch_texts = sample_texts[i:i + batch_size]
            batch_chunks = []
            
            for j, text in enumerate(batch_texts):
                print(f"  Chunking text {i + j + 1}: {text[:50]}...")
                
                try:
                    # Use real SVO chunker
                    chunks_response = await client.svo_adapter.chunk_text(
                        text=text
                    )
                    
                    # Add metadata to chunks
                    for chunk in chunks_response:
                        chunk.source_id = generate_uuid()
                        chunk.title = f"Document {i + j + 1}"
                        chunk.category = f"category_{(i + j) % 5}"
                        chunk.tags = [f"tag_{i + j}", f"batch_{(i + j) // 3}"]
                        # Use block_meta instead of metadata
                        chunk.block_meta = {
                            "batch_id": (i + j) // 3,
                            "text_index": i + j,
                            "chunk_index": chunks_response.index(chunk)
                        }
                    
                    batch_chunks.extend(chunks_response)
                    print(f"    ✓ Created {len(chunks_response)} chunks")
                    
                except SVOError as e:
                    print(f"    ❌ SVO chunking failed: {e}")
                except Exception as e:
                    print(f"    ❌ Unexpected error: {e}")
            
            # Save batch to vector store
            if batch_chunks:
                try:
                    result = await client.create_chunks(batch_chunks)
                    batch_count = result.created_count or 0
                    total_created += batch_count
                    print(f"  ✓ Saved batch {i // batch_size + 1}: {batch_count} chunks")
                    all_chunks.extend(batch_chunks)
                except Exception as e:
                    print(f"  ❌ Failed to save batch: {e}")
        
        print(f"Total chunks created and saved: {total_created}")
        
        # Search with complex filters
        search_filter = {
            "type": "DOC_BLOCK",
            "language": "EN",
            "category": "category_0",
            "tags": ["tag_0"]
        }
        
        results = await client.search_chunks(
            search_str="programming language",
            metadata_filter=search_filter,
            limit=10
        )
        
        print(f"Found {len(results)} matching chunks")
        
    finally:
        await client.close()


async def error_handling_example():
    """
    Demonstrate comprehensive error handling patterns with real chunking.
    """
    print("=== Error Handling Example ===")
    
    # Setup detailed logging
    logger = setup_logging(level="DEBUG")
    
    try:
        client = await VectorStoreClient.create("http://localhost:8007")
        
        # Test various error scenarios
        await test_validation_errors(client)
        await test_connection_errors(client)
        await test_server_errors(client)
        await test_svo_errors(client)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'client' in locals():
            await client.close()


async def test_validation_errors(client: VectorStoreClient):
    """Test validation error handling."""
    print("Testing validation errors...")
    
    try:
        # Invalid chunking parameters
        await client.svo_adapter.chunk_text(
            text=""  # Empty text
        )
    except ValidationError as e:
        print(f"Validation error caught: {e}")
        print(f"Field errors: {e.field_errors}")
    
    try:
        # Invalid search parameters
        await client.search_chunks(limit=-1)
    except ValidationError as e:
        print(f"Search validation error: {e}")


async def test_connection_errors(client: VectorStoreClient):
    """Test connection error handling."""
    print("Testing connection errors...")
    
    try:
        # Try to connect to non-existent server
        bad_client = await VectorStoreClient.create("http://localhost:9999")
        await bad_client.health_check()
    except ConnectionError as e:
        print(f"Connection error caught: {e}")
        print(f"Base URL: {e.base_url}")
        print(f"Timeout: {e.timeout}")


async def test_server_errors(client: VectorStoreClient):
    """Test server error handling."""
    print("Testing server errors...")
    
    try:
        # Try invalid command
        await client._execute_command("invalid_command")
    except ServerError as e:
        print(f"Server error caught: {e}")
        print(f"Status code: {e.status_code}")
        print(f"Server message: {e.server_message}")


async def test_svo_errors(client: VectorStoreClient):
    """Test SVO service error handling."""
    print("Testing SVO errors...")
    
    try:
        # Try chunking with invalid parameters
        await client.svo_adapter.chunk_text(
            text="Test text"
        )
    except SVOError as e:
        print(f"SVO error caught: {e}")
    except ValidationError as e:
        print(f"SVO validation error: {e}")


async def complex_search_example():
    """
    Demonstrate complex search scenarios with real chunked data.
    """
    print("=== Complex Search Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create diverse test data using real chunking
        await create_test_data_with_chunking(client)
        
        # Complex search scenarios
        await search_by_multiple_criteria(client)
        await search_with_relevance_threshold(client)
        await search_by_metadata_patterns(client)
        
    finally:
        await client.close()


async def create_test_data_with_chunking(client: VectorStoreClient):
    """Create diverse test data using real chunking."""
    test_texts = [
        # Technical documents
        "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms and has a large standard library.",
        
        "Machine learning algorithms require large datasets for training and validation. They use statistical techniques to identify patterns and make predictions based on data.",
        
        # Code examples
        "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# This function calculates the nth Fibonacci number using recursion.",
        
        # Questions and discussions
        "How do I implement a binary search tree in Python? I need to create a data structure that supports efficient insertion, deletion, and search operations.",
        
        # Documentation
        "Vector databases are specialized databases designed to store and retrieve high-dimensional vector embeddings. They are essential for semantic search, recommendation systems, and AI applications that require similarity search capabilities."
    ]
    
    all_chunks = []
    
    for i, text in enumerate(test_texts):
        print(f"  Chunking text {i + 1}: {text[:50]}...")
        
        try:
            # Use real chunking with different parameters
            chunk_type = "DocBlock" if i < 2 else "CodeBlock" if i == 2 else "Message" if i == 3 else "DocBlock"
            
            chunks_response = await client.svo_adapter.chunk_text(
                text=text
            )
            
            # Add metadata
            for j, chunk in enumerate(chunks_response):
                chunk.source_id = generate_uuid()
                chunk.title = f"Document {i + 1} - Part {j + 1}"
                chunk.category = "programming" if i < 2 else "ai" if i == 1 else "code" if i == 2 else "question" if i == 3 else "documentation"
                chunk.tags = ["python", "programming"] if i < 2 else ["machine-learning", "ai"] if i == 1 else ["python", "code", "recursion"] if i == 2 else ["python", "data-structures", "question"] if i == 3 else ["vector-databases", "documentation"]
                # Use block_meta instead of metadata
                chunk.block_meta = {
                    "difficulty": "beginner" if i < 2 else "intermediate" if i == 1 else "advanced" if i == 2 else "beginner" if i == 3 else "intermediate",
                    "topic": "programming" if i < 2 else "ai" if i == 1 else "algorithms" if i == 2 else "data-structures" if i == 3 else "databases",
                    "text_index": i,
                    "chunk_index": j
                }
            
            all_chunks.extend(chunks_response)
            print(f"    ✓ Created {len(chunks_response)} chunks")
            
        except Exception as e:
            print(f"    ❌ Failed to chunk text {i + 1}: {e}")
    
    # Save all chunks to vector store
    if all_chunks:
        try:
            result = await client.create_chunks(all_chunks)
            print(f"Created {result.created_count or 0} test chunks")
        except Exception as e:
            print(f"Failed to save chunks: {e}")


async def search_by_multiple_criteria(client: VectorStoreClient):
    """Search using multiple criteria and filters."""
    print("\n--- Search by Multiple Criteria ---")
    
    # Search for programming content with specific tags
    search_filter = {
        "type": "DOC_BLOCK",
        "category": "programming",
        "tags": ["python"]
    }
    
    results = await client.search_chunks(
        search_str="programming language",
        metadata_filter=search_filter,
        limit=5
    )
    
    print(f"Found {len(results)} programming documents:")
    for result in results:
        print(f"  - {result.title} (relevance: {getattr(result, 'relevance_score', 0.0):.3f})")


async def search_with_relevance_threshold(client: VectorStoreClient):
    """Search with minimum relevance threshold."""
    print("\n--- Search with Relevance Threshold ---")
    
    results = await client.search_chunks(
        search_str="machine learning algorithms",
        level_of_relevance=0.7,  # Only results with 70%+ relevance
        limit=10
    )
    
    print(f"Found {len(results)} highly relevant results:")
    for result in results:
        print(f"  - {getattr(result, 'title', 'No title')} (relevance: {getattr(result, 'relevance_score', 0.0):.3f})")


async def search_by_metadata_patterns(client: VectorStoreClient):
    """Search using metadata patterns."""
    print("\n--- Search by Metadata Patterns ---")
    
    # Search for beginner-level content
    metadata_filter = {
        "block_meta.difficulty": "beginner",
        "type": "doc_block"
    }
    
    results = await client.search_chunks(
        search_str="programming",
        metadata_filter=metadata_filter,
        limit=5
    )
    
    print(f"Found {len(results)} beginner-level programming content:")
    for result in results:
        difficulty = getattr(result, 'block_meta', {}).get("difficulty", "unknown")
        print(f"  - {getattr(result, 'title', 'No title')} (difficulty: {difficulty})")


async def retry_pattern_example():
    """
    Demonstrate retry patterns for unreliable operations with chunking.
    """
    print("=== Retry Pattern Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Define operation that might fail
        async def unreliable_chunking_operation():
            # Simulate unreliable chunking operation
            import random
            if random.random() < 0.7:  # 70% chance of failure
                raise SVOError("Simulated SVO service error")
            
            # Real chunking operation
            chunks = await client.svo_adapter.chunk_text(
                text="This is a test text for retry pattern demonstration."
            )
            return f"Successfully created {len(chunks)} chunks"
        
        # Use retry with backoff
        result = await retry_with_backoff(
            unreliable_chunking_operation,
            max_retries=3,
            base_delay=1.0,
            backoff_factor=2.0,
            exceptions=(SVOError, ConnectionError,)
        )
        
        print(f"Retry result: {result}")
        
    finally:
        await client.close()


async def performance_monitoring_example():
    """
    Demonstrate performance monitoring and metrics with real chunking.
    """
    print("=== Performance Monitoring Example ===")
    
    import time
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Monitor operation performance
        start_time = time.time()
        
        # Perform multiple operations
        health = await client.health_check()
        print(f"Health check took: {time.time() - start_time:.3f}s")
        
        # Monitor chunking performance
        test_text = "Vector databases are specialized databases designed to store and retrieve high-dimensional vector embeddings. They are essential for semantic search, recommendation systems, and AI applications that require similarity search capabilities. These databases use various indexing techniques to enable fast similarity search in high-dimensional spaces."
        
        chunking_start = time.time()
        chunks = await client.svo_adapter.chunk_text(
            text=test_text
        )
        chunking_time = time.time() - chunking_start
        
        print(f"Chunking took: {chunking_time:.3f}s")
        print(f"Created {len(chunks)} chunks")
        print(f"Average time per chunk: {chunking_time / len(chunks):.3f}s" if chunks else "No chunks created")
        
        # Monitor search performance
        search_start = time.time()
        results = await client.search_chunks(search_str="vector databases", limit=50)
        search_time = time.time() - search_start
        
        print(f"Search took: {search_time:.3f}s")
        print(f"Found {len(results)} results")
        if len(results) > 0:
            print(f"Average time per result: {search_time / len(results):.3f}s")
        else:
            print("No results found")
        
        # Monitor batch creation performance
        batch_start = time.time()
        
        # Create multiple texts for batch processing
        batch_texts = [
            f"Performance test text {i} with detailed information about various topics including programming, machine learning, and data science."
            for i in range(5)
        ]
        
        all_batch_chunks = []
        for text in batch_texts:
            try:
                chunks_response = await client.svo_adapter.chunk_text(
                    text=text
                )
                all_batch_chunks.extend(chunks_response)
            except Exception as e:
                print(f"Failed to chunk text: {e}")
        
        if all_batch_chunks:
            result = await client.create_chunks(all_batch_chunks)
            batch_time = time.time() - batch_start
            
            created_count = result.created_count or 0
            print(f"Batch processing took: {batch_time:.3f}s")
            print(f"Created {created_count} chunks")
            print(f"Average time per chunk: {batch_time / created_count:.3f}s" if created_count > 0 else "No chunks created")
        
    finally:
        await client.close()


async def direct_embedding_example():
    """
    Demonstrate direct embedding operations without chunking.
    """
    print("=== Direct Embedding Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Test texts for embedding
        test_texts = [
            "Python is a high-level programming language.",
            "Machine learning algorithms require large datasets.",
            "Vector databases store high-dimensional embeddings.",
            "Natural language processing enables text understanding.",
            "Deep learning uses neural networks with multiple layers."
        ]
        
        print("1. Generating embeddings for individual texts...")
        
        # Generate embeddings one by one
        embeddings = []
        for i, text in enumerate(test_texts):
            print(f"  Embedding text {i + 1}: {text[:50]}...")
            
            try:
                # Use direct embedding function
                embed_response = await client.embed_text(
                    text=text
                )
                
                print(f"    ✓ Generated {len(embed_response.embedding)}-dimensional embedding")
                print(f"    📊 Model: {embed_response.model}")
                print(f"    🔢 Dimension: {embed_response.dimension}")
                
                embeddings.append(embed_response.embedding)
                
            except Exception as e:
                print(f"    ❌ Failed to embed text {i + 1}: {e}")
        
        print(f"\n2. Batch embedding generation...")
        
        try:
            # Generate embeddings in batch
            batch_embeddings = await client.embed_batch(
                texts=test_texts
            )
            
            print(f"  ✓ Generated {len(batch_embeddings)} embeddings in batch")
            for i, embed_response in enumerate(batch_embeddings):
                print(f"    Text {i + 1}: {len(embed_response.embedding)} dimensions")
                
        except Exception as e:
            print(f"  ❌ Batch embedding failed: {e}")
        
        print(f"\n3. Getting available embedding models...")
        
        try:
            models_response = await client.get_embedding_models()
            print(f"  ✓ Available models: {len(models_response.models)}")
            print(f"  📋 Default model: {models_response.default_model}")
            print(f"  🔧 Model configurations: {len(models_response.model_configs)}")
            
        except Exception as e:
            print(f"  ❌ Failed to get models: {e}")
        
        print(f"\n4. Creating chunks with automatic embeddings...")
        
        try:
            # Create chunks with automatic embedding generation
            chunk = await client.create_chunk_with_embedding(
                text="This is a test chunk with automatic embedding generation."
            )
            
            print(f"  ✓ Created chunk: {chunk.uuid}")
            print(f"  📄 Text: {chunk.text[:50]}...")
            print(f"  🔢 Embedding: {len(chunk.embedding)} dimensions")
            print(f"  🏷️ Type: {chunk.type}")
            
        except Exception as e:
            print(f"  ❌ Failed to create chunk with embedding: {e}")
        
        print(f"\n5. Search by vector directly...")
        
        if embeddings:
            try:
                # Use the first embedding for vector search
                search_vector = embeddings[0]
                print(f"  🔍 Searching with {len(search_vector)}-dimensional vector...")
                
                results = await client.search_by_vector(
                    embedding=search_vector,
                    limit=5,
                    level_of_relevance=0.5
                )
                
                print(f"  ✓ Found {len(results)} results")
                for i, result in enumerate(results):
                    print(f"    {i + 1}. {result.text[:50]}... (relevance: {getattr(result, 'relevance_score', 0.0):.3f})")
                    
            except Exception as e:
                print(f"  ❌ Vector search failed: {e}")
        
        print(f"\n6. Performance comparison...")
        
        import time
        
        # Test individual embedding performance
        start_time = time.time()
        for text in test_texts[:3]:  # Test first 3 texts
            await client.embed_text(text)
        individual_time = time.time() - start_time
        
        # Test batch embedding performance
        start_time = time.time()
        await client.embed_batch(test_texts[:3])
        batch_time = time.time() - start_time
        
        print(f"  ⏱️ Individual embedding time: {individual_time:.3f}s")
        print(f"  ⏱️ Batch embedding time: {batch_time:.3f}s")
        print(f"  📈 Speedup: {individual_time / batch_time:.2f}x faster in batch")
        
    finally:
        await client.close()


async def main():
    """Run all advanced usage examples."""
    print("Vector Store Client - Advanced Usage Examples with Real Chunking")
    print("=" * 60)
    
    try:
        await batch_operations_example()
        await error_handling_example()
        await complex_search_example()
        await retry_pattern_example()
        await performance_monitoring_example()
        await direct_embedding_example()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 