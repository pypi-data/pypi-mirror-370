# Redis Fixtures Guide

## Overview

This guide describes the unified Redis-related fixtures available in `tests/conftest.py` for consistent and maintainable testing of Redis storage scenarios.

## Available Fixtures

### Data Creation Fixtures

#### `sample_semantic_chunk_data`
Complete test data for creating `SemanticChunk` instances with all common fields.

```python
def test_with_sample_data(sample_semantic_chunk_data):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    assert chunk.quality_score == 0.85
    assert chunk.tags == ["python", "test", "function"]
```

#### `minimal_semantic_chunk_data`
Minimal data for creating `SemanticChunk` instances with only required fields.

```python
def test_with_minimal_data(minimal_semantic_chunk_data):
    chunk = SemanticChunk(**minimal_semantic_chunk_data)
    # Only uuid and body are provided
```

#### `sample_chunk_query_data`
Complete test data for creating `ChunkQuery` instances.

```python
def test_query_with_sample_data(sample_chunk_query_data):
    query = ChunkQuery(**sample_chunk_query_data)
    assert query.type == "DocBlock"
    assert query.limit == 50
```

#### `minimal_chunk_query_data`
Minimal data for creating `ChunkQuery` instances.

```python
def test_query_with_minimal_data(minimal_chunk_query_data):
    query = ChunkQuery(**minimal_chunk_query_data)
    # Only type and limit are provided
```

### Redis Flat Dictionary Fixtures

#### `redis_flat_dict_sample`
Pre-built flat dictionary representing data as it would appear in Redis storage.

```python
def test_redis_sample_data(redis_flat_dict_sample, restore_from_redis_flat_dict):
    chunk = restore_from_redis_flat_dict(redis_flat_dict_sample, SemanticChunk, from_redis=True)
    assert chunk.quality_score == 0.85  # Restored from "0.85" string
    assert chunk.is_public is True      # Restored from "true" string
```

#### `redis_flat_dict_with_empty_values`
Sample with empty string values for testing type restoration.

```python
def test_empty_values_restoration(redis_flat_dict_with_empty_values, restore_from_redis_flat_dict):
    chunk = restore_from_redis_flat_dict(redis_flat_dict_with_empty_values, SemanticChunk, from_redis=True)
    assert chunk.tags == []        # Empty string -> empty list
    assert chunk.is_public is False  # Empty string -> False
```

#### `redis_flat_dict_with_null_values`
Sample with null values for testing type restoration.

```python
def test_null_values_restoration(redis_flat_dict_with_null_values, restore_from_redis_flat_dict):
    chunk = restore_from_redis_flat_dict(redis_flat_dict_with_null_values, SemanticChunk, from_redis=True)
    assert chunk.tags == []        # None -> empty list
    assert chunk.is_public is False  # None -> False
```

#### `redis_flat_dict_with_embedding`
Sample with embedding included as JSON string.

```python
def test_embedding_restoration(redis_flat_dict_with_embedding, restore_from_redis_flat_dict, valid_embedding):
    chunk = restore_from_redis_flat_dict(redis_flat_dict_with_embedding, SemanticChunk, from_redis=True)
    assert chunk.embedding == valid_embedding  # JSON string -> list
```

### Utility Fixtures

#### `create_redis_flat_dict`
Factory function to convert objects to Redis flat dictionary format.

```python
def test_redis_conversion(create_redis_flat_dict, sample_semantic_chunk_data):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    redis_dict = create_redis_flat_dict(chunk, include_embedding=False)
    
    assert "embedding" not in redis_dict
    assert redis_dict["quality_score"] == "0.85"
    assert redis_dict["is_public"] == "true"
```

#### `restore_from_redis_flat_dict`
Factory function to restore objects from Redis flat dictionary format.

```python
def test_redis_restoration(restore_from_redis_flat_dict, redis_flat_dict_sample):
    chunk = restore_from_redis_flat_dict(redis_flat_dict_sample, SemanticChunk, from_redis=True)
    assert chunk.quality_score == 0.85  # String converted back to float
```

#### `compare_objects_for_redis`
Utility function to compare objects after Redis round-trip conversion.

```python
def test_round_trip_comparison(compare_objects_for_redis, sample_semantic_chunk_data, create_redis_flat_dict, restore_from_redis_flat_dict):
    original = SemanticChunk(**sample_semantic_chunk_data)
    redis_dict = create_redis_flat_dict(original, include_embedding=False)
    restored = restore_from_redis_flat_dict(redis_dict, SemanticChunk, from_redis=True)
    
    assert compare_objects_for_redis(original, restored, exclude_embedding=True)
```

## Best Practices

### 1. Use Fixtures for Consistent Test Data

Instead of creating test data inline:

```python
# ❌ Don't do this
def test_bad_example():
    chunk = SemanticChunk(
        uuid="12345678-1234-4123-8123-123456789012",
        body="test",
        quality_score=0.85,
        # ... many more fields
    )

# ✅ Do this
def test_good_example(sample_semantic_chunk_data):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
```

### 2. Use Utility Fixtures for Common Operations

```python
# ❌ Don't repeat conversion logic
def test_bad_example():
    chunk = SemanticChunk(**data)
    redis_dict = chunk.to_flat_dict(for_redis=True, include_embedding=False)
    restored = SemanticChunk.from_flat_dict(redis_dict, from_redis=True)

# ✅ Use utility fixtures
def test_good_example(sample_semantic_chunk_data, create_redis_flat_dict, restore_from_redis_flat_dict):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    redis_dict = create_redis_flat_dict(chunk, include_embedding=False)
    restored = restore_from_redis_flat_dict(redis_dict, SemanticChunk, from_redis=True)
```

