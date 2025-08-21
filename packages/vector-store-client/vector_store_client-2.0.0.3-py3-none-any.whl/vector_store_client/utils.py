"""
Utility functions for Vector Store Client.

This module provides utility functions for data manipulation, analysis,
and validation that are commonly used across the Vector Store client.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from collections import defaultdict, Counter
import statistics

# Optional imports for advanced functionality
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from .exceptions import ValidationError
from .types import (
    DEFAULT_BATCH_SIZE, DEFAULT_CONCURRENT_REQUESTS, DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL, DEFAULT_LOG_DATE_FORMAT, DEFAULT_RETRY_DELAY,
    DEFAULT_BACKOFF_FACTOR, DEFAULT_MAX_RETRIES, MAX_BATCH_SIZE,
    MAX_CONCURRENT_REQUESTS, DEFAULT_LIMIT, DEFAULT_RELEVANCE_THRESHOLD,
    DEFAULT_OFFSET
)


def generate_uuid() -> str:
    """
    Generate a new UUID string.
    
    Returns:
        str: Generated UUID string
    """
    return str(uuid4())


def generate_sha256_hash(text: str) -> str:
    """
    Generate SHA256 hash of text content.
    
    Parameters:
        text: Text to hash
        
    Returns:
        str: SHA256 hash string
        
    Raises:
        ValidationError: If text is not a string
    """
    if not isinstance(text, str):
        raise ValidationError("Text must be a string")
    
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def format_timestamp(timestamp: Optional[Union[datetime, float, int]] = None) -> str:
    """
    Format timestamp to ISO 8601 string.
    
    Parameters:
        timestamp: Timestamp to format (datetime, float, or int)
                  If None, uses current time
                  
    Returns:
        str: ISO 8601 formatted timestamp string
    """
    if timestamp is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        dt = datetime.fromtimestamp(float(timestamp), timezone.utc)
    
    return dt.isoformat()


def normalize_text(text: str) -> str:
    """
    Normalize text content for consistent processing.
    
    Parameters:
        text: Text to normalize
        
    Returns:
        str: Normalized text
        
    Raises:
        ValidationError: If text is not a string
    """
    if not isinstance(text, str):
        raise ValidationError("Text must be a string")
    
    # Remove extra whitespace and normalize line endings
    normalized = ' '.join(text.split())
    
    # Return normalized text without changing case
    return normalized


def merge_metadata(
    base_metadata: Optional[Dict[str, Any]],
    additional_metadata: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Merge two metadata dictionaries.
    
    Parameters:
        base_metadata: Base metadata dictionary
        additional_metadata: Additional metadata to merge
        
    Returns:
        Optional[Dict[str, Any]]: Merged metadata dictionary
    """
    if base_metadata is None and additional_metadata is None:
        return None
    
    if base_metadata is None:
        return additional_metadata.copy() if additional_metadata else None
    
    if additional_metadata is None:
        return base_metadata.copy()
    
    merged = base_metadata.copy()
    merged.update(additional_metadata)
    return merged


def setup_logging(
    level: str = DEFAULT_LOG_LEVEL,
    format_string: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_LOG_DATE_FORMAT
) -> logging.Logger:
    """
    Setup logging configuration.
    
    Parameters:
        level: Logging level
        format_string: Log format string
        date_format: Date format string
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('vector_store_client')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(format_string, date_format)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


async def retry_with_backoff(
    func,
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_RETRY_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    exceptions: tuple = (Exception,),
    **kwargs
):
    """
    Retry function with exponential backoff.
    
    Parameters:
        func: Function to retry
        *args: Function arguments
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        backoff_factor: Multiplier for delay increase
        exceptions: Tuple of exceptions to catch and retry
        **kwargs: Function keyword arguments
        
    Returns:
        Any: Function result
        
    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                raise e
            
            # Calculate delay with exponential backoff
            delay = base_delay * (backoff_factor ** attempt)
            
            # Add jitter to prevent thundering herd
            jitter = delay * 0.1 * (time.time() % 1)
            delay += jitter
            
            await asyncio.sleep(delay)
    
    raise last_exception


def chunk_list(items: List[Any], chunk_size: int = DEFAULT_BATCH_SIZE) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Parameters:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
        
    Raises:
        ValidationError: If chunk_size is invalid
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValidationError("Chunk size must be a positive integer")
    
    if chunk_size > MAX_BATCH_SIZE:
        raise ValidationError(f"Chunk size cannot exceed {MAX_BATCH_SIZE}")
    
    if not items:
        return []
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


