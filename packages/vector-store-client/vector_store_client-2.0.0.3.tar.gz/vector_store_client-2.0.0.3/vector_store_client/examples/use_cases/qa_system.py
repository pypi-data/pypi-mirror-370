"""
Question-Answering System using Vector Store Client.

This module demonstrates how to build a Q&A system using the Vector Store
client for semantic search and answer retrieval.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import re

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
)
from vector_store_client.utils import normalize_text


class QASystem:
    """
    Question-Answering system using Vector Store.
    
    Provides functionality for:
    - Question processing and analysis
    - Semantic search for relevant content
    - Answer generation and ranking
    - Context-aware responses
    """
    
    def __init__(self, client: VectorStoreClient):
        """
        Initialize QA system.
        
        Parameters:
            client (VectorStoreClient): Vector Store client instance
        """
        self.client = client
    
    async def ask_question(
        self,
        question: str,
        max_results: int = 5,
        min_relevance: float = 0.6,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a question and get an answer.
        
        Parameters:
            question (str): The question to ask
            max_results (int): Maximum number of relevant chunks to retrieve
            min_relevance (float): Minimum relevance threshold
            include_context (bool): Whether to include context in response
            
        Returns:
            Dict[str, Any]: Answer with metadata and context
        """
        try:
            # Process the question
            processed_question = self._process_question(question)
            
            # Search for relevant content
            search_results = await self.client.search_chunks(
                search_str=processed_question,
                limit=max_results,
                level_of_relevance=min_relevance
            )
            
            if not search_results:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "confidence": 0.0,
                    "sources": [],
                    "context": None,
                    "question": question
                }
            
            # Generate answer from search results
            answer, confidence, sources = self._generate_answer(
                question, search_results, include_context
            )
            
            return {
                "answer": answer,
                "confidence": confidence,
                "sources": sources,
                "context": self._extract_context(search_results) if include_context else None,
                "question": question,
                "total_results": len(search_results)
            }
            
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error while processing your question: {e}",
                "confidence": 0.0,
                "sources": [],
                "context": None,
                "question": question,
                "error": str(e)
            }
    
    async def ask_follow_up_question(
        self,
        original_question: str,
        follow_up: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Ask a follow-up question with conversation context.
        
        Parameters:
            original_question (str): The original question
            follow_up (str): The follow-up question
            conversation_history (List[Dict[str, Any]]): Previous conversation turns
            
        Returns:
            Dict[str, Any]: Answer with conversation context
        """
        try:
            # Combine original question and follow-up with context
            contextual_question = self._build_contextual_question(
                original_question, follow_up, conversation_history
            )
            
            # Search with enhanced context
            search_results = await self.client.search_chunks(
                search_str=contextual_question,
                limit=8,  # More results for context
                level_of_relevance=0.5  # Lower threshold for context
            )
            
            # Generate answer with conversation awareness
            answer, confidence, sources = self._generate_contextual_answer(
                follow_up, search_results, conversation_history
            )
            
            return {
                "answer": answer,
                "confidence": confidence,
                "sources": sources,
                "context": self._extract_context(search_results),
                "question": follow_up,
                "original_question": original_question,
                "conversation_context": len(conversation_history)
            }
            
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error with your follow-up question: {e}",
                "confidence": 0.0,
                "sources": [],
                "context": None,
                "question": follow_up,
                "error": str(e)
            }
    
    async def get_similar_questions(
        self,
        question: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar questions that have been asked before.
        
        Parameters:
            question (str): The question to find similar ones for
            limit (int): Maximum number of similar questions
            
        Returns:
            List[Dict[str, Any]]: List of similar questions with answers
        """
        try:
            # Search for question-type chunks
            similar_questions = await self.client.search_chunks(
                search_str=question,
                metadata_filter={"type": "message"},
                limit=limit
            )
            
            results = []
            for result in similar_questions:
                # Extract question and answer from the chunk
                qa_pair = self._extract_qa_pair(result.chunk)
                if qa_pair:
                    results.append({
                        "question": qa_pair["question"],
                        "answer": qa_pair["answer"],
                        "similarity": result.relevance_score,
                        "source": result.chunk.uuid
                    })
            
            return results
            
        except Exception as e:
            print(f"Error finding similar questions: {e}")
            return []
    
    async def suggest_related_questions(
        self,
        question: str,
        limit: int = 3
    ) -> List[str]:
        """
        Suggest related questions based on the input question.
        
        Parameters:
            question (str): The input question
            limit (int): Maximum number of suggestions
            
        Returns:
            List[str]: List of suggested related questions
        """
        try:
            # Extract key concepts from the question
            key_concepts = self._extract_key_concepts(question)
            
            suggestions = []
            for concept in key_concepts[:3]:  # Use top 3 concepts
                # Search for content related to each concept
                results = await self.client.search_chunks(
                    search_str=concept,
                    limit=2
                )
                
                for result in results:
                    # Generate a question based on the content
                    suggested_question = self._generate_question_from_content(
                        concept, result.chunk
                    )
                    if suggested_question and suggested_question not in suggestions:
                        suggestions.append(suggested_question)
                        if len(suggestions) >= limit:
                            break
                
                if len(suggestions) >= limit:
                    break
            
            return suggestions[:limit]
            
        except Exception as e:
            print(f"Error suggesting related questions: {e}")
            return []
    
    def _process_question(self, question: str) -> str:
        """
        Process and normalize a question for better search.
        
        Parameters:
            question (str): Raw question
            
        Returns:
            str: Processed question
        """
        # Remove question words and normalize
        question = normalize_text(question)
        
        # Remove common question words
        question_words = ["what", "how", "why", "when", "where", "who", "which", "is", "are", "can", "could", "would", "should"]
        words = question.split()
        filtered_words = [word for word in words if word.lower() not in question_words]
        
        return " ".join(filtered_words)
    
    def _generate_answer(
        self,
        question: str,
        search_results: List[Any],
        include_context: bool
    ) -> Tuple[str, float, List[Dict[str, Any]]]:
        """
        Generate an answer from search results.
        
        Parameters:
            question (str): Original question
            search_results (List[Any]): Search results
            include_context (bool): Whether to include context
            
        Returns:
            Tuple[str, float, List[Dict[str, Any]]]: Answer, confidence, sources
        """
        if not search_results:
            return "I couldn't find any relevant information.", 0.0, []
        
        # Use the top result as the primary answer
        top_result = search_results[0]
        primary_answer = self._extract_answer_from_chunk(top_result.chunk, question)
        
        # Calculate confidence based on relevance and content quality
        confidence = self._calculate_answer_confidence(top_result, question)
        
        # Collect sources
        sources = []
        for result in search_results[:3]:  # Top 3 sources
            sources.append({
                "uuid": result.chunk.uuid,
                "title": result.chunk.title,
                "relevance": result.relevance_score,
                "type": result.chunk.type,
                "category": result.chunk.category
            })
        
        return primary_answer, confidence, sources
    
    def _generate_contextual_answer(
        self,
        follow_up: str,
        search_results: List[Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Tuple[str, float, List[Dict[str, Any]]]:
        """
        Generate answer with conversation context.
        
        Parameters:
            follow_up (str): Follow-up question
            search_results (List[Any]): Search results
            conversation_history (List[Dict[str, Any]]): Conversation history
            
        Returns:
            Tuple[str, float, List[Dict[str, Any]]]: Answer, confidence, sources
        """
        # Combine information from conversation history and new search results
        contextual_info = self._extract_contextual_info(conversation_history)
        
        if not search_results:
            # Try to answer based on conversation history
            if contextual_info:
                return f"Based on our previous conversation: {contextual_info}", 0.7, []
            else:
                return "I need more context to answer your follow-up question.", 0.3, []
        
        # Generate answer with context
        top_result = search_results[0]
        answer = self._extract_answer_from_chunk(top_result.chunk, follow_up)
        
        # Add context if available
        if contextual_info:
            answer = f"{answer} This relates to our earlier discussion about {contextual_info}."
        
        confidence = self._calculate_answer_confidence(top_result, follow_up)
        
        sources = [{
            "uuid": top_result.chunk.uuid,
            "title": top_result.chunk.title,
            "relevance": top_result.relevance_score,
            "context_enhanced": True
        }]
        
        return answer, confidence, sources
    
    def _extract_answer_from_chunk(self, chunk: SemanticChunk, question: str) -> str:
        """
        Extract or generate an answer from a chunk.
        
        Parameters:
            chunk (SemanticChunk): Content chunk
            question (str): Original question
            
        Returns:
            str: Generated answer
        """
        # For simple cases, return the chunk text
        if chunk.type == ChunkType.DOC_BLOCK:
            return chunk.text
        
        # For code blocks, format appropriately
        elif chunk.type == ChunkType.CODE_BLOCK:
            return f"Here's the code:\n{chunk.text}"
        
        # For messages, extract the answer part
        elif chunk.type == ChunkType.MESSAGE:
            return self._extract_answer_from_message(chunk.text)
        
        # Default case
        return chunk.text
    
    def _extract_answer_from_message(self, message: str) -> str:
        """
        Extract answer from a message that might contain Q&A.
        
        Parameters:
            message (str): Message content
            
        Returns:
            str: Extracted answer
        """
        # Simple extraction - look for patterns like "Answer:" or "A:"
        patterns = [
            r"Answer:\s*(.+)",
            r"A:\s*(.+)",
            r"Solution:\s*(.+)",
            r"Explanation:\s*(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern found, return the whole message
        return message
    
    def _calculate_answer_confidence(
        self,
        result: Any,
        question: str
    ) -> float:
        """
        Calculate confidence score for an answer.
        
        Parameters:
            result: Search result
            question (str): Original question
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        base_confidence = result.relevance_score
        
        # Adjust based on content quality
        content_quality = 0.0
        chunk = result.chunk
        
        # Length factor
        if len(chunk.text) > 100:
            content_quality += 0.2
        elif len(chunk.text) > 50:
            content_quality += 0.1
        
        # Type factor
        if chunk.type == ChunkType.DOC_BLOCK:
            content_quality += 0.2
        elif chunk.type == ChunkType.CODE_BLOCK:
            content_quality += 0.3
        
        # Category factor
        if chunk.category in ["tutorial", "documentation", "guide"]:
            content_quality += 0.1
        
        # Tags factor
        if chunk.tags and len(chunk.tags) > 1:
            content_quality += 0.1
        
        return min(base_confidence + content_quality, 1.0)
    
    def _extract_context(self, search_results: List[Any]) -> str:
        """
        Extract context from search results.
        
        Parameters:
            search_results (List[Any]): Search results
            
        Returns:
            str: Context information
        """
        if not search_results:
            return ""
        
        # Combine information from top results
        context_parts = []
        for result in search_results[:2]:  # Use top 2 results
            chunk = result.chunk
            if chunk.title:
                context_parts.append(f"'{chunk.title}'")
            elif chunk.category:
                context_parts.append(f"content about {chunk.category}")
        
        if context_parts:
            return f"Based on {', '.join(context_parts)}"
        
        return ""
    
    def _build_contextual_question(
        self,
        original_question: str,
        follow_up: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Build a contextual question combining history and follow-up.
        
        Parameters:
            original_question (str): Original question
            follow_up (str): Follow-up question
            conversation_history (List[Dict[str, Any]]): Conversation history
            
        Returns:
            str: Contextual question
        """
        # Extract key information from conversation history
        context_keywords = []
        for turn in conversation_history[-3:]:  # Last 3 turns
            if "answer" in turn:
                # Extract key concepts from previous answers
                keywords = self._extract_key_concepts(turn["answer"])
                context_keywords.extend(keywords[:2])  # Top 2 keywords per turn
        
        # Combine with follow-up question
        contextual_parts = [follow_up]
        if context_keywords:
            contextual_parts.extend(context_keywords)
        
        return " ".join(contextual_parts)
    
    def _extract_contextual_info(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Extract contextual information from conversation history.
        
        Parameters:
            conversation_history (List[Dict[str, Any]]): Conversation history
            
        Returns:
            str: Contextual information
        """
        if not conversation_history:
            return ""
        
        # Extract key topics from recent conversation
        topics = []
        for turn in conversation_history[-2:]:  # Last 2 turns
            if "answer" in turn:
                key_concepts = self._extract_key_concepts(turn["answer"])
                topics.extend(key_concepts[:1])  # Top concept per turn
        
        if topics:
            return ", ".join(set(topics))  # Remove duplicates
        
        return ""
    
    def _extract_qa_pair(self, chunk: SemanticChunk) -> Optional[Dict[str, str]]:
        """
        Extract question-answer pair from a chunk.
        
        Parameters:
            chunk (SemanticChunk): Content chunk
            
        Returns:
            Optional[Dict[str, str]]: Q&A pair or None
        """
        text = chunk.text
        
        # Look for Q&A patterns
        patterns = [
            (r"Q:\s*(.+?)\s*A:\s*(.+)", "Q:", "A:"),
            (r"Question:\s*(.+?)\s*Answer:\s*(.+)", "Question:", "Answer:"),
            (r"(.+\?)\s*(.+)", "?", "")
        ]
        
        for pattern, q_marker, a_marker in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                question = match.group(1).strip()
                answer = match.group(2).strip()
                return {"question": question, "answer": answer}
        
        return None
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from text.
        
        Parameters:
            text (str): Input text
            
        Returns:
            List[str]: Key concepts
        """
        # Simple keyword extraction
        # In a real implementation, you'd use NLP techniques
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can"}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        from collections import Counter
        word_counts = Counter(keywords)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(5)]
    
    def _generate_question_from_content(self, concept: str, chunk: SemanticChunk) -> Optional[str]:
        """
        Generate a question based on content and concept.
        
        Parameters:
            concept (str): Key concept
            chunk (SemanticChunk): Content chunk
            
        Returns:
            Optional[str]: Generated question or None
        """
        # Simple question generation
        if chunk.title:
            return f"What is {chunk.title}?"
        elif chunk.category:
            return f"How does {concept} relate to {chunk.category}?"
        else:
            return f"Can you explain {concept}?"
        
        return None


async def main():
    """Demonstrate QA system."""
    print("Question-Answering System Demo")
    print("=" * 40)
    
    # Initialize client and QA system
    client = await VectorStoreClient.create("http://localhost:8007")
    qa_system = QASystem(client)
    
    try:
        # Create sample Q&A content
        await create_sample_qa_content(client)
        
        # Demonstrate QA functionality
        questions = [
            "What is machine learning?",
            "How do neural networks work?",
            "What programming languages are used for AI?",
            "Can you explain deep learning?"
        ]
        
        conversation_history = []
        
        for question in questions:
            print(f"\nQ: {question}")
            
            # Get answer
            answer = await qa_system.ask_question(question)
            print(f"A: {answer['answer']}")
            print(f"Confidence: {answer['confidence']:.2f}")
            
            # Store in conversation history
            conversation_history.append({
                "question": question,
                "answer": answer['answer'],
                "confidence": answer['confidence']
            })
            
            # Get similar questions
            similar = await qa_system.get_similar_questions(question, limit=2)
            if similar:
                print(f"Similar questions: {len(similar)} found")
            
            # Get related questions
            related = await qa_system.suggest_related_questions(question, limit=2)
            if related:
                print(f"Related questions: {related}")
        
        # Demonstrate follow-up questions
        print(f"\n--- Follow-up Questions ---")
        follow_up = "How does this relate to what we discussed earlier?"
        follow_up_answer = await qa_system.ask_follow_up_question(
            questions[0], follow_up, conversation_history
        )
        print(f"Follow-up Q: {follow_up}")
        print(f"Follow-up A: {follow_up_answer['answer']}")
        
    finally:
        await client.close()


async def create_sample_qa_content(client: VectorStoreClient):
    """Create sample Q&A content for demonstration."""
    from vector_store_client import SemanticChunk, ChunkType, LanguageEnum
    
    qa_chunks = [
        SemanticChunk(
            body="Q: What is machine learning?\nA: Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            text="Q: What is machine learning?\nA: Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Machine Learning Definition",
            category="ai",
            tags=["machine-learning", "definition", "ai"]
        ),
        SemanticChunk(
            body="Q: How do neural networks work?\nA: Neural networks are computing systems inspired by biological brains. They consist of interconnected nodes (neurons) that process information and learn patterns through training on data.",
            text="Q: How do neural networks work?\nA: Neural networks are computing systems inspired by biological brains. They consist of interconnected nodes (neurons) that process information and learn patterns through training on data.",
            type=ChunkType.MESSAGE,
            language=LanguageEnum.EN,
            title="Neural Networks Explanation",
            category="ai",
            tags=["neural-networks", "explanation", "ai"]
        ),
        SemanticChunk(
            body="Python is the most popular programming language for machine learning and AI development. It offers extensive libraries like TensorFlow, PyTorch, and scikit-learn that make it easy to implement machine learning algorithms.",
            text="Python is the most popular programming language for machine learning and AI development. It offers extensive libraries like TensorFlow, PyTorch, and scikit-learn that make it easy to implement machine learning algorithms.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Python for AI Development",
            category="programming",
            tags=["python", "ai", "programming", "libraries"]
        )
    ]
    
    result = await client.create_chunks(qa_chunks)
    print(f"Created {result.total_created} sample Q&A chunks")


if __name__ == "__main__":
    asyncio.run(main()) 