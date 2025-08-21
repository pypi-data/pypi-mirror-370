"""
Semantic Search Engine using Vector Store Client.

This module demonstrates how to build a semantic search engine using
the Vector Store client for advanced search capabilities.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
    SearchOrder,
)
from vector_store_client.utils import create_search_filter, normalize_text


class SemanticSearchEngine:
    """
    Semantic search engine using Vector Store.
    
    Provides functionality for:
    - Semantic search with relevance scoring
    - Advanced filtering and faceted search
    - Search result ranking and clustering
    - Search analytics and insights
    """
    
    def __init__(self, client: VectorStoreClient):
        """
        Initialize semantic search engine.
        
        Parameters:
            client (VectorStoreClient): Vector Store client instance
        """
        self.client = client
    
    async def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        min_relevance: float = 0.0,
        order_by: SearchOrder = SearchOrder.RELEVANCE
    ) -> Dict[str, Any]:
        """
        Perform semantic search with advanced filtering.
        
        Parameters:
            query (str): Search query
            filters (Dict[str, Any], optional): Search filters
            limit (int): Maximum number of results
            offset (int): Result offset for pagination
            min_relevance (float): Minimum relevance threshold
            order_by (SearchOrder): Result ordering
            
        Returns:
            Dict[str, Any]: Search results with metadata
        """
        try:
            # Normalize query
            normalized_query = normalize_text(query)
            
            # Build search filter
            search_filter = self._build_search_filter(filters)
            
            # Perform search
            results = await self.client.search_chunks(
                search_str=normalized_query,
                metadata_filter=search_filter,
                limit=limit,
                level_of_relevance=min_relevance,
                offset=offset
            )
            
            # Process and rank results
            processed_results = self._process_search_results(results, query)
            
            # Get search analytics
            analytics = await self._get_search_analytics(query, results)
            
            return {
                "query": query,
                "results": processed_results,
                "total_results": len(results),
                "analytics": analytics,
                "search_params": {
                    "filters": filters,
                    "limit": limit,
                    "offset": offset,
                    "min_relevance": min_relevance,
                    "order_by": order_by.value
                }
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": str(e),
                "analytics": {}
            }
    
    async def faceted_search(
        self,
        query: str,
        facets: List[str],
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Perform faceted search with category breakdowns.
        
        Parameters:
            query (str): Search query
            facets (List[str]): Facets to analyze (e.g., ["category", "type", "language"])
            limit (int): Maximum number of results to analyze
            
        Returns:
            Dict[str, Any]: Search results with facet breakdowns
        """
        try:
            # Perform base search
            search_results = await self.semantic_search(query, limit=limit)
            
            # Analyze facets
            facet_analysis = {}
            for facet in facets:
                facet_analysis[facet] = self._analyze_facet(
                    search_results["results"], facet
                )
            
            return {
                "query": query,
                "results": search_results["results"],
                "facets": facet_analysis,
                "total_results": search_results["total_results"]
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "facets": {},
                "error": str(e)
            }
    
    async def search_suggestions(
        self,
        partial_query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get search suggestions based on partial query.
        
        Parameters:
            partial_query (str): Partial search query
            limit (int): Maximum number of suggestions
            
        Returns:
            List[Dict[str, Any]]: List of search suggestions
        """
        try:
            # Search for content that might match the partial query
            results = await self.client.search_chunks(
                search_str=partial_query,
                limit=limit * 2  # Get more to filter
            )
            
            suggestions = []
            seen_suggestions = set()
            
            for result in results:
                # Extract potential suggestions from titles and content
                potential_suggestions = self._extract_suggestions(
                    partial_query, result.chunk
                )
                
                for suggestion in potential_suggestions:
                    if suggestion not in seen_suggestions:
                        suggestions.append({
                            "suggestion": suggestion,
                            "relevance": result.relevance_score,
                            "source": result.chunk.uuid,
                            "type": "content_based"
                        })
                        seen_suggestions.add(suggestion)
                        
                        if len(suggestions) >= limit:
                            break
                
                if len(suggestions) >= limit:
                    break
            
            # Sort by relevance
            suggestions.sort(key=lambda x: x["relevance"], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            print(f"Error getting search suggestions: {e}")
            return []
    
    async def search_by_vector(
        self,
        vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search using a pre-computed vector.
        
        Parameters:
            vector (List[float]): Query vector
            filters (Dict[str, Any], optional): Search filters
            limit (int): Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            # This would require implementing search_by_vector in the client
            # For now, we'll simulate it by searching with a placeholder
            search_filter = self._build_search_filter(filters)
            
            # Note: This is a placeholder - actual implementation would use vector search
            results = await self.client.search_chunks(
                search_str="vector_search_placeholder",
                metadata_filter=search_filter,
                limit=limit
            )
            
            processed_results = []
            for result in results:
                # Calculate similarity with the provided vector
                similarity = self._calculate_vector_similarity(vector, result.chunk.embedding)
                
                processed_results.append({
                    "uuid": result.chunk.uuid,
                    "title": result.chunk.title,
                    "text": result.chunk.text,
                    "type": result.chunk.type,
                    "category": result.chunk.category,
                    "similarity_score": similarity,
                    "metadata": result.chunk.metadata
                })
            
            # Sort by similarity
            processed_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "query_vector": vector,
                "results": processed_results,
                "total_results": len(processed_results),
                "filters": filters
            }
            
        except Exception as e:
            return {
                "query_vector": vector,
                "results": [],
                "total_results": 0,
                "error": str(e)
            }
    
    async def search_analytics(
        self,
        time_window: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Get search analytics for the specified time window.
        
        Parameters:
            time_window (timedelta): Time window for analytics
            
        Returns:
            Dict[str, Any]: Search analytics data
        """
        try:
            # Get recent content for analysis
            cutoff_time = datetime.now() - time_window
            
            recent_content = await self.client.search_chunks(
                metadata_filter={
                    "created_at": {"$gte": cutoff_time.isoformat()}
                },
                limit=1000  # Get more for analysis
            )
            
            # Analyze search patterns
            analytics = {
                "total_content": len(recent_content),
                "content_by_type": {},
                "content_by_category": {},
                "content_by_language": {},
                "popular_tags": {},
                "content_timeline": {},
                "search_insights": {}
            }
            
            for result in recent_content:
                chunk = result.chunk
                
                # Count by type
                chunk_type = chunk.type.value
                analytics["content_by_type"][chunk_type] = analytics["content_by_type"].get(chunk_type, 0) + 1
                
                # Count by category
                if chunk.category:
                    analytics["content_by_category"][chunk.category] = analytics["content_by_category"].get(chunk.category, 0) + 1
                
                # Count by language
                chunk_lang = chunk.language.value
                analytics["content_by_language"][chunk_lang] = analytics["content_by_language"].get(chunk_lang, 0) + 1
                
                # Count tags
                if chunk.tags:
                    for tag in chunk.tags:
                        analytics["popular_tags"][tag] = analytics["popular_tags"].get(tag, 0) + 1
                
                # Timeline analysis
                if chunk.created_at:
                    try:
                        created_date = datetime.fromisoformat(chunk.created_at.replace('Z', '+00:00'))
                        date_key = created_date.strftime('%Y-%m-%d')
                        analytics["content_timeline"][date_key] = analytics["content_timeline"].get(date_key, 0) + 1
                    except:
                        pass
            
            # Generate insights
            analytics["search_insights"] = self._generate_search_insights(analytics)
            
            return analytics
            
        except Exception as e:
            return {
                "error": str(e),
                "total_content": 0,
                "content_by_type": {},
                "content_by_category": {},
                "content_by_language": {},
                "popular_tags": {},
                "content_timeline": {},
                "search_insights": {}
            }
    
    def _build_search_filter(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build search filter from user filters.
        
        Parameters:
            filters (Dict[str, Any], optional): User filters
            
        Returns:
            Dict[str, Any]: Processed search filter
        """
        if not filters:
            return {}
        
        search_filter = {}
        
        # Handle different filter types
        for key, value in filters.items():
            if key == "type" and value:
                search_filter["type"] = value
            elif key == "category" and value:
                search_filter["category"] = value
            elif key == "language" and value:
                search_filter["language"] = value
            elif key == "tags" and value:
                search_filter["tags"] = value if isinstance(value, list) else [value]
            elif key == "date_range" and value:
                # Handle date range filtering
                if "start_date" in value:
                    search_filter["created_at"] = {"$gte": value["start_date"]}
                if "end_date" in value:
                    if "created_at" in search_filter:
                        search_filter["created_at"]["$lte"] = value["end_date"]
                    else:
                        search_filter["created_at"] = {"$lte": value["end_date"]}
            elif key == "content_length" and value:
                # Handle content length filtering
                if "min_length" in value:
                    search_filter["text_length"] = {"$gte": value["min_length"]}
                if "max_length" in value:
                    if "text_length" in search_filter:
                        search_filter["text_length"]["$lte"] = value["max_length"]
                    else:
                        search_filter["text_length"] = {"$lte": value["max_length"]}
            else:
                # Pass through other filters
                search_filter[key] = value
        
        return search_filter
    
    def _process_search_results(
        self,
        results: List[Any],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Process and enhance search results.
        
        Parameters:
            results (List[Any]): Raw search results
            query (str): Original search query
            
        Returns:
            List[Dict[str, Any]]: Processed results
        """
        processed_results = []
        
        for i, result in enumerate(results):
            chunk = result.chunk
            
            # Calculate additional relevance factors
            relevance_factors = self._calculate_relevance_factors(chunk, query)
            
            # Extract highlights
            highlights = self._extract_highlights(chunk.text, query)
            
            processed_result = {
                "uuid": chunk.uuid,
                "title": chunk.title,
                "text": chunk.text,
                "type": chunk.type,
                "category": chunk.category,
                "language": chunk.language,
                "tags": chunk.tags,
                "relevance_score": result.relevance_score,
                "rank": i + 1,
                "highlights": highlights,
                "relevance_factors": relevance_factors,
                "metadata": chunk.metadata,
                "created_at": chunk.created_at
            }
            
            processed_results.append(processed_result)
        
        return processed_results
    
    def _calculate_relevance_factors(
        self,
        chunk: SemanticChunk,
        query: str
    ) -> Dict[str, float]:
        """
        Calculate various relevance factors for a chunk.
        
        Parameters:
            chunk (SemanticChunk): Content chunk
            query (str): Search query
            
        Returns:
            Dict[str, float]: Relevance factors
        """
        factors = {}
        
        # Title relevance
        if chunk.title:
            title_similarity = self._calculate_text_similarity(query, chunk.title)
            factors["title_relevance"] = title_similarity
        
        # Tag relevance
        if chunk.tags:
            tag_matches = sum(1 for tag in chunk.tags if tag.lower() in query.lower())
            factors["tag_relevance"] = tag_matches / len(chunk.tags) if chunk.tags else 0
        
        # Category relevance
        if chunk.category:
            category_similarity = self._calculate_text_similarity(query, chunk.category)
            factors["category_relevance"] = category_similarity
        
        # Content freshness
        if chunk.created_at:
            try:
                created_date = datetime.fromisoformat(chunk.created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_date).days
                factors["freshness"] = max(0, 1 - (days_old / 365))  # Decay over a year
            except:
                factors["freshness"] = 0.5
        
        # Content quality
        factors["content_quality"] = self._calculate_content_quality(chunk)
        
        return factors
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity.
        
        Parameters:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_content_quality(self, chunk: SemanticChunk) -> float:
        """
        Calculate content quality score.
        
        Parameters:
            chunk (SemanticChunk): Content chunk
            
        Returns:
            float: Quality score (0.0 to 1.0)
        """
        score = 0.0
        
        # Length factor
        text_length = len(chunk.text)
        if text_length > 500:
            score += 0.3
        elif text_length > 100:
            score += 0.2
        else:
            score += 0.1
        
        # Structure factor
        if chunk.title:
            score += 0.2
        
        if chunk.tags and len(chunk.tags) > 1:
            score += 0.1
        
        if chunk.category:
            score += 0.1
        
        # Type factor
        if chunk.type == ChunkType.DOC_BLOCK:
            score += 0.2
        elif chunk.type == ChunkType.CODE_BLOCK:
            score += 0.3
        
        return min(score, 1.0)
    
    def _extract_highlights(self, text: str, query: str) -> List[str]:
        """
        Extract highlighted snippets from text.
        
        Parameters:
            text (str): Text content
            query (str): Search query
            
        Returns:
            List[str]: Highlighted snippets
        """
        highlights = []
        query_words = query.lower().split()
        
        # Simple highlighting - find sentences containing query words
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in query_words):
                # Truncate long sentences
                if len(sentence) > 200:
                    sentence = sentence[:200] + "..."
                highlights.append(sentence.strip())
                
                if len(highlights) >= 3:  # Limit to 3 highlights
                    break
        
        return highlights
    
    def _analyze_facet(
        self,
        results: List[Dict[str, Any]],
        facet: str
    ) -> Dict[str, Any]:
        """
        Analyze a specific facet in search results.
        
        Parameters:
            results (List[Dict[str, Any]]): Search results
            facet (str): Facet to analyze
            
        Returns:
            Dict[str, Any]: Facet analysis
        """
        facet_counts = {}
        facet_values = []
        
        for result in results:
            value = result.get(facet)
            if value:
                facet_counts[value] = facet_counts.get(value, 0) + 1
                facet_values.append(value)
        
        # Calculate statistics
        total = len(facet_values)
        unique_values = len(facet_counts)
        
        return {
            "counts": facet_counts,
            "total": total,
            "unique_values": unique_values,
            "most_common": sorted(facet_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _extract_suggestions(
        self,
        partial_query: str,
        chunk: SemanticChunk
    ) -> List[str]:
        """
        Extract search suggestions from a chunk.
        
        Parameters:
            partial_query (str): Partial query
            chunk (SemanticChunk): Content chunk
            
        Returns:
            List[str]: Search suggestions
        """
        suggestions = []
        
        # Extract from title
        if chunk.title and partial_query.lower() in chunk.title.lower():
            suggestions.append(chunk.title)
        
        # Extract from tags
        if chunk.tags:
            for tag in chunk.tags:
                if partial_query.lower() in tag.lower():
                    suggestions.append(tag)
        
        # Extract from category
        if chunk.category and partial_query.lower() in chunk.category.lower():
            suggestions.append(chunk.category)
        
        return suggestions
    
    def _calculate_vector_similarity(
        self,
        vector1: List[float],
        vector2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Parameters:
            vector1 (List[float]): First vector
            vector2 (List[float]): Second vector
            
        Returns:
            float: Similarity score
        """
        if len(vector1) != len(vector2):
            return 0.0
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def _get_search_analytics(
        self,
        query: str,
        results: List[Any]
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific search.
        
        Parameters:
            query (str): Search query
            results (List[Any]): Search results
            
        Returns:
            Dict[str, Any]: Search analytics
        """
        analytics = {
            "query_length": len(query.split()),
            "result_count": len(results),
            "avg_relevance": 0.0,
            "relevance_distribution": {},
            "content_types": {},
            "categories": {},
            "languages": {}
        }
        
        if not results:
            return analytics
        
        # Calculate average relevance
        total_relevance = sum(result.relevance_score for result in results)
        analytics["avg_relevance"] = total_relevance / len(results)
        
        # Analyze relevance distribution
        for result in results:
            score_range = int(result.relevance_score * 10) / 10  # Round to 0.1
            analytics["relevance_distribution"][score_range] = analytics["relevance_distribution"].get(score_range, 0) + 1
        
        # Analyze content types
        for result in results:
            chunk_type = result.chunk.type.value
            analytics["content_types"][chunk_type] = analytics["content_types"].get(chunk_type, 0) + 1
        
        # Analyze categories
        for result in results:
            if result.chunk.category:
                analytics["categories"][result.chunk.category] = analytics["categories"].get(result.chunk.category, 0) + 1
        
        # Analyze languages
        for result in results:
            chunk_lang = result.chunk.language.value
            analytics["languages"][chunk_lang] = analytics["languages"].get(chunk_lang, 0) + 1
        
        return analytics
    
    def _generate_search_insights(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from search analytics.
        
        Parameters:
            analytics (Dict[str, Any]): Analytics data
            
        Returns:
            Dict[str, Any]: Generated insights
        """
        insights = {
            "popular_content_types": [],
            "trending_categories": [],
            "popular_tags": [],
            "content_growth": "stable",
            "recommendations": []
        }
        
        # Most popular content types
        if analytics["content_by_type"]:
            insights["popular_content_types"] = sorted(
                analytics["content_by_type"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        
        # Trending categories
        if analytics["content_by_category"]:
            insights["trending_categories"] = sorted(
                analytics["content_by_category"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        
        # Popular tags
        if analytics["popular_tags"]:
            insights["popular_tags"] = sorted(
                analytics["popular_tags"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        
        # Content growth analysis
        if analytics["content_timeline"]:
            timeline_values = list(analytics["content_timeline"].values())
            if len(timeline_values) > 1:
                recent_avg = sum(timeline_values[-3:]) / 3
                earlier_avg = sum(timeline_values[:-3]) / max(1, len(timeline_values) - 3)
                
                if recent_avg > earlier_avg * 1.2:
                    insights["content_growth"] = "increasing"
                elif recent_avg < earlier_avg * 0.8:
                    insights["content_growth"] = "decreasing"
        
        # Generate recommendations
        if insights["popular_content_types"]:
            insights["recommendations"].append(
                f"Focus on {insights['popular_content_types'][0][0]} content"
            )
        
        if insights["trending_categories"]:
            insights["recommendations"].append(
                f"Explore {insights['trending_categories'][0][0]} category"
            )
        
        return insights


async def main():
    """Demonstrate semantic search engine."""
    print("Semantic Search Engine Demo")
    print("=" * 40)
    
    # Initialize client and search engine
    client = await VectorStoreClient.create("http://localhost:8007")
    search_engine = SemanticSearchEngine(client)
    
    try:
        # Create sample content
        await create_sample_search_content(client)
        
        # Demonstrate different search capabilities
        print("\n1. Basic Semantic Search:")
        basic_results = await search_engine.semantic_search(
            "machine learning algorithms",
            limit=5
        )
        print(f"Found {basic_results['total_results']} results")
        
        print("\n2. Filtered Search:")
        filtered_results = await search_engine.semantic_search(
            "programming",
            filters={"category": "programming", "type": "doc_block"},
            limit=5
        )
        print(f"Found {filtered_results['total_results']} filtered results")
        
        print("\n3. Faceted Search:")
        faceted_results = await search_engine.faceted_search(
            "artificial intelligence",
            facets=["category", "type", "language"],
            limit=10
        )
        print(f"Facets: {list(faceted_results['facets'].keys())}")
        
        print("\n4. Search Suggestions:")
        suggestions = await search_engine.search_suggestions("machine", limit=3)
        for suggestion in suggestions:
            print(f"  - {suggestion['suggestion']}")
        
        print("\n5. Search Analytics:")
        analytics = await search_engine.search_analytics(timedelta(days=30))
        print(f"Total content: {analytics['total_content']}")
        print(f"Content types: {list(analytics['content_by_type'].keys())}")
        
    finally:
        await client.close()


async def create_sample_search_content(client: VectorStoreClient):
    """Create sample content for search demonstration."""
    from vector_store_client import SemanticChunk, ChunkType, LanguageEnum
    
    search_chunks = [
        SemanticChunk(
            body="Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed for specific tasks.",
            text="Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed for specific tasks.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Machine Learning Algorithms",
            category="ai",
            tags=["machine-learning", "algorithms", "ai", "data-science"]
        ),
        SemanticChunk(
            body="Deep learning is a subset of machine learning that uses neural networks with multiple layers to model complex patterns in data.",
            text="Deep learning is a subset of machine learning that uses neural networks with multiple layers to model complex patterns in data.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Deep Learning Fundamentals",
            category="ai",
            tags=["deep-learning", "neural-networks", "machine-learning"]
        ),
        SemanticChunk(
            body="Python is the most popular programming language for machine learning and data science due to its extensive ecosystem of libraries.",
            text="Python is the most popular programming language for machine learning and data science due to its extensive ecosystem of libraries.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Python for Machine Learning",
            category="programming",
            tags=["python", "programming", "machine-learning", "data-science"]
        ),
        SemanticChunk(
            body="def train_model(X, y):\n    model = RandomForestClassifier()\n    model.fit(X, y)\n    return model",
            text="def train_model(X, y):\n    model = RandomForestClassifier()\n    model.fit(X, y)\n    return model",
            type=ChunkType.CODE_BLOCK,
            language=LanguageEnum.EN,
            title="Machine Learning Model Training",
            category="programming",
            tags=["python", "machine-learning", "code", "training"]
        )
    ]
    
    result = await client.create_chunks(search_chunks)
    print(f"Created {result.total_created} sample search chunks")


if __name__ == "__main__":
    asyncio.run(main()) 