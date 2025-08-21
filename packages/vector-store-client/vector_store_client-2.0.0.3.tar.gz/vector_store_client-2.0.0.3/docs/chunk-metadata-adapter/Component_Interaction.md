# Component Interaction

- [Index](#index)
- [Glossary](#glossary)
- [Architecture Overview](#architecture-overview)
- [Component Responsibilities](#component-responsibilities)
- [Integration Examples](#integration-examples)
- [See Also](#see-also)

---

## Index

- [Glossary](#glossary)
- [Architecture Overview](#architecture-overview)
- [Component Responsibilities](#component-responsibilities)
- [Integration Examples](#integration-examples)
- [See Also](#see-also)

---

## Glossary

**ChunkMetadataBuilder** — Facade for creating, converting, and validating chunk metadata (flat and structured).

**SemanticChunk** — Structured model for chunk metadata (nested fields, lists, metrics).

**FlatSemanticChunk** — Flat model for storage (all fields as primitives, lists as comma-separated strings).

**ChunkMetrics** — Quality and usage metrics (quality_score, coverage, cohesion, etc.).

**FeedbackMetrics** — User feedback (accepted, rejected, modifications).

**Enums** — ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum (see [Metadata.md](Metadata.md)).

---

## Architecture Overview

The package uses a layered architecture:

```
┌──────────────────────────────┐
│      Client Application      │
└──────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│  ChunkMetadataBuilder       │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   Data Models Layer         │
│ ┌───────────────┐           │
│ │ SemanticChunk │           │
│ │ FlatSemanticC.│           │
│ └───────┬───────┘           │
│         │                   │
│ ┌───────▼───────┐           │
│ │ ChunkMetrics  │           │
│ └───────┬───────┘           │
│         │                   │
│ ┌───────▼───────┐           │
│ │FeedbackMetric.│           │
│ └───────────────┘           │
└─────────────┬───────────────┘
              │
┌─────────────▼───────────────┐
│   Validation Layer          │
└─────────────────────────────┘
```

---

## Component Responsibilities

- **ChunkMetadataBuilder**: High-level API for building, converting, and validating metadata. Methods:
    - `build_flat_metadata`
    - `build_semantic_chunk`
    - `flat_to_semantic`
    - `semantic_to_flat`
- **SemanticChunk**: Structured model (see [Metadata.md](Metadata.md))
- **FlatSemanticChunk**: Flat model for storage
- **ChunkMetrics/FeedbackMetrics**: Quality, usage, and feedback metrics
- **Enums**: See [Metadata.md](Metadata.md)
- **Validation Layer**: Strict validation for UUID, ISO8601, enums, metrics, required fields

---

## Integration Examples

### Vector Database

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType
import chromadb

builder = ChunkMetadataBuilder(project="MyProject")
metadata = builder.build_flat_metadata(
    text="Content to embed",
    source_id="...",
    ordinal=1,
    type=ChunkType.DOC_BLOCK,
    language="en",
    coverage=0.9
)
collection = chromadb.Client().create_collection("documents")
collection.add(
    ids=[metadata["uuid"]],
    embeddings=get_embeddings(metadata["text"]),
    metadatas=[metadata]
)
```

### Document Store

```python
from chunk_metadata_adapter import ChunkMetadataBuilder
import json

builder = ChunkMetadataBuilder(project="MyProject")
chunk = builder.build_semantic_chunk(
    text="Document content",
    language="en",
    type="DocBlock",
    source_id="...",
    coverage=0.9
)
with open(f"chunks/{chunk.uuid}.json", "w") as f:
    flat_data = builder.semantic_to_flat(chunk)
    json.dump(flat_data, f)
```

### Processing Pipeline

```python
def process_document(doc_path, project_name):
    with open(doc_path, "r") as f:
        content = f.read()
    source_id = str(uuid.uuid4())
    builder = ChunkMetadataBuilder(project=project_name)
    chunks = []
    for i, text in enumerate(split_into_chunks(content)):
        chunk = builder.build_semantic_chunk(
            text=text,
            language="en",
            type="DocBlock",
            source_id=source_id,
            ordinal=i,
            source_path=doc_path,
            coverage=0.9
        )
        chunks.append(chunk)
    link_chunks(chunks)
    store_chunks(chunks)
    return chunks
```

---

## See Also

- [Metadata Fields & Types](Metadata.md)
- [Usage Guide](Usage.md)
- [Flat <-> Semantic Conversion](flat_semantic_conversion.md)
- [Data Lifecycle](data_lifecycle.en.md) 