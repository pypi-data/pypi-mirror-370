"""
Examples of using high-level utility methods with real services.

This module demonstrates how to use the utility methods with real
Vector Store services, including text chunk creation, search methods,
batch operations, and analysis functions.

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
from vector_store_client.models import SemanticChunk
from vector_store_client.types import ChunkType, LanguageEnum
from vector_store_client.utils import generate_uuid


async def basic_usage_example():
    """Basic usage example with real services."""
    print("=== Basic Usage Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create chunks manually (since create_chunks_from_texts doesn't exist)
        texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand text."
        ]
        
        chunks = []
        for i, text in enumerate(texts):
            chunk = SemanticChunk(
                body=text,
                text=text,
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                source_id=generate_uuid(),
                category="machine-learning",
                embedding=[0.1] * 384  # Placeholder embedding
            )
            chunks.append(chunk)
        
        # Create chunks in vector store
        create_result = await client.create_chunks(chunks)
        print(f"Created {len(create_result.uuids)} chunks")
        
        # Search by text using search_chunks
        results = await client.search_chunks(
            search_str="machine learning",
            limit=5
        )
        
        print(f"Found {len(results)} relevant chunks")
        
        # Search by metadata
        project_chunks = await client.search_chunks(
            metadata_filter={"source_id": "ml-docs"}
        )
        
        print(f"Found {len(project_chunks)} project chunks")
        
    except Exception as e:
        print(f"⚠️  Error in basic usage: {e}")


async def advanced_usage_example():
    """Advanced usage example with complex queries."""
    print("\n=== Advanced Usage Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Search with metadata filter (equivalent to AST query)
        metadata_filter = {
            "type": "DOC_BLOCK",
            "language": "en"
        }
        
        results = await client.search_chunks(
            metadata_filter=metadata_filter,
            limit=10
        )
        
        print(f"Found {len(results)} English documents")
        
        # Multiple searches with different queries
        queries = [
            {"search_str": "machine learning", "limit": 5},
            {"search_str": "deep learning", "limit": 5},
            {"search_str": "neural networks", "limit": 5}
        ]
        
        batch_results = []
        for query in queries:
            try:
                result = await client.search_chunks(**query)
                batch_results.append(result)
                print(f"Query '{query['search_str']}': {len(result)} results")
            except Exception as e:
                print(f"Query '{query['search_str']}' failed: {e}")
                batch_results.append([])
        
        total_results = sum(len(results) for results in batch_results)
        print(f"Total results across all queries: {total_results}")
        
    except Exception as e:
        print(f"⚠️  Error in advanced usage: {e}")


async def batch_operations_example():
    """Batch operations example."""
    print("\n=== Batch Operations Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create multiple batches
        batch_size = 10
        num_batches = 3
        
        for batch_num in range(num_batches):
            chunks = []
            for i in range(batch_size):
                chunk = SemanticChunk(
                    body=f"Batch {batch_num} chunk {i} content about data science and analytics.",
                    text=f"Batch {batch_num} chunk {i} content about data science and analytics.",
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    source_id=generate_uuid(),
                    category="data-science",
                    embedding=[0.1] * 384
                )
                chunks.append(chunk)
            
            # Create batch
            create_result = await client.create_chunks(chunks)
            print(f"Batch {batch_num + 1}: Created {len(create_result.uuids)} chunks")
        
        # Batch search
        search_queries = [
            "data science",
            "analytics",
            "machine learning"
        ]
        
        print("\nBatch search results:")
        for query in search_queries:
            results = await client.search_chunks(search_str=query, limit=5)
            print(f"'{query}': {len(results)} results")
        
        # Batch deletion
        all_chunks = await client.search_chunks(limit=50)
        if all_chunks:
            # Delete chunks from first batch
            batch_uuids = [chunk.uuid for chunk in all_chunks if chunk.source_id == "batch-0"]
            if batch_uuids:
                delete_result = await client.delete_chunks(uuids=batch_uuids)
                print(f"Deleted {delete_result.deleted_count} chunks from batch 0")
        
    except Exception as e:
        print(f"⚠️  Error in batch operations: {e}")


async def statistics_and_analysis_example():
    """Statistics and analysis example."""
    print("\n=== Statistics and Analysis Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Get basic statistics
        health = await client.health_check()
        print(f"Server status: {health.status}")
        print(f"Version: {health.version}")
        print(f"Uptime: {health.uptime}s")
        
        # Get help information
        help_info = await client.get_help()
        print(f"Available commands: {len(help_info.get('data', {}).get('commands', []))}")
        
        # Search for chunks and analyze
        all_chunks = await client.search_chunks(limit=100)
        print(f"Total chunks in store: {len(all_chunks)}")
        
        if all_chunks:
            # Analyze chunk types
            type_counts = {}
            language_counts = {}
            source_counts = {}
            
            for chunk in all_chunks:
                # Count by type
                chunk_type = getattr(chunk, 'type', 'unknown')
                type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
                
                # Count by language
                language = getattr(chunk, 'language', 'unknown')
                language_counts[language] = language_counts.get(language, 0) + 1
                
                # Count by source
                source = getattr(chunk, 'source_id', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print("\nChunk Analysis:")
            print(f"Types: {type_counts}")
            print(f"Languages: {language_counts}")
            print(f"Sources: {source_counts}")
        
    except Exception as e:
        print(f"⚠️  Error in statistics and analysis: {e}")


async def export_import_example():
    """Export and import example."""
    print("\n=== Export and Import Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Export chunks (simulate by getting all chunks)
        print("Exporting chunks...")
        all_chunks = await client.search_chunks(limit=50)
        
        if all_chunks:
            # Convert to exportable format
            export_data = []
            for chunk in all_chunks:
                export_chunk = {
                    "uuid": chunk.uuid,
                    "body": chunk.body,
                    "text": chunk.text,
                    "type": getattr(chunk, 'type', 'unknown'),
                    "language": getattr(chunk, 'language', 'unknown'),
                    "source_id": getattr(chunk, 'source_id', 'unknown'),
                    "category": getattr(chunk, 'category', 'unknown'),
                    "metadata": getattr(chunk, 'metadata', {})
                }
                export_data.append(export_chunk)
            
            print(f"Exported {len(export_data)} chunks")
            
            # Simulate import by creating new chunks
            print("Importing chunks to new source...")
            imported_chunks = []
            for chunk_data in export_data[:5]:  # Import first 5 as example
                new_chunk = SemanticChunk(
                    body=chunk_data['body'],
                    text=chunk_data['text'],
                    type=chunk_data['type'],
                    language=chunk_data['language'],
                    source_id=f"imported-{chunk_data['source_id']}",
                    category=chunk_data['category'],
                    metadata=chunk_data['metadata'],
                    embedding=[0.1] * 384
                )
                imported_chunks.append(new_chunk)
            
            if imported_chunks:
                import_result = await client.create_chunks(imported_chunks)
                print(f"Imported {len(import_result.uuids)} chunks")
        
    except Exception as e:
        print(f"⚠️  Error in export/import: {e}")


async def utility_functions_example():
    """Utility functions example."""
    print("\n=== Utility Functions Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create test data
        test_chunks = [
            SemanticChunk(
                body="Python programming language is widely used for data science.",
                text="Python programming language is widely used for data science.",
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                source_id=generate_uuid(),
                category="programming",
                embedding=[0.1] * 384
            ),
            SemanticChunk(
                body="JavaScript is essential for web development.",
                text="JavaScript is essential for web development.",
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                source_id=generate_uuid(),
                category="programming",
                embedding=[0.2] * 384
            )
        ]
        
        # Create chunks
        create_result = await client.create_chunks(test_chunks)
        print(f"Created {len(create_result.uuids)} test chunks")
        
        # Search and format results
        results = await client.search_chunks(search_str="programming", limit=10)
        
        print(f"\nSearch Results ({len(results)} found):")
        for i, chunk in enumerate(results, 1):
            print(f"{i}. {chunk.body[:50]}...")
            print(f"   UUID: {chunk.uuid}")
            print(f"   Type: {getattr(chunk, 'type', 'unknown')}")
            print(f"   Source: {getattr(chunk, 'source_id', 'unknown')}")
            print()
        
    except Exception as e:
        print(f"⚠️  Error in utility functions: {e}")


async def performance_optimization_example():
    """Performance optimization example."""
    print("\n=== Performance Optimization Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        import time
        
        # Measure search performance
        print("Measuring search performance...")
        
        search_queries = [
            "programming",
            "data science",
            "machine learning",
            "web development"
        ]
        
        for query in search_queries:
            start_time = time.time()
            results = await client.search_chunks(search_str=query, limit=10)
            end_time = time.time()
            
            print(f"'{query}': {len(results)} results in {end_time - start_time:.3f}s")
        
        # Measure batch creation performance
        print("\nMeasuring batch creation performance...")
        
        batch_sizes = [5, 10, 20]
        for batch_size in batch_sizes:
            chunks = []
            for i in range(batch_size):
                chunk = SemanticChunk(
                    body=f"Performance test chunk {i} with detailed content for testing.",
                    text=f"Performance test chunk {i} with detailed content for testing.",
                    type=ChunkType.DOC_BLOCK,
                    language=LanguageEnum.EN,
                    source_id=generate_uuid(),
                    category="testing",
                    embedding=[0.1] * 384
                )
                chunks.append(chunk)
            
            start_time = time.time()
            create_result = await client.create_chunks(chunks)
            end_time = time.time()
            
            print(f"Batch size {batch_size}: {len(create_result.uuids)} chunks in {end_time - start_time:.3f}s")
        
    except Exception as e:
        print(f"⚠️  Error in performance optimization: {e}")


async def main():
    """Run all utility examples."""
    print("🚀 Vector Store Utilities Examples")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    try:
        await basic_usage_example()
        await advanced_usage_example()
        await batch_operations_example()
        await statistics_and_analysis_example()
        await export_import_example()
        await utility_functions_example()
        await performance_optimization_example()
        
        print("\n✅ All utility examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during utility examples: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 