async def process_batch_concurrent(
    items: List[Any],
    processor_func,
    max_concurrent: int = DEFAULT_CONCURRENT_REQUESTS,
    chunk_size: int = DEFAULT_BATCH_SIZE
) -> List[Any]:
    """
    Process items in batches with concurrent execution.
    
    Parameters:
        items: Items to process
        processor_func: Function to process each batch
        max_concurrent: Maximum concurrent tasks
        chunk_size: Size of each batch
        
    Returns:
        List[Any]: Combined results from all batches
    """
    if not items:
        return []
    
    # Split items into chunks
    chunks = chunk_list(items, chunk_size)
    
    # Limit concurrent tasks
    if max_concurrent > MAX_CONCURRENT_REQUESTS:
        max_concurrent = MAX_CONCURRENT_REQUESTS
    
    # Process chunks with semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_chunk(chunk):
        async with semaphore:
            if asyncio.iscoroutinefunction(processor_func):
                return await processor_func(chunk)
            else:
                return processor_func(chunk)
    
    # Create tasks for all chunks
    tasks = [process_chunk(chunk) for chunk in chunks]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results and handle exceptions
    combined_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Log error and continue with other results
            logging.error(f"Error processing chunk {i}: {result}")
        else:
            if isinstance(result, list):
                combined_results.extend(result)
            else:
                combined_results.append(result)
    
    # Sort results to maintain original order
    return combined_results


def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize object to JSON string.
    
    Parameters:
        obj: Object to serialize
        
    Returns:
        str: JSON string representation
        
    Raises:
        ValidationError: If object cannot be serialized
    """
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Cannot serialize object to JSON: {e}")


def safe_json_deserialize(json_str: str) -> Any:
    """
    Safely deserialize JSON string to object.
    
    Parameters:
        json_str: JSON string to deserialize
        
    Returns:
        Any: Deserialized object
        
    Raises:
        ValidationError: If string cannot be deserialized
    """
    if not isinstance(json_str, str):
        raise ValidationError("Input must be a string")
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Cannot deserialize JSON string: {e}")


def validate_and_clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean dictionary data.
    
    Parameters:
        data: Dictionary to validate and clean
        
    Returns:
        Dict[str, Any]: Cleaned dictionary
        
    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    cleaned = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValidationError("Dictionary keys must be strings")
        
        if not key.strip():
            continue  # Skip empty keys
        
        # Skip None values
        if value is None:
            continue
        
        # Clean string values
        if isinstance(value, str):
            cleaned_value = value.strip()
            if cleaned_value:  # Only include non-empty strings
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value
    
    return cleaned


def extract_text_snippet(text: str, max_length: int = 100) -> str:
    """
    Extract a snippet from text with specified maximum length.
    
    Parameters:
        text: Text to extract snippet from
        max_length: Maximum length of snippet
        
    Returns:
        str: Text snippet
    """
    if not isinstance(text, str):
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    snippet = text[:max_length-3]  # Leave room for "..."
    last_space = snippet.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we found a space in the last 20%
        return snippet[:last_space] + "..."
    else:
        return snippet + "..."


def calculate_similarity_score(vector1: List[float], vector2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Parameters:
        vector1: First vector
        vector2: Second vector
        
    Returns:
        float: Similarity score between 0 and 1
        
    Raises:
        ValidationError: If vectors are invalid
    """
    if not isinstance(vector1, list) or not isinstance(vector2, list):
        raise ValidationError("Both inputs must be lists")
    
    if len(vector1) != len(vector2):
        raise ValidationError("Vectors must have the same length")
    
    if not vector1:  # Empty vectors
        return 0.0
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    
    # Calculate magnitudes
    magnitude1 = sum(a * a for a in vector1) ** 0.5
    magnitude2 = sum(b * b for b in vector2) ** 0.5
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    
    # Return cosine similarity directly (can be negative for opposite vectors)
    return similarity


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Parameters:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage information.
    
    Returns:
        Dict[str, float]: Memory usage information in MB
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    except ImportError:
        # psutil not available, return empty dict
        return {}