### 3. Test Type Restoration Scenarios

```python
def test_type_restoration_scenarios(redis_flat_dict_with_empty_values, redis_flat_dict_with_null_values, restore_from_redis_flat_dict):
    # Test empty values
    chunk_empty = restore_from_redis_flat_dict(redis_flat_dict_with_empty_values, SemanticChunk, from_redis=True)
    assert chunk_empty.tags == []
    assert chunk_empty.is_public is False
    
    # Test null values
    chunk_null = restore_from_redis_flat_dict(redis_flat_dict_with_null_values, SemanticChunk, from_redis=True)
    assert chunk_null.tags == []
    assert chunk_null.is_public is False
```

### 4. Test Both SemanticChunk and ChunkQuery

```python
def test_both_object_types(sample_semantic_chunk_data, sample_chunk_query_data, create_redis_flat_dict, restore_from_redis_flat_dict):
    # Test SemanticChunk
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    chunk_redis = create_redis_flat_dict(chunk, include_embedding=False)
    chunk_restored = restore_from_redis_flat_dict(chunk_redis, SemanticChunk, from_redis=True)
    
    # Test ChunkQuery
    query = ChunkQuery(**sample_chunk_query_data)
    query_redis = create_redis_flat_dict(query, include_embedding=False)
    query_restored = restore_from_redis_flat_dict(query_redis, ChunkQuery, from_redis=True)
```

## Common Test Patterns

### Round-Trip Testing

```python
def test_redis_round_trip(
    sample_semantic_chunk_data,
    create_redis_flat_dict,
    restore_from_redis_flat_dict,
    compare_objects_for_redis
):
    # 1. Create original object
    original = SemanticChunk(**sample_semantic_chunk_data)
    
    # 2. Convert to Redis format
    redis_dict = create_redis_flat_dict(original, include_embedding=False)
    
    # 3. Verify Redis format
    assert "embedding" not in redis_dict
    assert redis_dict["quality_score"] == "0.85"
    
    # 4. Restore from Redis format
    restored = restore_from_redis_flat_dict(redis_dict, SemanticChunk, from_redis=True)
    
    # 5. Compare objects
    assert compare_objects_for_redis(original, restored, exclude_embedding=True)
```

### Embedding Testing

```python
def test_embedding_handling(
    sample_semantic_chunk_data,
    create_redis_flat_dict,
    restore_from_redis_flat_dict
):
    original = SemanticChunk(**sample_semantic_chunk_data)
    
    # Test without embedding (default)
    redis_dict_no_emb = create_redis_flat_dict(original, include_embedding=False)
    assert "embedding" not in redis_dict_no_emb
    
    # Test with embedding
    redis_dict_with_emb = create_redis_flat_dict(original, include_embedding=True)
    assert "embedding" in redis_dict_with_emb
    assert isinstance(redis_dict_with_emb["embedding"], str)
    
    # Test restoration
    restored = restore_from_redis_flat_dict(redis_dict_with_emb, SemanticChunk, from_redis=True)
    assert restored.embedding == original.embedding
```

### Type Restoration Testing

```python
def test_type_restoration(
    redis_flat_dict_with_empty_values,
    restore_from_redis_flat_dict
):
    chunk = restore_from_redis_flat_dict(
        redis_flat_dict_with_empty_values,
        SemanticChunk,
        from_redis=True
    )
    
    # Verify proper type restoration
    assert chunk.tags == []           # Empty string -> empty list
    assert chunk.links == []          # Empty string -> empty list
    assert chunk.block_meta == {}     # Empty string -> empty dict
    assert chunk.quality_score == 0.0 # Empty string -> 0.0
    assert chunk.feedback_accepted == 0  # Empty string -> 0
    assert chunk.is_public is False   # Empty string -> False
    assert chunk.is_deleted is False  # Empty string -> False
```

## Migration Guide

### From Inline Test Data

If you have existing tests with inline test data:

```python
# Before
def test_old_way():
    chunk = SemanticChunk(
        uuid="12345678-1234-4123-8123-123456789012",
        body="test content",
        quality_score=0.85,
        tags=["test"],
        # ... many more fields
    )
    redis_dict = chunk.to_flat_dict(for_redis=True)
    # ... rest of test

# After
def test_new_way(sample_semantic_chunk_data, create_redis_flat_dict):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    redis_dict = create_redis_flat_dict(chunk, include_embedding=False)
    # ... rest of test
```

### From Manual Redis Conversion

If you have existing tests with manual Redis conversion:

```python
# Before
def test_old_way():
    chunk = SemanticChunk(**data)
    redis_dict = chunk.to_flat_dict(for_redis=True, include_embedding=False)
    restored = SemanticChunk.from_flat_dict(redis_dict, from_redis=True)
    # Manual comparison...

# After
def test_new_way(sample_semantic_chunk_data, create_redis_flat_dict, restore_from_redis_flat_dict, compare_objects_for_redis):
    chunk = SemanticChunk(**sample_semantic_chunk_data)
    redis_dict = create_redis_flat_dict(chunk, include_embedding=False)
    restored = restore_from_redis_flat_dict(redis_dict, SemanticChunk, from_redis=True)
    assert compare_objects_for_redis(chunk, restored, exclude_embedding=True)
```

## Benefits

1. **Consistency**: All tests use the same test data format
2. **Maintainability**: Changes to test data only need to be made in one place
3. **Readability**: Tests focus on behavior rather than data setup
4. **Reusability**: Fixtures can be combined and customized as needed
5. **Reliability**: Pre-tested fixtures reduce the chance of test data errors 