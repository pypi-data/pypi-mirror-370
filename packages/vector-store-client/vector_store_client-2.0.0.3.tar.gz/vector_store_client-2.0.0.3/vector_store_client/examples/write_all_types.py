"""
Write All Types Example for Vector Store Client.

This module demonstrates how to create and store different types
of content in the Vector Store, including documents, code blocks,
messages, and various metadata combinations.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from typing import List, Dict, Any
import uuid

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
    ChunkStatus,
)
from vector_store_client.utils import generate_uuid, generate_sha256_hash, format_timestamp


async def create_all_content_types():
    """
    Create examples of all content types supported by Vector Store.
    """
    print("Creating All Content Types Example")
    print("=" * 50)
    
    client = await VectorStoreClient.create("http://localhost:8007")
    
    try:
        # Create different types of content
        await create_document_blocks(client)
        await create_code_blocks(client)
        await create_messages(client)
        await create_mixed_content(client)
        await create_content_with_embeddings(client)
        await create_content_with_metadata(client)
        
        print("\nAll content types created successfully!")
        
    finally:
        await client.close()


async def create_document_blocks(client: VectorStoreClient):
    """Create various document blocks."""
    print("\n--- Creating Document Blocks ---")
    
    doc_chunks = [
        # Technical documentation
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
            text="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Introduction to Machine Learning",
            category="AI",
            tags=["machine-learning", "ai", "introduction", "tutorial"],
            metadata={
                "difficulty": "beginner",
                "topic": "artificial-intelligence",
                "word_count": 45,
                "reading_time": "2 minutes"
            }
        ),
        
        # Research paper abstract
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.2] * 384,
            body="This paper presents a novel approach to natural language processing using transformer-based architectures. We demonstrate significant improvements in text classification tasks across multiple datasets, achieving state-of-the-art results with 95% accuracy.",
            text="This paper presents a novel approach to natural language processing using transformer-based architectures. We demonstrate significant improvements in text classification tasks across multiple datasets, achieving state-of-the-art results with 95% accuracy.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Transformer-Based NLP: A Novel Approach",
            category="Research",
            tags=["nlp", "transformers", "research", "paper"],
            metadata={
                "difficulty": "advanced",
                "topic": "natural-language-processing",
                "word_count": 38,
                "reading_time": "1.5 minutes",
                "research_area": "NLP"
            }
        ),
        
        # Blog post
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.3] * 384,
            body="Python has become the de facto language for data science and machine learning. Its simplicity, extensive library ecosystem, and strong community support make it ideal for both beginners and experts. In this post, we'll explore why Python dominates the data science landscape.",
            text="Python has become the de facto language for data science and machine learning. Its simplicity, extensive library ecosystem, and strong community support make it ideal for both beginners and experts. In this post, we'll explore why Python dominates the data science landscape.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Why Python Dominates Data Science",
            category="Programming",
            tags=["python", "data-science", "programming", "blog"],
            metadata={
                "difficulty": "intermediate",
                "topic": "programming",
                "word_count": 52,
                "reading_time": "2.5 minutes",
                "post_type": "blog"
            }
        ),
        
        # Tutorial content
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.4] * 384,
            body="Getting started with Docker is easier than you think. Docker allows you to package applications with their dependencies into containers, ensuring consistent behavior across different environments. This tutorial will walk you through the basics of Docker containerization.",
            text="Getting started with Docker is easier than you think. Docker allows you to package applications with their dependencies into containers, ensuring consistent behavior across different environments. This tutorial will walk you through the basics of Docker containerization.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Docker Basics: A Beginner's Guide",
            category="DevOps",
            tags=["docker", "containers", "devops", "tutorial"],
            metadata={
                "difficulty": "beginner",
                "topic": "containerization",
                "word_count": 48,
                "reading_time": "2 minutes",
                "tutorial_type": "beginner"
            }
        )
    ]
    
    result = await client.create_chunks(doc_chunks)
    print(f"Created {result.created_count} document blocks")


async def create_code_blocks(client: VectorStoreClient):
    """Create various code blocks."""
    print("\n--- Creating Code Blocks ---")
    
    code_chunks = [
        # Python code
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="def fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number.\"\"\"\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# Example usage\nfor i in range(10):\n    print(f\"F({i}) = {fibonacci(i)}\")",
            text="def fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number.\"\"\"\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# Example usage\nfor i in range(10):\n    print(f\"F({i}) = {fibonacci(i)}\")",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN,
            title="Fibonacci Function in Python",
            category="Programming",
            tags=["python", "algorithms", "recursion", "fibonacci"],
            metadata={
                "programming_language": "python",
                "difficulty": "beginner",
                "topic": "algorithms",
                "code_lines": 10,
                "complexity": "O(2^n)"
            }
        ),
        
        # JavaScript code
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="// Async function to fetch data\nasync function fetchUserData(userId) {\n    try {\n        const response = await fetch(`/api/users/${userId}`);\n        if (!response.ok) {\n            throw new Error('User not found');\n        }\n        return await response.json();\n    } catch (error) {\n        console.error('Error fetching user:', error);\n        return null;\n    }\n}\n\n// Usage example\nconst user = await fetchUserData(123);",
            text="// Async function to fetch data\nasync function fetchUserData(userId) {\n    try {\n        const response = await fetch(`/api/users/${userId}`);\n        if (!response.ok) {\n            throw new Error('User not found');\n        }\n        return await response.json();\n    } catch (error) {\n        console.error('Error fetching user:', error);\n        return null;\n    }\n}\n\n// Usage example\nconst user = await fetchUserData(123);",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN,
            title="Async JavaScript Function",
            category="Programming",
            tags=["javascript", "async", "fetch", "api"],
            metadata={
                "programming_language": "javascript",
                "difficulty": "intermediate",
                "topic": "asynchronous-programming",
                "code_lines": 15,
                "complexity": "O(1)"
            }
        ),
        
        # SQL code
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="-- Complex SQL query with joins and aggregations\nSELECT \n    u.username,\n    COUNT(p.id) as post_count,\n    AVG(p.rating) as avg_rating,\n    MAX(p.created_at) as last_post\nFROM users u\nLEFT JOIN posts p ON u.id = p.user_id\nWHERE u.status = 'active'\n    AND p.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\nGROUP BY u.id, u.username\nHAVING post_count > 5\nORDER BY avg_rating DESC\nLIMIT 10;",
            text="-- Complex SQL query with joins and aggregations\nSELECT \n    u.username,\n    COUNT(p.id) as post_count,\n    AVG(p.rating) as avg_rating,\n    MAX(p.created_at) as last_post\nFROM users u\nLEFT JOIN posts p ON u.id = p.user_id\nWHERE u.status = 'active'\n    AND p.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)\nGROUP BY u.id, u.username\nHAVING post_count > 5\nORDER BY avg_rating DESC\nLIMIT 10;",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN,
            title="Complex SQL Query with Joins",
            category="Database",
            tags=["sql", "database", "joins", "aggregation"],
            metadata={
                "programming_language": "sql",
                "difficulty": "advanced",
                "topic": "database-queries",
                "code_lines": 15,
                "complexity": "O(n log n)"
            }
        ),
        
        # Docker configuration
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="# Dockerfile for Python application\nFROM python:3.9-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [\"python\", \"app.py\"]",
            text="# Dockerfile for Python application\nFROM python:3.9-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [\"python\", \"app.py\"]",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN,
            title="Python Dockerfile",
            category="DevOps",
            tags=["docker", "python", "containerization", "deployment"],
            metadata={
                "programming_language": "dockerfile",
                "difficulty": "intermediate",
                "topic": "containerization",
                "code_lines": 12,
                "complexity": "O(1)"
            }
        )
    ]
    
    result = await client.create_chunks(code_chunks)
    print(f"Created {result.created_count} code blocks")


async def create_messages(client: VectorStoreClient):
    """Create various message types."""
    print("\n--- Creating Messages ---")
    
    message_chunks = [
        # Question
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="How do I implement a binary search tree in Python? I need to create a BST class with insert, search, and delete methods. Can someone provide a complete implementation with examples?",
            text="How do I implement a binary search tree in Python? I need to create a BST class with insert, search, and delete methods. Can someone provide a complete implementation with examples?",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Binary Search Tree Implementation Question",
            category="Programming",
            tags=["python", "data-structures", "binary-search-tree", "question"],
            metadata={
                "message_type": "question",
                "difficulty": "intermediate",
                "topic": "data-structures",
                "word_count": 35,
                "requires_code": True
            }
        ),
        
        # Answer
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Here's a complete implementation of a Binary Search Tree in Python:\n\nclass Node:\n    def __init__(self, key):\n        self.key = key\n        self.left = None\n        self.right = None\n\nclass BST:\n    def __init__(self):\n        self.root = None\n    \n    def insert(self, key):\n        self.root = self._insert_recursive(self.root, key)\n    \n    def _insert_recursive(self, root, key):\n        if root is None:\n            return Node(key)\n        if key < root.key:\n            root.left = self._insert_recursive(root.left, key)\n        else:\n            root.right = self._insert_recursive(root.right, key)\n        return root",
            text="Here's a complete implementation of a Binary Search Tree in Python:\n\nclass Node:\n    def __init__(self, key):\n        self.key = key\n        self.left = None\n        self.right = None\n\nclass BST:\n    def __init__(self):\n        self.root = None\n    \n    def insert(self, key):\n        self.root = self._insert_recursive(self.root, key)\n    \n    def _insert_recursive(self, root, key):\n        if root is None:\n            return Node(key)\n        if key < root.key:\n            root.left = self._insert_recursive(root.left, key)\n        else:\n            root.right = self._insert_recursive(root.right, key)\n        return root",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Binary Search Tree Implementation Answer",
            category="Programming",
            tags=["python", "data-structures", "binary-search-tree", "answer"],
            metadata={
                "message_type": "answer",
                "difficulty": "intermediate",
                "topic": "data-structures",
                "word_count": 120,
                "includes_code": True
            }
        ),
        
        # Discussion
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="I've been working with machine learning models for the past year, and I've noticed that the choice of hyperparameters can make a huge difference in model performance. Has anyone else experienced this? What strategies do you use for hyperparameter tuning? I'm particularly interested in automated approaches like Bayesian optimization.",
            text="I've been working with machine learning models for the past year, and I've noticed that the choice of hyperparameters can make a huge difference in model performance. Has anyone else experienced this? What strategies do you use for hyperparameter tuning? I'm particularly interested in automated approaches like Bayesian optimization.",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Hyperparameter Tuning Discussion",
            category="AI",
            tags=["machine-learning", "hyperparameters", "discussion", "optimization"],
            metadata={
                "message_type": "discussion",
                "difficulty": "advanced",
                "topic": "machine-learning",
                "word_count": 58,
                "requires_experience": True
            }
        ),
        
        # Announcement
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="We're excited to announce the release of our new Vector Store API v2.0! This major update includes improved search performance, better support for large-scale deployments, and enhanced metadata filtering capabilities. The new version is backward compatible and includes comprehensive migration guides.",
            text="We're excited to announce the release of our new Vector Store API v2.0! This major update includes improved search performance, better support for large-scale deployments, and enhanced metadata filtering capabilities. The new version is backward compatible and includes comprehensive migration guides.",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Vector Store API v2.0 Release Announcement",
            category="Product",
            tags=["api", "release", "announcement", "vector-store"],
            metadata={
                "message_type": "announcement",
                "difficulty": "all",
                "topic": "product-updates",
                "word_count": 42,
                "is_official": True
            }
        )
    ]
    
    result = await client.create_chunks(message_chunks)
    print(f"Created {result.created_count} messages")


async def create_mixed_content(client: VectorStoreClient):
    """Create content with mixed types and languages."""
    print("\n--- Creating Mixed Content ---")
    
    mixed_chunks = [
        # Russian content
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Машинное обучение - это подраздел искусственного интеллекта, который позволяет компьютерам учиться на основе данных без явного программирования. Алгоритмы машинного обучения могут находить скрытые закономерности в данных и использовать их для прогнозирования.",
            text="Машинное обучение - это подраздел искусственного интеллекта, который позволяет компьютерам учиться на основе данных без явного программирования. Алгоритмы машинного обучения могут находить скрытые закономерности в данных и использовать их для прогнозирования.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.RU,
            title="Введение в машинное обучение",
            category="AI",
            tags=["машинное-обучение", "искусственный-интеллект", "алгоритмы"],
            metadata={
                "difficulty": "beginner",
                "topic": "artificial-intelligence",
                "language": "russian",
                "word_count": 35
            }
        ),
        
        # Spanish content
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Python es un lenguaje de programación versátil ampliamente utilizado en ciencia de datos y aprendizaje automático. Su simplicidad, extenso ecosistema de bibliotecas y fuerte apoyo de la comunidad lo hacen ideal tanto para principiantes como para expertos.",
            text="Python es un lenguaje de programación versátil ampliamente utilizado en ciencia de datos y aprendizaje automático. Su simplicidad, extenso ecosistema de bibliotecas y fuerte apoyo de la comunidad lo hacen ideal tanto para principiantes como para expertos.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.ES,
            title="Python para Ciencia de Datos",
            category="Programming",
            tags=["python", "ciencia-de-datos", "programación"],
            metadata={
                "difficulty": "intermediate",
                "topic": "programming",
                "language": "spanish",
                "word_count": 42
            }
        ),
        
        # French content
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="L'apprentissage automatique est un sous-ensemble de l'intelligence artificielle qui permet aux ordinateurs d'apprendre à partir de données sans être explicitement programmés. Les algorithmes d'apprentissage automatique peuvent découvrir des modèles cachés dans les données.",
            text="L'apprentissage automatique est un sous-ensemble de l'intelligence artificielle qui permet aux ordinateurs d'apprendre à partir de données sans être explicitement programmés. Les algorithmes d'apprentissage automatique peuvent découvrir des modèles cachés dans les données.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.FR,
            title="Introduction à l'Apprentissage Automatique",
            category="AI",
            tags=["apprentissage-automatique", "intelligence-artificielle", "algorithmes"],
            metadata={
                "difficulty": "beginner",
                "topic": "artificial-intelligence",
                "language": "french",
                "word_count": 38
            }
        ),
        
        # German content
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Maschinelles Lernen ist ein Teilbereich der künstlichen Intelligenz, der es Computern ermöglicht, aus Daten zu lernen, ohne explizit programmiert zu werden. Maschinelle Lernalgorithmen können versteckte Muster in Daten finden und für Vorhersagen nutzen.",
            text="Maschinelles Lernen ist ein Teilbereich der künstlichen Intelligenz, der es Computern ermöglicht, aus Daten zu lernen, ohne explizit programmiert zu werden. Maschinelle Lernalgorithmen können versteckte Muster in Daten finden und für Vorhersagen nutzen.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.DE,
            title="Einführung in Maschinelles Lernen",
            category="AI",
            tags=["maschinelles-lernen", "künstliche-intelligenz", "algorithmen"],
            metadata={
                "difficulty": "beginner",
                "topic": "artificial-intelligence",
                "language": "german",
                "word_count": 40
            }
        )
    ]
    
    result = await client.create_chunks(mixed_chunks)
    print(f"Created {result.created_count} mixed content items")


async def create_content_with_embeddings(client: VectorStoreClient):
    """Create content with custom embeddings."""
    print("\n--- Creating Content with Embeddings ---")
    
    # Generate sample 384-dimensional embeddings
    def generate_sample_embedding():
        import random
        return [random.uniform(-1, 1) for _ in range(384)]
    
    embedding_chunks = [
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="This is a sample document with a custom embedding vector. The embedding represents the semantic meaning of this text in a 384-dimensional space.",
            text="This is a sample document with a custom embedding vector. The embedding represents the semantic meaning of this text in a 384-dimensional space.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Sample Document with Custom Embedding",
            category="Example",
            tags=["embedding", "sample", "custom"],
            metadata={
                "embedding_type": "custom",
                "embedding_dimension": 384,
                "embedding_model": "custom_model"
            }
        ),
        
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=generate_sample_embedding(),
            body="Another document with a different embedding vector. This demonstrates how different content can have distinct vector representations.",
            text="Another document with a different embedding vector. This demonstrates how different content can have distinct vector representations.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Another Document with Embedding",
            category="Example",
            tags=["embedding", "sample", "vector"],
            metadata={
                "embedding_type": "custom",
                "embedding_dimension": 384,
                "embedding_model": "custom_model"
            }
        )
    ]
    
    result = await client.create_chunks(embedding_chunks)
    print(f"Created {result.created_count} content items with custom embeddings")


async def create_content_with_metadata(client: VectorStoreClient):
    """Create content with rich metadata."""
    print("\n--- Creating Content with Rich Metadata ---")
    
    rich_metadata_chunks = [
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="This document demonstrates rich metadata capabilities. It includes various types of metadata fields for comprehensive content management and search.",
            text="This document demonstrates rich metadata capabilities. It includes various types of metadata fields for comprehensive content management and search.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Rich Metadata Example",
            category="Documentation",
            tags=["metadata", "example", "documentation"],
            metadata={
                # Basic metadata
                "author": "John Doe",
                "created_date": "2024-01-15",
                "last_modified": "2024-01-20",
                "version": "1.2.3",
                
                # Content metadata
                "word_count": 25,
                "reading_time": "1 minute",
                "difficulty_level": "intermediate",
                "target_audience": ["developers", "data-scientists"],
                
                # Technical metadata
                "file_size": 2048,
                "format": "markdown",
                "encoding": "utf-8",
                "checksum": generate_sha256_hash("Rich metadata example"),
                
                # Business metadata
                "department": "Engineering",
                "project": "Vector Store Client",
                "priority": "medium",
                "status": "published",
                
                # Custom metadata
                "custom_field_1": "custom_value_1",
                "custom_field_2": 42,
                "custom_field_3": True,
                "custom_field_4": ["item1", "item2", "item3"],
                "custom_field_5": {
                    "nested": "value",
                    "nested_number": 123,
                    "nested_array": [1, 2, 3]
                }
            }
        ),
        
        SemanticChunk(
            source_id=str(uuid.uuid4()),
            embedding=[0.1] * 384,
            body="Another example with different metadata structure. This shows how metadata can vary between different content items.",
            text="Another example with different metadata structure. This shows how metadata can vary between different content items.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Alternative Metadata Example",
            category="Documentation",
            tags=["metadata", "alternative", "example"],
            metadata={
                # Different structure
                "content_info": {
                    "author": "Jane Smith",
                    "created": "2024-01-10T10:30:00Z",
                    "modified": "2024-01-18T14:45:00Z"
                },
                "technical_specs": {
                    "format": "text",
                    "encoding": "utf-8",
                    "size_bytes": 1024
                },
                "business_context": {
                    "team": "Product",
                    "sprint": "Q1-2024",
                    "milestone": "v2.0"
                },
                "analytics": {
                    "views": 150,
                    "likes": 12,
                    "shares": 5,
                    "avg_time_on_page": 120
                }
            }
        )
    ]
    
    result = await client.create_chunks(rich_metadata_chunks)
    print(f"Created {result.created_count} content items with rich metadata")


async def main():
    """Run the complete example."""
    print("Vector Store Client - Write All Types Example")
    print("=" * 60)
    
    try:
        await create_all_content_types()
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("You can now search for different content types using:")
        print("- Document blocks: Search for 'machine learning' or 'python'")
        print("- Code blocks: Search for 'fibonacci' or 'docker'")
        print("- Messages: Search for 'question' or 'discussion'")
        print("- Mixed content: Search for content in different languages")
        print("- Rich metadata: Search using metadata filters")
        
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 