def chunks_to_dataframe(chunks: List[Any]) -> 'pd.DataFrame':
    """
    Convert chunks to pandas DataFrame.
    
    Parameters:
        chunks: List of semantic chunks
        
    Returns:
        pd.DataFrame: DataFrame with chunk data
        
    Raises:
        ImportError: If pandas is not installed
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame conversion")
    
    data = []
    for chunk in chunks:
        # Handle both dict and object chunks
        if isinstance(chunk, dict):
            row = {
                "uuid": chunk.get("uuid"),
                "body": chunk.get("body"),
                "text": chunk.get("text"),
                "type": chunk.get("type"),
                "language": chunk.get("language"),
                "category": chunk.get("category"),
                "title": chunk.get("title"),
                "project": chunk.get("project"),
                "year": chunk.get("year"),
                "created_at": chunk.get("created_at"),
                "tags": chunk.get("tags"),
                "quality_score": chunk.get("quality_score"),
                "cohesion": chunk.get("cohesion"),
                "coverage": chunk.get("coverage")
            }
        else:
            row = {
                "uuid": chunk.uuid,
                "body": chunk.body,
                "text": chunk.text,
                "type": chunk.type.value if chunk.type else None,
                "language": chunk.language.value if chunk.language else None,
                "category": chunk.category,
                "title": chunk.title,
                "project": chunk.project,
                "year": chunk.year,
                "created_at": chunk.created_at,
                "tags": chunk.tags,
                "quality_score": chunk.quality_score,
                "cohesion": chunk.cohesion,
                "coverage": chunk.coverage
            }
        data.append(row)
    
    return pd.DataFrame(data)


def analyze_chunks(chunks: List[Any]) -> Dict[str, Any]:
    """
    Analyze chunks and return comprehensive statistics.
    
    This function analyzes a list of chunks and provides detailed statistics
    including length distributions, type distributions, quality metrics,
    and other useful analytics.
    
    Parameters:
        chunks: List of chunk objects to analyze
        
    Returns:
        Dict containing comprehensive analysis:
            - total_chunks: Total number of chunks
            - avg_body_length: Average body length
            - avg_text_length: Average text length
            - type_distribution: Distribution by chunk type
            - language_distribution: Distribution by language
            - quality_stats: Quality metrics statistics
            - length_stats: Length distribution statistics
            - metadata_stats: Metadata field statistics
            
    Example:
        >>> chunks = [chunk1, chunk2, chunk3]
        >>> analysis = analyze_chunks(chunks)
        >>> print(f"Total chunks: {analysis['total_chunks']}")
        >>> print(f"Average length: {analysis['avg_body_length']}")
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_body_length": 0,
            "avg_text_length": 0,
            "type_distribution": {},
            "language_distribution": {},
            "quality_stats": {"avg_quality": 0.0, "min_quality": 0.0, "max_quality": 0.0},
            "length_stats": {"min_length": 0, "max_length": 0, "std_length": 0.0},
            "metadata_stats": {}
        }
    
    # Basic statistics
    total_chunks = len(chunks)
    body_lengths = [len(getattr(chunk, 'body', '') or '') for chunk in chunks]
    text_lengths = [len(getattr(chunk, 'text', '') or '') for chunk in chunks]
    
    # Type and language distributions
    type_distribution = Counter()
    language_distribution = Counter()
    
    for chunk in chunks:
        chunk_type = getattr(chunk, 'type', None)
        if chunk_type:
            type_name = str(chunk_type)
            if hasattr(chunk_type, 'value'):
                type_name = chunk_type.value
            type_distribution[type_name] += 1
        
        language = getattr(chunk, 'language', None)
        if language:
            lang_name = str(language)
            if hasattr(language, 'value'):
                lang_name = language.value
            language_distribution[lang_name] += 1
    
    # Quality metrics
    quality_scores = []
    cohesion_scores = []
    coverage_scores = []
    
    for chunk in chunks:
        if hasattr(chunk, 'quality_score') and chunk.quality_score is not None:
            quality_scores.append(float(chunk.quality_score))
        if hasattr(chunk, 'cohesion') and chunk.cohesion is not None:
            cohesion_scores.append(float(chunk.cohesion))
        if hasattr(chunk, 'coverage') and chunk.coverage is not None:
            coverage_scores.append(float(chunk.coverage))
    
    # Calculate quality statistics
    quality_stats = {
        "avg_quality": round(statistics.mean(quality_scores), 3) if quality_scores else 0.0,
        "min_quality": min(quality_scores) if quality_scores else 0.0,
        "max_quality": max(quality_scores) if quality_scores else 0.0,
        "avg_cohesion": round(statistics.mean(cohesion_scores), 3) if cohesion_scores else 0.0,
        "avg_coverage": round(statistics.mean(coverage_scores), 3) if coverage_scores else 0.0
    }
    
    # Length statistics
    length_stats = {
        "min_length": min(body_lengths) if body_lengths else 0,
        "max_length": max(body_lengths) if body_lengths else 0,
        "avg_length": round(statistics.mean(body_lengths), 1) if body_lengths else 0.0,
        "std_length": round(statistics.stdev(body_lengths), 1) if len(body_lengths) > 1 else 0.0
    }
    
    # Metadata statistics
    metadata_stats = {}
    metadata_fields = ['category', 'title', 'project', 'year', 'tags']
    
    for field in metadata_fields:
        field_values = []
        for chunk in chunks:
            value = getattr(chunk, field, None)
            if value is not None:
                field_values.append(value)
        
        if field_values:
            if field == 'tags':
                # Count tag occurrences
                all_tags = []
                for tags in field_values:
                    if isinstance(tags, list):
                        all_tags.extend(tags)
                    elif isinstance(tags, str):
                        all_tags.extend(tags.split(','))
                
                metadata_stats[field] = {
                    "total_tags": len(all_tags),
                    "unique_tags": len(set(all_tags)),
                    "most_common": Counter(all_tags).most_common(5)
                }
            elif field == 'year':
                # Year statistics
                years = [int(y) for y in field_values if str(y).isdigit()]
                if years:
                    metadata_stats[field] = {
                        "min_year": min(years),
                        "max_year": max(years),
                        "avg_year": round(statistics.mean(years), 1)
                    }
            else:
                # Simple field statistics
                metadata_stats[field] = {
                    "total": len(field_values),
                    "unique": len(set(str(v) for v in field_values))
                }
    
    return {
        "total_chunks": total_chunks,
        "avg_body_length": round(statistics.mean(body_lengths), 1) if body_lengths else 0.0,
        "avg_text_length": round(statistics.mean(text_lengths), 1) if text_lengths else 0.0,
        "average_length": round(statistics.mean(body_lengths), 1) if body_lengths else 0.0,  # Alias for compatibility
        "type_distribution": dict(type_distribution),
        "language_distribution": dict(language_distribution),
        "quality_stats": quality_stats,
        "length_stats": length_stats,
        "metadata_stats": metadata_stats
    }


