"""
Batch operations examples for Vector Store Client.

This module demonstrates efficient batch processing patterns for
large datasets, including chunk creation, search, and deletion.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import time
import uuid
from typing import List, Dict, Any

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
)
from vector_store_client.utils import process_batch_concurrent, setup_logging


async def large_batch_creation_example():
    """
    Demonstrate efficient creation of large batches of chunks.
    """
    print("=== Large Batch Creation Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Generate large dataset
        total_chunks = 1000
        batch_size = 50
        
        print(f"Creating {total_chunks} chunks in batches of {batch_size}")
        
        start_time = time.time()
        total_created = 0
        
        for batch_num in range(0, total_chunks, batch_size):
            batch_start = time.time()
            
            # Create batch of chunks
            chunks = []
            for i in range(batch_num, min(batch_num + batch_size, total_chunks)):
                chunk = SemanticChunk(
                    body=f"Document content for chunk {i}. This is a comprehensive document about topic {i} with detailed information and examples.",
                    text=f"Document content for chunk {i}. This is a comprehensive document about topic {i} with detailed information and examples.",
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    title=f"Document {i}",
                    category=f"category_{i % 10}",
                    tags=[f"tag_{i}", f"batch_{batch_num // batch_size}"],
                    metadata={
                        "batch_id": batch_num // batch_size,
                        "chunk_index": i,
                        "created_timestamp": time.time()
                    },
                    source_id=str(uuid.uuid4()),
                    embedding=[0.1] * 384
                )
                chunks.append(chunk)
            
            # Create batch
            result = await client.create_chunks(chunks)
            batch_time = time.time() - batch_start
            
            total_created += result.created_count
            print(f"Batch {batch_num // batch_size + 1}: {result.created_count} chunks in {batch_time:.2f}s")
        
        total_time = time.time() - start_time
        print(f"\nTotal: {total_created} chunks created in {total_time:.2f}s")
        print(f"Average: {total_created / total_time:.1f} chunks/second")
        
    finally:
        await client.close()


async def parallel_batch_processing_example():
    """
    Demonstrate parallel processing of batches for improved performance.
    """
    print("=== Parallel Batch Processing Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create multiple batches for parallel processing
        batches = []
        num_batches = 5
        chunks_per_batch = 20
        
        for batch_id in range(num_batches):
            batch_chunks = []
            for i in range(chunks_per_batch):
                chunk = SemanticChunk(
                    body=f"Parallel batch {batch_id} chunk {i} content",
                    text=f"Parallel batch {batch_id} chunk {i} content",
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    title=f"Parallel Chunk {batch_id}-{i}",
                    category=f"parallel_{batch_id}",
                    tags=[f"parallel", f"batch_{batch_id}"],
                    metadata={"batch_id": batch_id, "parallel": True},
                    source_id=str(uuid.uuid4()),
                    embedding=[0.1] * 384
                )
                batch_chunks.append(chunk)
            batches.append(batch_chunks)
        
        # Process batches in parallel
        start_time = time.time()
        
        async def process_batch(batch_chunks: List[SemanticChunk], batch_id: int):
            """Process a single batch."""
            batch_start = time.time()
            result = await client.create_chunks(batch_chunks)
            batch_time = time.time() - batch_start
            print(f"Parallel batch {batch_id}: {result.created_count} chunks in {batch_time:.2f}s")
            return result
        
        # Create tasks for parallel execution
        tasks = [
            process_batch(batch, i) 
            for i, batch in enumerate(batches)
        ]
        
        # Execute all batches in parallel
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        total_created = sum(r.created_count for r in results)
        
        print(f"\nParallel processing: {total_created} chunks in {total_time:.2f}s")
        print(f"Average: {total_created / total_time:.1f} chunks/second")
        
    finally:
        await client.close()


async def batch_search_example():
    """
    Demonstrate efficient batch searching with pagination.
    """
    print("=== Batch Search Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # First, create some test data
        await create_test_data_for_search(client)
        
        # Perform batch searches
        search_queries = [
            "programming language",
            "machine learning",
            "data structures",
            "algorithms",
            "web development"
        ]
        
        print(f"Performing batch searches for {len(search_queries)} queries")
        
        start_time = time.time()
        all_results = []
        
        for query in search_queries:
            query_start = time.time()
            
            # Search with pagination
            results = await client.search_chunks(
                search_str=query,
                limit=20,
                offset=0
            )
            
            query_time = time.time() - query_start
            print(f"Query '{query}': {len(results)} results in {query_time:.2f}s")
            
            all_results.extend(results)
        
        total_time = time.time() - start_time
        print(f"\nTotal search time: {total_time:.2f}s")
        print(f"Total results: {len(all_results)}")
        print(f"Average results per query: {len(all_results) / len(search_queries):.1f}")
        
    finally:
        await client.close()


async def create_test_data_for_search(client: VectorStoreClient):
    """Create test data for search examples."""
    test_chunks = [
        # Programming content
        SemanticChunk(
            body="Python is a versatile programming language used for web development, data science, and automation.",
            text="Python is a versatile programming language used for web development, data science, and automation.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Python Programming",
            category="programming",
            tags=["python", "programming", "web"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        SemanticChunk(
            body="JavaScript is essential for modern web development and interactive user interfaces.",
            text="JavaScript is essential for modern web development and interactive user interfaces.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="JavaScript Web Development",
            category="programming",
            tags=["javascript", "web", "frontend"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        # Machine learning content
        SemanticChunk(
            body="Machine learning algorithms can be supervised, unsupervised, or reinforcement learning.",
            text="Machine learning algorithms can be supervised, unsupervised, or reinforcement learning.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Machine Learning Types",
            category="ai",
            tags=["machine-learning", "algorithms", "ai"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        # Data structures content
        SemanticChunk(
            body="Binary trees are hierarchical data structures used for efficient searching and sorting.",
            text="Binary trees are hierarchical data structures used for efficient searching and sorting.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Binary Trees",
            category="algorithms",
            tags=["data-structures", "trees", "algorithms"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        SemanticChunk(
            body="Hash tables provide O(1) average time complexity for insertions and lookups.",
            text="Hash tables provide O(1) average time complexity for insertions and lookups.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Hash Tables",
            category="algorithms",
            tags=["data-structures", "hash-tables", "algorithms"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        )
    ]
    
    result = await client.create_chunks(test_chunks)
    print(f"Created {result.created_count} test chunks for search")


async def batch_deletion_example():
    """
    Demonstrate efficient batch deletion of chunks.
    """
    print("=== Batch Deletion Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # First, create some test data to delete
        await create_test_data_for_deletion(client)
        
        # Find chunks to delete
        print("Finding chunks to delete...")
        
        # Delete by category
        categories_to_delete = ["temporary", "test"]
        
        for category in categories_to_delete:
            print(f"Deleting chunks with category: {category}")
            
            delete_start = time.time()
            result = await client.delete_chunks(metadata_filter={"category": category})
            delete_time = time.time() - delete_start
            
            print(f"Deleted {result.deleted_count} chunks in {delete_time:.2f}s")
        
        # Delete by tags
        tags_to_delete = ["batch_test"]
        
        for tag in tags_to_delete:
            print(f"Deleting chunks with tag: {tag}")
            
            delete_start = time.time()
            result = await client.delete_chunks(metadata_filter={"tags": [tag]})
            delete_time = time.time() - delete_start
            
            print(f"Deleted {result.deleted_count} chunks in {delete_time:.2f}s")
        
        # Find and delete duplicates
        print("Finding duplicate UUIDs...")
        duplicates = await client.find_duplicate_uuids()
        
        if duplicates.duplicates:
            print(f"Found {duplicates.total_duplicates} duplicate UUIDs in {duplicates.total_groups} groups")
            
            # Delete duplicates
            for group in duplicates.duplicates:
                uuids = group.get("uuids", [])
                if len(uuids) > 1:
                    # Keep first, delete rest
                    uuids_to_delete = uuids[1:]
                    print(f"Deleting {len(uuids_to_delete)} duplicates from group")
                    
                    delete_start = time.time()
                    result = await client.force_delete_by_uuids(uuids_to_delete)
                    delete_time = time.time() - delete_start
                    
                    print(f"Deleted {result.deleted_count} duplicates in {delete_time:.2f}s")
        else:
            print("No duplicate UUIDs found")
        
    finally:
        await client.close()


async def create_test_data_for_deletion(client: VectorStoreClient):
    """Create test data for deletion examples."""
    test_chunks = [
        # Temporary chunks
        SemanticChunk(
            body="This is a temporary chunk that will be deleted",
            text="This is a temporary chunk that will be deleted",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Temporary Document",
            category="temporary",
            tags=["temporary", "batch_test"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        SemanticChunk(
            body="Another temporary chunk for testing deletion",
            text="Another temporary chunk for testing deletion",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Another Temporary",
            category="temporary",
            tags=["temporary", "batch_test"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        # Test chunks
        SemanticChunk(
            body="Test chunk for batch operations",
            text="Test chunk for batch operations",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Test Document",
            category="test",
            tags=["test", "batch_test"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        ),
        # Permanent chunks (should not be deleted)
        SemanticChunk(
            body="This is a permanent chunk that should not be deleted",
            text="This is a permanent chunk that should not be deleted",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Permanent Document",
            category="permanent",
            tags=["permanent", "important"],
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        )
    ]
    
    result = await client.create_chunks(test_chunks)
    print(f"Created {result.created_count} test chunks for deletion")


async def performance_comparison_example():
    """
    Compare performance of different batch processing approaches.
    """
    print("=== Performance Comparison Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Test data size
        total_chunks = 200
        chunk_size = 20
        
        print(f"Testing with {total_chunks} chunks in batches of {chunk_size}")
        
        # Approach 1: Sequential processing
        print("\n1. Sequential Processing:")
        start_time = time.time()
        await sequential_processing(client, total_chunks, chunk_size)
        sequential_time = time.time() - start_time
        print(f"Sequential time: {sequential_time:.2f}s")
        
        # Approach 2: Parallel processing
        print("\n2. Parallel Processing:")
        start_time = time.time()
        await parallel_processing(client, total_chunks, chunk_size)
        parallel_time = time.time() - start_time
        print(f"Parallel time: {parallel_time:.2f}s")
        
        # Performance comparison
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        print(f"\nPerformance Comparison:")
        print(f"Speedup: {speedup:.2f}x")
        print(f"Time saved: {sequential_time - parallel_time:.2f}s")
        
    finally:
        await client.close()


async def sequential_processing(client: VectorStoreClient, total_chunks: int, batch_size: int):
    """Process chunks sequentially."""
    for i in range(0, total_chunks, batch_size):
        chunks = create_test_chunks(i, min(i + batch_size, total_chunks))
        await client.create_chunks(chunks)


async def parallel_processing(client: VectorStoreClient, total_chunks: int, batch_size: int):
    """Process chunks in parallel."""
    tasks = []
    for i in range(0, total_chunks, batch_size):
        chunks = create_test_chunks(i, min(i + batch_size, total_chunks))
        task = client.create_chunks(chunks)
        tasks.append(task)
    
    await asyncio.gather(*tasks)


def create_test_chunks(start_idx: int, end_idx: int) -> List[SemanticChunk]:
    """Create test chunks for the given range."""
    chunks = []
    for i in range(start_idx, end_idx):
        chunk = SemanticChunk(
            body=f"Performance test chunk {i}",
            text=f"Performance test chunk {i}",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title=f"Test Chunk {i}",
            category="performance_test",
            tags=["performance", "test"],
            metadata={"test_index": i},
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384
        )
        chunks.append(chunk)
    return chunks


async def main():
    """Run all batch operation examples."""
    print("Vector Store Client - Batch Operations Examples")
    print("=" * 50)
    
    try:
        await large_batch_creation_example()
        await parallel_batch_processing_example()
        await batch_search_example()
        await batch_deletion_example()
        await performance_comparison_example()
        
        print("\nAll batch operation examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 