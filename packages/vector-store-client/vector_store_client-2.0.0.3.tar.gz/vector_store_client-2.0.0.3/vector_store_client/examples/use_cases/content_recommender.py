"""
Content Recommendation System using Vector Store Client.

This module demonstrates how to build a content recommendation system
using the Vector Store client for semantic similarity and content discovery.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from vector_store_client import (
    VectorStoreClient,
    SemanticChunk,
    ChunkType,
    LanguageEnum,
)
from vector_store_client.utils import create_search_filter


class ContentRecommender:
    """
    Content recommendation system using Vector Store.
    
    Provides functionality for:
    - Content-based recommendations
    - Collaborative filtering
    - Trending content discovery
    - Personalized recommendations
    """
    
    def __init__(self, client: VectorStoreClient):
        """
        Initialize content recommender.
        
        Parameters:
            client (VectorStoreClient): Vector Store client instance
        """
        self.client = client
    
    async def get_content_based_recommendations(
        self,
        content_id: str,
        limit: int = 10,
        min_relevance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get content-based recommendations based on a specific content item.
        
        Parameters:
            content_id (str): ID of the content to base recommendations on
            limit (int): Maximum number of recommendations
            min_relevance (float): Minimum relevance threshold
            
        Returns:
            List[Dict[str, Any]]: List of recommended content items
        """
        try:
            # Get the source content
            source_results = await self.client.search_chunks(
                metadata_filter={"uuid": content_id},
                limit=1
            )
            
            if not source_results:
                return []
            
            source_chunk = source_results[0].chunk
            
            # Find similar content
            similar_results = await self.client.search_chunks(
                search_str=source_chunk.text,
                limit=limit + 1,  # +1 to exclude the source
                level_of_relevance=min_relevance,
                metadata_filter={
                    "uuid": {"$ne": content_id},  # Exclude source
                    "type": source_chunk.type
                }
            )
            
            # Filter out the source content
            recommendations = []
            for result in similar_results:
                if result.chunk.uuid != content_id:
                    recommendations.append({
                        "uuid": result.chunk.uuid,
                        "title": result.chunk.title,
                        "text": result.chunk.text,
                        "type": result.chunk.type,
                        "category": result.chunk.category,
                        "relevance_score": result.relevance_score,
                        "similarity_reason": "Content-based similarity"
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting content-based recommendations: {e}")
            return []
    
    async def get_collaborative_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get collaborative filtering recommendations based on user behavior.
        
        Parameters:
            user_id (str): User ID for recommendations
            limit (int): Maximum number of recommendations
            
        Returns:
            List[Dict[str, Any]]: List of recommended content items
        """
        try:
            # Find content that similar users have interacted with
            # This is a simplified implementation - in practice, you'd have user interaction data
            
            # Get content from the same category as user's recent interactions
            user_preferences = await self._get_user_preferences(user_id)
            
            if not user_preferences:
                return []
            
            # Find content in preferred categories
            recommendations = []
            for category in user_preferences.get("categories", []):
                category_results = await self.client.search_chunks(
                    metadata_filter={
                        "category": category,
                        "uuid": {"$nin": user_preferences.get("viewed_content", [])}
                    },
                    limit=limit // len(user_preferences.get("categories", [1]))
                )
                
                for result in category_results:
                    recommendations.append({
                        "uuid": result.chunk.uuid,
                        "title": result.chunk.title,
                        "text": result.chunk.text,
                        "type": result.chunk.type,
                        "category": result.chunk.category,
                        "relevance_score": result.relevance_score,
                        "similarity_reason": f"Category preference: {category}"
                    })
            
            # Sort by relevance and return top results
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting collaborative recommendations: {e}")
            return []
    
    async def get_trending_content(
        self,
        time_window: timedelta = timedelta(days=7),
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending content based on recent activity.
        
        Parameters:
            time_window (timedelta): Time window for trending calculation
            limit (int): Maximum number of recommendations
            
        Returns:
            List[Dict[str, Any]]: List of trending content items
        """
        try:
            # Find recently created content
            cutoff_time = datetime.now() - time_window
            
            recent_results = await self.client.search_chunks(
                metadata_filter={
                    "created_at": {"$gte": cutoff_time.isoformat()}
                },
                limit=limit * 2  # Get more to filter by popularity
            )
            
            # In a real implementation, you'd calculate popularity based on views, likes, etc.
            # For this example, we'll use a simple heuristic based on content length and type
            
            trending_content = []
            for result in recent_results:
                popularity_score = self._calculate_popularity_score(result.chunk)
                
                trending_content.append({
                    "uuid": result.chunk.uuid,
                    "title": result.chunk.title,
                    "text": result.chunk.text,
                    "type": result.chunk.type,
                    "category": result.chunk.category,
                    "created_at": result.chunk.created_at,
                    "popularity_score": popularity_score,
                    "trending_reason": "Recently created content"
                })
            
            # Sort by popularity and return top results
            trending_content.sort(key=lambda x: x["popularity_score"], reverse=True)
            return trending_content[:limit]
            
        except Exception as e:
            print(f"Error getting trending content: {e}")
            return []
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations combining multiple strategies.
        
        Parameters:
            user_id (str): User ID for recommendations
            limit (int): Maximum number of recommendations
            
        Returns:
            List[Dict[str, Any]]: List of personalized recommendations
        """
        try:
            # Get user preferences and recent activity
            user_preferences = await self._get_user_preferences(user_id)
            recent_content = user_preferences.get("recent_content", [])
            
            if not recent_content:
                # New user - return trending content
                return await self.get_trending_content(limit=limit)
            
            # Get recommendations based on recent content
            all_recommendations = []
            
            # Content-based recommendations
            for content_id in recent_content[:3]:  # Use last 3 items
                content_recs = await self.get_content_based_recommendations(
                    content_id, limit=limit // 3
                )
                all_recommendations.extend(content_recs)
            
            # Collaborative recommendations
            collab_recs = await self.get_collaborative_recommendations(
                user_id, limit=limit // 2
            )
            all_recommendations.extend(collab_recs)
            
            # Remove duplicates and sort by relevance
            unique_recommendations = self._remove_duplicates(all_recommendations)
            unique_recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            print(f"Error getting personalized recommendations: {e}")
            return []
    
    async def search_and_recommend(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for content and provide recommendations.
        
        Parameters:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results and recommendations
        """
        try:
            # Perform search
            search_results = await self.client.search_chunks(
                search_str=query,
                limit=limit
            )
            
            # Get recommendations based on top search result
            recommendations = []
            if search_results:
                top_result = search_results[0]
                recommendations = await self.get_content_based_recommendations(
                    top_result.chunk.uuid,
                    limit=limit // 2
                )
            
            return {
                "search_results": [
                    {
                        "uuid": result.chunk.uuid,
                        "title": result.chunk.title,
                        "text": result.chunk.text,
                        "type": result.chunk.type,
                        "category": result.chunk.category,
                        "relevance_score": result.relevance_score
                    }
                    for result in search_results
                ],
                "recommendations": recommendations,
                "query": query,
                "total_results": len(search_results)
            }
            
        except Exception as e:
            print(f"Error in search and recommend: {e}")
            return {
                "search_results": [],
                "recommendations": [],
                "query": query,
                "total_results": 0
            }
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences and recent activity.
        
        Parameters:
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: User preferences and activity data
        """
        # In a real implementation, this would query a user database
        # For this example, we'll return mock data
        
        # Find content that the user has interacted with
        user_content = await self.client.search_chunks(
            metadata_filter={
                "metadata.user_id": user_id,
                "metadata.interaction_type": {"$in": ["view", "like", "bookmark"]}
            },
            limit=50
        )
        
        # Extract preferences
        categories = {}
        viewed_content = []
        
        for result in user_content:
            if result.chunk.category:
                categories[result.chunk.category] = categories.get(result.chunk.category, 0) + 1
            viewed_content.append(result.chunk.uuid)
        
        # Sort categories by frequency
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "user_id": user_id,
            "categories": [cat for cat, _ in sorted_categories[:5]],
            "viewed_content": viewed_content,
            "recent_content": viewed_content[-10:]  # Last 10 items
        }
    
    def _calculate_popularity_score(self, chunk: SemanticChunk) -> float:
        """
        Calculate popularity score for content.
        
        Parameters:
            chunk (SemanticChunk): Content chunk
            
        Returns:
            float: Popularity score
        """
        # Simple popularity calculation based on content characteristics
        score = 0.0
        
        # Content length factor
        text_length = len(chunk.text)
        if text_length > 1000:
            score += 0.3
        elif text_length > 500:
            score += 0.2
        else:
            score += 0.1
        
        # Content type factor
        if chunk.type == ChunkType.DOC_BLOCK:
            score += 0.2
        elif chunk.type == ChunkType.CODE_BLOCK:
            score += 0.3
        elif chunk.type == ChunkType.MESSAGE:
            score += 0.1
        
        # Category factor
        if chunk.category in ["programming", "ai", "technology"]:
            score += 0.2
        
        # Tags factor
        if chunk.tags and len(chunk.tags) > 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _remove_duplicates(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate recommendations.
        
        Parameters:
            recommendations (List[Dict[str, Any]]): List of recommendations
            
        Returns:
            List[Dict[str, Any]]: Deduplicated recommendations
        """
        seen_uuids = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec["uuid"] not in seen_uuids:
                seen_uuids.add(rec["uuid"])
                unique_recommendations.append(rec)
        
        return unique_recommendations


async def main():
    """Demonstrate content recommendation system."""
    print("Content Recommendation System Demo")
    print("=" * 40)
    
    # Initialize client and recommender
    client = await VectorStoreClient.create("http://localhost:8007")
    recommender = ContentRecommender(client)
    
    try:
        # Create some sample content for demonstration
        await create_sample_content(client)
        
        # Demonstrate different recommendation types
        print("\n1. Content-based Recommendations:")
        content_recs = await recommender.get_content_based_recommendations(
            "sample-uuid-1", limit=5
        )
        for rec in content_recs:
            print(f"  - {rec['title']} (relevance: {rec['relevance_score']:.3f})")
        
        print("\n2. Trending Content:")
        trending = await recommender.get_trending_content(limit=5)
        for item in trending:
            print(f"  - {item['title']} (popularity: {item['popularity_score']:.3f})")
        
        print("\n3. Search and Recommend:")
        search_results = await recommender.search_and_recommend("machine learning", limit=5)
        print(f"  Search results: {search_results['total_results']}")
        print(f"  Recommendations: {len(search_results['recommendations'])}")
        
        print("\n4. Personalized Recommendations:")
        personalized = await recommender.get_personalized_recommendations("user123", limit=5)
        for rec in personalized:
            print(f"  - {rec['title']} (reason: {rec.get('similarity_reason', 'N/A')})")
        
    finally:
        await client.close()


async def create_sample_content(client: VectorStoreClient):
    """Create sample content for demonstration."""
    sample_chunks = [
        SemanticChunk(
            body="Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            text="Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Introduction to Machine Learning",
            category="ai",
            tags=["machine-learning", "ai", "introduction"],
            metadata={"user_id": "user123", "interaction_type": "view"}
        ),
        SemanticChunk(
            body="Deep learning uses neural networks with multiple layers to model complex patterns in data.",
            text="Deep learning uses neural networks with multiple layers to model complex patterns in data.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Deep Learning Fundamentals",
            category="ai",
            tags=["deep-learning", "neural-networks", "ai"],
            metadata={"user_id": "user123", "interaction_type": "like"}
        ),
        SemanticChunk(
            body="Python is a versatile programming language widely used in data science and machine learning.",
            text="Python is a versatile programming language widely used in data science and machine learning.",
            type=ChunkType.DOC_BLOCK,
            language=LanguageEnum.EN,
            title="Python for Data Science",
            category="programming",
            tags=["python", "data-science", "programming"],
            metadata={"user_id": "user456", "interaction_type": "bookmark"}
        )
    ]
    
    result = await client.create_chunks(sample_chunks)
    print(f"Created {result.total_created} sample chunks")


if __name__ == "__main__":
    asyncio.run(main()) 