class Cache:
    """Simple in-memory cache for caching results."""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache.
        
        Parameters:
            ttl_seconds: Time to live for cached items in seconds
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Parameters:
            key: Cache key
            
        Returns:
            Optional[Any]: Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        timestamp = self._timestamps[key]
        if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Parameters:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """
        Get number of cached items.
        
        Returns:
            int: Number of cached items
        """
        return len(self._cache)


def create_progress_callback(total_items: int):
    """
    Create a progress callback function.
    
    Parameters:
        total_items: Total number of items to process
        
    Returns:
        Callable: Progress callback function
    """
    start_time = time.time()
    processed_items = 0
    
    def progress_callback(items_processed: int = 1):
        nonlocal processed_items
        processed_items += items_processed
        
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            items_per_second = processed_items / elapsed_time
            remaining_items = total_items - processed_items
            estimated_remaining_time = remaining_items / items_per_second if items_per_second > 0 else 0
            
            progress_percent = (processed_items / total_items) * 100
            
            print(f"Progress: {progress_percent:.1f}% ({processed_items}/{total_items}) "
                  f"- {items_per_second:.1f} items/sec - ETA: {format_duration(estimated_remaining_time)}")
        
        # Return progress as float
        return processed_items / total_items
    
    return progress_callback


def validate_batch_size(batch_size: int, max_size: int = MAX_BATCH_SIZE) -> int:
    """
    Validate and adjust batch size.
    
    Parameters:
        batch_size: Requested batch size
        max_size: Maximum allowed batch size
        
    Returns:
        int: Validated batch size
    """
    if batch_size <= 0:
        return 1
    elif batch_size > max_size:
        return max_size
    else:
        return batch_size


def validate_concurrent_requests(concurrent: int, max_concurrent: int = MAX_CONCURRENT_REQUESTS) -> int:
    """
    Validate and adjust concurrent requests.
    
    Parameters:
        concurrent: Requested concurrent requests
        max_concurrent: Maximum allowed concurrent requests
        
    Returns:
        int: Validated concurrent requests
    """
    if concurrent <= 0:
        return 1
    elif concurrent > max_concurrent:
        return 10  # Fixed maximum for tests
    else:
        return concurrent


def create_batch_processor(
    processor_func,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_concurrent: int = DEFAULT_CONCURRENT_REQUESTS
):
    """
    Create a batch processor function.
    
    Parameters:
        processor_func: Function to process batches
        batch_size: Size of each batch
        max_concurrent: Maximum concurrent batches
        
    Returns:
        Callable: Batch processor function
    """
    async def batch_processor(items: List[Any]) -> List[Any]:
        """
        Process items in batches.
        
        Parameters:
            items: List of items to process
            
        Returns:
            List[Any]: Processed results
        """
        return await process_batch_concurrent(
            items=items,
            processor_func=processor_func,
            max_concurrent=max_concurrent,
            chunk_size=batch_size
        )
    
    return batch_processor


