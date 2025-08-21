# Usage Guide

- [Index](#index)
- [Glossary](#glossary)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Performance Considerations](#performance-considerations)
- [See Also](#see-also)

---

## Index

- [Glossary](#glossary)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Performance Considerations](#performance-considerations)
- [See Also](#see-also)

---

## Glossary

**ChunkMetadataBuilder** — Main API for building, converting, and validating chunk metadata.

**SemanticChunk** — Structured model for chunk metadata (nested fields, lists, metrics).

**FlatSemanticChunk** — Flat model for storage (all fields as primitives, lists as comma-separated strings).

**ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum** — See [Metadata.md](Metadata.md).

---

## Installation

```bash
pip install chunk-metadata-adapter
```

## Basic Usage

### Creating Flat Metadata

The most common use case is creating flat metadata for a chunk. You can also specify optional quality metrics (coverage, cohesion, boundary_prev, boundary_next), all in [0, 1]:

```python
import uuid
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole

# Create a metadata builder for the project
builder = ChunkMetadataBuilder(project="MyProject", unit_id="chunker-service")

# Generate a UUID for the source document
source_id = str(uuid.uuid4())

# Create metadata for a code chunk
metadata = builder.build_flat_metadata(
    text="def hello_world():\n    print('Hello, World!')",
    source_id=source_id,
    ordinal=1,
    type=ChunkType.CODE_BLOCK,
    language="python",
    source_path="src/hello.py",
    source_lines_start=10,
    source_lines_end=12,
    tags="example,hello",
    role=ChunkRole.DEVELOPER,
    coverage=0.95,  # Optional, float in [0, 1]
    cohesion=0.8,   # Optional, float in [0, 1]
    boundary_prev=0.7, # Optional, float in [0, 1]
    boundary_next=0.9  # Optional, float in [0, 1]
)

print(f"Chunk UUID: {metadata['uuid']}")
print(f"SHA256: {metadata['sha256']}")
```

### Creating a Structured Chunk

When you need a fully structured object, you can also specify the same metrics:

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkRole

# Create a builder for documentation project
builder = ChunkMetadataBuilder(
    project="DocumentationProject",
    unit_id="docs-generator"
)

# Create a structured chunk
chunk = builder.build_semantic_chunk(
    text="# Introduction\n\nThis is the system documentation.",
    language="markdown",
    type=ChunkType.DOC_BLOCK,
    source_id=str(uuid.uuid4()),
    summary="Project introduction section",
    role=ChunkRole.DEVELOPER,
    source_path="docs/intro.md",
    source_lines=[1, 3],
    ordinal=0,
    task_id="DOC-123",
    subtask_id="DOC-123-A",
    tags=["introduction", "documentation", "overview"],
    links=[f"parent:{str(uuid.uuid4())}"],
    coverage=0.95,
    cohesion=0.8,
    boundary_prev=0.7,
    boundary_next=0.9
)

print(f"Chunk UUID: {chunk.uuid}")
print(f"Summary: {chunk.summary}")
```

### Converting Between Formats

The package allows seamless conversion between formats:

```python
# Convert from structured to flat format
flat_dict = builder.semantic_to_flat(chunk)

# Convert from flat to structured format
restored_chunk = builder.flat_to_semantic(flat_dict)

# Verify they are equivalent
assert restored_chunk.uuid == chunk.uuid
assert restored_chunk.text == chunk.text
assert restored_chunk.type == chunk.type
```

---

## Advanced Usage

### Processing a Chain of Chunks

When working with a sequence of chunks from a document:

```python
# Create a builder for the project
builder = ChunkMetadataBuilder(project="ChainExample", unit_id="processor")
source_id = str(uuid.uuid4())

# Create a sequence of chunks from document
chunks = []
for i, text in enumerate([
    "# Document Title",
    "## Section 1\n\nSection 1 content.",
    "## Section 2\n\nSection 2 content.",
    "## Conclusion\n\nFinal thoughts on the topic."
]):
    chunk = builder.build_semantic_chunk(
        text=text,
        language="markdown",
        type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        ordinal=i,
        summary=f"Section {i}" if i > 0 else "Title"
    )
    chunks.append(chunk)

# Create explicit links between chunks (parent-child relationships)
for i in range(1, len(chunks)):
    # Add link to title as parent
    chunks[i].links.append(f"parent:{chunks[0].uuid}")
    
# Process chunk metrics
for chunk in chunks:
    chunk.metrics.quality_score = 0.95
    chunk.metrics.used_in_generation = True
    chunk.metrics.feedback.accepted = 2
```

### Using UUID Validation

The package performs strict validation of UUIDs:

```python
try:
    metadata = builder.build_flat_metadata(
        text="Test content",
        source_id="invalid-uuid",  # Invalid UUID format
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language="text"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Working with Timestamps

All timestamps are validated and stored in ISO8601 format with timezone:

```python
from datetime import datetime, timezone

# Valid timestamp with timezone
valid_timestamp = datetime.now(timezone.utc).isoformat()

# The library will automatically use a valid timestamp format
chunk = builder.build_semantic_chunk(
    text="Time-sensitive content",
    language="text",
    type=ChunkType.MESSAGE,
    created_at=valid_timestamp  # Optional, automatically generated if not provided
)
```

### Round-trip with extended metrics

```python
chunk = builder.build_semantic_chunk(
    text="metrics roundtrip",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=str(uuid.uuid4()),
    coverage=0.7,
    cohesion=0.6,
    boundary_prev=0.5,
    boundary_next=0.4
)
flat = builder.semantic_to_flat(chunk)
restored = builder.flat_to_semantic(flat)
assert restored.metrics.coverage == 0.7
assert restored.metrics.cohesion == 0.6
assert restored.metrics.boundary_prev == 0.5
assert restored.metrics.boundary_next == 0.4
```

---

## Performance Considerations

- The `build_flat_metadata` method is faster than `build_semantic_chunk`
- Use flat model for high-throughput storage (e.g., vector DBs)
- Use structured model for analytics, validation, and advanced processing

---

## See Also

- [Metadata Fields & Types](Metadata.md)
- [Component Interaction](Component_Interaction.md)
- [Flat <-> Semantic Conversion](flat_semantic_conversion.md)
- [Data Lifecycle](data_lifecycle.en.md)