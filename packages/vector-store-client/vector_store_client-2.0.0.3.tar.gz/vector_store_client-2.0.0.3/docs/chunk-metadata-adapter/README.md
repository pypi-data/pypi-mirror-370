# Chunk Metadata Adapter Documentation

This directory contains documentation for the `chunk_metadata_adapter` package.

## Documentation Files

- [Metadata Structure](Metadata.md) - Description of the metadata structure and fields
- [Usage Guide](Usage.md) - Guide for using the package with examples
- [Component Interaction](Component_Interaction.md) - Description of how the components interact

## Russian Documentation

Russian versions of documentation are available with `.ru` suffix before the extension:
- [Metadata Structure (RU)](Metadata.ru.md)
- [Usage Guide (RU)](Usage.ru.md)
- [Component Interaction (RU)](Component_Interaction.ru.md)

## API Reference

The package provides the following main components:

- `ChunkMetadataBuilder` - Main class for creating and transforming metadata
- `SemanticChunk` - Fully structured model for chunk metadata
- `FlatSemanticChunk` - Flat representation of chunk metadata for storage

For detailed API reference, see the [Python docstrings](../chunk_metadata_adapter/) in the source code.

- Support for extended chunk quality metrics: coverage, cohesion, boundary_prev, boundary_next 

---

## Glossary

**Chunk** — The minimal logical unit of text or code for which metadata is generated.

**SemanticChunk** — Structured chunk metadata model with nested objects and typed fields. Used for programmatic processing.

**FlatSemanticChunk** — Flat chunk metadata model for storage in key-value systems. All collections are serialized as strings, nested objects are flattened.

**ChunkId** — UUIDv4 identifier of a chunk or related object (source_id, block_id, etc.).

**ChunkType** — Type of chunk content (e.g., DocBlock, CodeBlock, Message, etc.).

**ChunkStatus** — Lifecycle or processing status of a chunk (RAW, CLEANED, VERIFIED, VALIDATED, RELIABLE, etc.).

**ChunkRole** — Role of the content author or source (DEVELOPER, USER, SYSTEM, etc.).

**ChunkMetrics** — Object with chunk quality and usage metrics (quality_score, coverage, cohesion, boundary_prev, boundary_next, etc.).

**FeedbackMetrics** — User feedback metrics (accepted, rejected, flagged, etc.).

**source_lines** — Range of source file lines to which the chunk refers.

**links** — Relationships between chunks in the format relation:uuid4 (e.g., parent:uuid, related:uuid).

**tags** — List of tags characterizing the chunk content.

**block_id, block_type, block_index, block_meta** — Fields for aggregation and reconstruction of the original document structure.

---

## Useful Links

- [Metadata Structure](Metadata.md)
- [Usage Guide](Usage.md)
- [Component Interaction](Component_Interaction.md)
- [Data Lifecycle](data_lifecycle.en.md)
- [Flat <-> Semantic Conversion Rules](flat_semantic_conversion.md)

---

For details, see also the Russian documentation and the API reference in the source code. 