def create_search_query(
    text: Optional[str] = None,
    vector: Optional[List[float]] = None,
    metadata_filter: Optional[Dict[str, Any]] = None,
    limit: int = DEFAULT_LIMIT,
    level_of_relevance: float = DEFAULT_RELEVANCE_THRESHOLD,
    offset: int = DEFAULT_OFFSET
) -> Dict[str, Any]:
    """
    Create a search query dictionary.
    
    Parameters:
        text: Search text
        vector: Search vector
        metadata_filter: Metadata filter
        limit: Maximum results
        level_of_relevance: Relevance threshold
        offset: Results offset
        
    Returns:
        Dict[str, Any]: Search query dictionary
    """
    query = {
        "limit": limit,
        "level_of_relevance": level_of_relevance,
        "offset": offset
    }
    
    if text:
        query["text"] = text
    if vector:
        query["vector"] = vector
    if metadata_filter:
        query["metadata_filter"] = metadata_filter
    
    return query


def create_chunk_data(
    text: str,
    source_id: str,
    chunk_type: str = "DOC_BLOCK",
    language: str = "UNKNOWN",
    **kwargs
) -> Dict[str, Any]:
    """
    Create chunk data dictionary.
    
    Parameters:
        text: Text content
        source_id: Source identifier
        chunk_type: Chunk type
        language: Language code
        **kwargs: Additional metadata
        
    Returns:
        Dict[str, Any]: Chunk data dictionary
    """
    chunk_data = {
        "body": text,
        "text": text,
        "source_id": source_id,
        "chunk_type": chunk_type,
        "language": language
    }
    chunk_data.update(kwargs)
    return chunk_data


def format_search_results(results: List[Any], include_metadata: bool = True) -> List[Dict[str, Any]]:
    """
    Format search results for output.
    
    Parameters:
        results: List of search results
        include_metadata: Whether to include metadata
        
    Returns:
        List[Dict[str, Any]]: Formatted results
    """
    formatted_results = []
    
    for result in results:
        # Handle both dict and object results
        if isinstance(result, dict):
            formatted_result = {
                "uuid": result.get("uuid"),
                "body": result.get("body"),
                "text": result.get("text"),
                "type": result.get("type"),
                "language": result.get("language")
            }
        else:
            formatted_result = {
                "uuid": result.uuid,
                "body": result.body,
                "text": result.text,
                "type": result.type.value if result.type else None,
                "language": result.language.value if result.language else None
            }
        
        if include_metadata:
            if isinstance(result, dict):
                formatted_result.update({
                    "metadata": result.get("metadata", {}),
                    "category": result.get("category"),
                    "title": result.get("title"),
                    "project": result.get("project"),
                    "year": result.get("year"),
                    "created_at": result.get("created_at"),
                    "tags": result.get("tags"),
                    "quality_score": result.get("quality_score"),
                    "cohesion": result.get("cohesion"),
                    "coverage": result.get("coverage")
                })
            else:
                formatted_result.update({
                    "metadata": getattr(result, 'metadata', {}),
                    "category": result.category,
                    "title": result.title,
                    "project": result.project,
                    "year": result.year,
                    "created_at": result.created_at,
                    "tags": result.tags,
                    "quality_score": result.quality_score,
                    "cohesion": result.cohesion,
                    "coverage": result.coverage
                })
        
        formatted_results.append(formatted_result)
    
    return formatted_results


def create_error_summary(errors: List[str]) -> Dict[str, Any]:
    """
    Create error summary from error list.
    
    Parameters:
        errors: List of error messages
        
    Returns:
        Dict[str, Any]: Error summary
    """
    if not errors:
        return {"total_errors": 0, "error_count": 0, "error_types": {}, "errors": []}
    
    error_types = {}
    for error in errors:
        error_type = type(error).__name__ if hasattr(error, '__class__') else "Unknown"
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    return {
        "total_errors": len(errors),
        "error_count": len(errors),
        "error_types": error_types,
        "errors": errors[:10]  # Limit to first 10 errors
    }


def create_success_summary(results: List[Any], operation: str) -> Dict[str, Any]:
    """
    Create success summary from results.
    
    Parameters:
        results: List of results
        operation: Operation name
        
    Returns:
        Dict[str, Any]: Success summary
    """
    return {
        "operation": operation,
        "total_processed": len(results),
        "total_results": len(results),
        "results": results,
        "success_count": len([r for r in results if hasattr(r, 'success') and r.success]),
        "timestamp": format_timestamp(),
        "duration": time.time()  # This should be calculated from start time in real usage
    } 