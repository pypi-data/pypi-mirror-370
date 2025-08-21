"""
Full Workflow Example for Vector Store Client.

This example demonstrates a complete workflow:
1. Getting text content
2. Creating chunks manually (since chunking service integration is in extended client)
3. Sending chunks to vector store
4. Searching and retrieving chunks

This serves as a comprehensive integration test and usage guide.

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
from vector_store_client.types import ChunkType, LanguageEnum, ChunkStatus
from vector_store_client.exceptions import VectorStoreError


async def full_workflow_example():
    """
    Complete workflow example: Text → Chunk Creation → Storage → Search.
    
    This example demonstrates:
    1. Getting text content from various sources
    2. Creating chunks manually (simulating chunking service)
    3. Storing chunks in vector database
    4. Searching and retrieving chunks
    5. Basic maintenance operations
    """
    print("=== Vector Store Client - Full Workflow Example ===\n")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Create client
    print("1. Creating client...")
    client = await VectorStoreClient.create("http://localhost:8007")
    print("✓ Client created successfully\n")
    
    try:
        # Check server health
        print("2. Checking server health...")
        health = await client.health_check()
        print(f"✓ Server health: {health.status}")
        print(f"✓ Version: {health.version}")
        print(f"✓ Uptime: {health.uptime}s\n")
        
        # Step 1: Get text content
        print("3. Getting text content...")
        sample_texts = get_sample_texts()
        print(f"✓ Got {len(sample_texts)} text samples")
        for i, text in enumerate(sample_texts, 1):
            print(f"  {i}. {text['title']} ({len(text['content'])} chars)")
        print()
        
        # Step 2: Create chunks manually (simulating chunking service)
        print("4. Creating chunks manually...")
        all_chunks = []
        
        for text_data in sample_texts:
            print(f"  Creating chunks for: {text_data['title']}")
            
            # Simulate chunking by creating chunks manually
            chunks = create_chunks_from_text(
                text=text_data['content'],
                title=text_data['title'],
                category=text_data['category'],
                tags=text_data['tags'],
                source_id=str(uuid.uuid4())
            )
            
            print(f"    ✓ Created {len(chunks)} chunks")
            all_chunks.extend(chunks)
        
        print(f"✓ Total chunks created: {len(all_chunks)}")
        print()
        
        # Step 3: Store chunks in vector database
        print("5. Storing chunks in vector database...")
        
        # Store in batches for better performance
        batch_size = 10
        total_stored = 0
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            try:
                create_result = await client.create_chunks(batch)
                total_stored += len(create_result.uuids)
                print(f"  ✓ Stored batch {i // batch_size + 1}: {len(create_result.uuids)} chunks")
            except Exception as e:
                print(f"  ⚠️  Failed to store batch {i // batch_size + 1}: {e}")
        
        print(f"✓ Total chunks stored: {total_stored}")
        print()
        
        # Step 4: Search and retrieve chunks
        print("6. Searching and retrieving chunks...")
        
        # Search by different criteria
        search_queries = [
            "machine learning",
            "Python programming",
            "data science",
            "artificial intelligence"
        ]
        
        for query in search_queries:
            try:
                results = await client.search_chunks(search_str=query, limit=5)
                print(f"  ✓ '{query}': {len(results)} results")
                
                if results:
                    # Show first result details
                    first_result = results[0]
                    print(f"    First result: {first_result.body[:50]}...")
                    print(f"    UUID: {first_result.uuid}")
                    print(f"    Type: {getattr(first_result, 'type', 'unknown')}")
            except Exception as e:
                print(f"  ⚠️  Search failed for '{query}': {e}")
        
        print()
        
        # Step 5: Basic maintenance operations
        print("7. Performing basic maintenance...")
        
        try:
            # Get server info
            help_info = await client.help()
            print(f"  ✓ Available commands: {len(help_info.help_data.get('commands', {}))}")
            
            # Count chunks
            count_result = await client.execute_command("count", {})
            print(f"  ✓ Total chunks in store: {count_result.get('count', 0)}")
            
            # Check for duplicates
            duplicates_result = await client.execute_command("find_duplicate_uuids", {})
            duplicate_count = duplicates_result.get('total_duplicates', 0)
            print(f"  ✓ Duplicate chunks found: {duplicate_count}")
            
        except Exception as e:
            print(f"  ⚠️  Maintenance operations failed: {e}")
        
        print("\n✅ Full workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during full workflow: {e}")
    finally:
        await client.close()


def create_chunks_from_text(
    text: str,
    title: str,
    category: str,
    tags: List[str],
    source_id: str,
    max_chunk_size: int = 200
) -> List[SemanticChunk]:
    """
    Create chunks from text manually (simulating chunking service).
    
    This is a simplified chunking implementation for demonstration.
    In a real scenario, you would use the SVO chunking service.
    """
    chunks = []
    
    # Simple text splitting by sentences
    sentences = text.split('. ')
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue
            
        # Create chunk
        chunk = SemanticChunk(
            body=sentence.strip(),
            text=sentence.strip(),
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title=title,
            category=category,
            tags=tags,
            source_id=source_id,
            embedding=[0.1] * 384  # Placeholder embedding
        )
        
        chunks.append(chunk)
    
    return chunks


def get_sample_texts() -> List[Dict[str, Any]]:
    """Get sample texts for demonstration."""
    return [
        {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples that we provide.",
            "category": "AI",
            "tags": ["machine-learning", "ai", "introduction", "tutorial"]
        },
        {
            "title": "Python for Data Science",
            "content": "Python has become the de facto language for data science and machine learning. Its simplicity, extensive library ecosystem, and strong community support make it ideal for both beginners and experts. Key libraries like NumPy, Pandas, and Scikit-learn provide powerful tools for data manipulation, analysis, and machine learning. Python's readability and extensive documentation make it accessible to newcomers while offering advanced features for experienced developers.",
            "category": "Programming",
            "tags": ["python", "data-science", "programming", "tutorial"]
        },
        {
            "title": "Natural Language Processing Basics",
            "content": "Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. NLP draws from many disciplines including computer science and computational linguistics, in its pursuit to fill the gap between human communication and computer understanding. Modern NLP techniques are based on machine learning, especially statistical machine learning. The combination of machine learning, deep learning, and NLP has led to significant improvements in language understanding.",
            "category": "AI",
            "tags": ["nlp", "ai", "language-processing", "tutorial"]
        }
    ]


async def chunking_workflow_example():
    """
    Demonstrate chunking workflow with manual chunk creation.
    """
    print("=== Chunking Workflow Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Sample text for chunking
        sample_text = """
        Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines statistics, data analysis, machine learning, and related methods to understand and analyze actual phenomena with data. Data science employs techniques and theories drawn from many fields within the context of mathematics, statistics, computer science, information science, and domain knowledge.
        """
        
        print("Original text length:", len(sample_text))
        
        # Create chunks manually
        chunks = create_chunks_from_text(
            text=sample_text,
            title="Data Science Introduction",
            category="Data Science",
            tags=["data-science", "introduction", "tutorial"],
            source_id="data-science-docs"
        )
        
        print(f"Created {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"  {i}. {chunk.body[:50]}...")
        
        # Store chunks
        create_result = await client.create_chunks(chunks)
        print(f"Stored {len(create_result.uuids)} chunks successfully")
        
    except Exception as e:
        print(f"Error in chunking workflow: {e}")
    finally:
        await client.close()


async def search_workflow_example():
    """
    Demonstrate search workflow with various search strategies.
    """
    print("=== Search Workflow Example ===")
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create some test data first
        test_chunks = [
            SemanticChunk(
                body="Python is a versatile programming language used for web development, data science, and automation.",
                text="Python is a versatile programming language used for web development, data science, and automation.",
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                title="Python Overview",
                category="Programming",
                tags=["python", "programming", "tutorial"],
                source_id="python-docs",
                embedding=[0.1] * 384
            ),
            SemanticChunk(
                body="Machine learning algorithms can be supervised, unsupervised, or semi-supervised depending on the training data available.",
                text="Machine learning algorithms can be supervised, unsupervised, or semi-supervised depending on the training data available.",
                type=ChunkType.DOC_BLOCK,
                language=LanguageEnum.EN,
                title="Machine Learning Types",
                category="AI",
                tags=["machine-learning", "ai", "algorithms"],
                source_id="ml-docs",
                embedding=[0.2] * 384
            )
        ]
        
        # Store test data
        create_result = await client.create_chunks(test_chunks)
        print(f"Created {len(create_result.uuids)} test chunks")
        
        # Perform various searches
        search_queries = [
            "Python programming",
            "machine learning",
            "data science",
            "web development"
        ]
        
        print("\nSearch Results:")
        for query in search_queries:
            try:
                results = await client.search_chunks(search_str=query, limit=3)
                print(f"'{query}': {len(results)} results")
                
                for i, result in enumerate(results[:2], 1):
                    print(f"  {i}. {result.body[:60]}...")
            except Exception as e:
                print(f"'{query}': Error - {e}")
        
    except Exception as e:
        print(f"Error in search workflow: {e}")
    finally:
        await client.close()


async def main():
    """Run the full workflow example."""
    try:
        await full_workflow_example()
    except Exception as e:
        print(f"❌ Error running full workflow example: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 