# Metadata Structure

- [Project Goals](#project-goals)
- [Metadata Fields](#metadata-fields)
- [Model Structure](#model-structure)
- [Conversion, Validation, Autofill](#conversion-validation-autofill)
- [Best Practices](#best-practices)
- [See Also](#see-also)

---

## Project Goals

**Chunk Metadata Adapter** provides strict, unified, and validated metadata models for text/code chunks in search, RAG, NLP, and document systems. It ensures:
- Consistent metadata structure for all chunk types
- Strict validation and autofill for all fields
- Easy conversion between structured (Pydantic) and flat (key-value) formats
- Support for advanced analytics, aggregation, and lifecycle management

---

## Metadata Fields

All fields are strictly typed and validated. See [Enums and Metrics](#see-also) for details.

| Field                | Type/Enum                | Constraints/Values         | Description |
|----------------------|-------------------------|----------------------------|-------------|
| `uuid`               | `ChunkId` (UUIDv4 str)  | required, UUIDv4           | Unique chunk identifier |
| `source_id`          | `ChunkId` (UUIDv4 str)  | required, UUIDv4           | Source document ID |
| `project`            | Optional[str]           | ≤128 chars                 | Project name |
| `task_id`            | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Task ID |
| `subtask_id`         | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Subtask ID |
| `unit_id`            | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Processing unit ID |
| `type`               | `ChunkType`             | required, [enum][1]        | Chunk type |
| `role`               | Optional[`ChunkRole`]   | [enum][2], default SYSTEM | Author role |
| `language`           | Optional[`LanguageEnum`] | [enum][3], default UNKNOWN | Content language |
| `body`               | str                     | 1-10000 chars, required    | Original chunk text |
| `text`               | Optional[str]           | 0-10000 chars              | Normalized text for search |
| `summary`            | Optional[str]           | 0-512 chars                | Short summary of the chunk |
| `ordinal`            | Optional[int]           | ≥0, default 0              | Chunk order in source |
| `sha256`             | Optional[str]           | 64 hex chars               | SHA256 hash of the text |
| `created_at`         | Optional[str]           | ISO8601 with timezone      | Creation timestamp |
| `status`             | Optional[`ChunkStatus`] | [enum][4], default NEW     | Processing/lifecycle status |
| `source_path`        | Optional[str]           | ≤512 chars                 | Path to source file |
| `quality_score`      | Optional[float]         | 0-1                        | [Metric][5] |
| `coverage`           | Optional[float]         | 0-1                        | [Metric][5] |
| `cohesion`           | Optional[float]         | 0-1                        | [Metric][5] |
| `boundary_prev`      | Optional[float]         | 0-1                        | [Metric][5] |
| `boundary_next`      | Optional[float]         | 0-1                        | [Metric][5] |
| `used_in_generation` | Optional[bool]          | default None               | [Metric][5] |
| `feedback_accepted`  | Optional[int]           | ≥0                         | [Metric][5] |
| `feedback_rejected`  | Optional[int]           | ≥0                         | [Metric][5] |
| `feedback_modifications` | Optional[int]       | ≥0                         | [Metric][5] |
| `start`              | Optional[int]           | ≥0                         | Start offset in source |
| `end`                | Optional[int]           | ≥0, end ≥ start            | End offset in source |
| `category`           | Optional[str]           | ≤64 chars                  | Business category |
| `title`              | Optional[str]           | ≤256 chars                 | Title/short name |
| `year`               | Optional[int]           | 0-2100, default 0          | Year (e.g., publication) |
| `is_public`          | Optional[bool]          | default None               | Public flag |
| `is_deleted`         | Optional[bool]          | default None               | Soft delete flag |
| `source`             | Optional[str]           | ≤64 chars                  | Data source |
| `block_type`         | Optional[`BlockType`]   | [enum][6]                  | Source block type |
| `chunking_version`   | Optional[str]           | 1-32 chars, default '1.0'  | Chunking algorithm version |
| `metrics`            | Optional[`ChunkMetrics`] | see [metrics][5]          | Full metrics object |
| `block_id`           | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Source block ID |
| `embedding`          | Optional[Any]           |                            | Vector embedding |
| `block_index`        | Optional[int]           | ≥0                         | Block order in source |
| `source_lines_start` | Optional[int]           | ≥0                         | Start line in source file |
| `source_lines_end`   | Optional[int]           | ≥0                         | End line in source file |
| `tags`               | Optional[List[str]]     | ≤32 items, ≤32 chars/item  | Tags (list in structured, comma-str in flat) |
| `links`              | Optional[List[str]]     | ≤32 items, 'parent:uuid'/'related:uuid' | Chunk links |
| `block_meta`         | Optional[dict]          |                            | Extra block metadata |

**Block Metadata (block_meta):**
The `block_meta` field can contain additional metadata about the block. Common use cases include:

| Field                    | Type   | Description |
|--------------------------|--------|-------------|
| `total_chunks_in_source` | int    | Total number of chunks in the source document |
| `is_last_chunk`          | bool   | Whether this is the last chunk in the source |
| `is_first_chunk`         | bool   | Whether this is the first chunk in the source |
| `chunk_position`         | str    | Human-readable position (e.g., "3/10") |
| `chunk_percentage`       | float  | Percentage through the source (0-100) |
| `source_info`            | dict   | Additional source information |

**Example block_meta:**
```python
block_meta = {
    "total_chunks_in_source": 10,
    "is_last_chunk": False,
    "is_first_chunk": True,
    "chunk_position": "1/10",
    "chunk_percentage": 10.0,
    "source_info": {
        "total_sections": 9,
        "has_title": True,
        "has_conclusion": True
    }
}
```

**Filter queries with block_meta:**
```python
# Find last chunk in sources with 10+ chunks
"block_meta.total_chunks_in_source >= 10 AND block_meta.is_last_chunk = true"

# Find first chunk
"ordinal = 0 AND block_meta.is_first_chunk = true"

# Find chunks past 50% of source
"block_meta.chunk_percentage > 50"
```

| `tags_flat`          | Optional[str]           | ≤1024 chars                | Comma-separated tags for flat storage |
| `link_related`       | Optional[str]           |                            | Related chunk UUID |
| `link_parent`        | Optional[str]           |                            | Parent chunk UUID |
| `is_code`            | Optional[bool]          | computed field             | Whether chunk contains source code (auto-computed) |

[1]: #see-also
[2]: #see-also
[3]: #see-also
[4]: #see-also
[5]: #see-also
[6]: #see-also

---

## Detailed Field Descriptions

### Core Fields

| Field                | Type/Enum                | Constraints/Values         | Description | Autofill/Validation | Example |
|----------------------|-------------------------|----------------------------|-------------|---------------------|---------|
| `uuid`               | `ChunkId` (UUIDv4 str)  | required, UUIDv4           | Unique chunk identifier | Autogenerated if missing; must be valid UUIDv4 | `"de93be12-3af5-4e6d-9ad2-c2a843c0bfb5"` |
| `source_id`          | `ChunkId` (UUIDv4 str)  | required, UUIDv4           | Source document ID | Required; must be valid UUIDv4 | `"b7e2...c4"` |
| `project`            | Optional[str]           | ≤128 chars                 | Project name | Optional; empty string if missing | `"MyProject"` |
| `task_id`            | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Task ID | Optional; default UUID if missing | `"0000...0000"` |
| `subtask_id`         | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Subtask ID | Optional; default UUID if missing | `"0000...0000"` |
| `unit_id`            | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Processing unit ID | Optional; default UUID if missing | `"0000...0000"` |
| `type`               | `ChunkType`             | required, [enum][1]        | Chunk type | Required; validated against enum | `ChunkType.DOC_BLOCK` |
| `role`               | Optional[`ChunkRole`]   | [enum][2], default SYSTEM | Author role | Optional; default SYSTEM | `ChunkRole.DEVELOPER` |
| `language`           | Optional[`LanguageEnum`] | [enum][3], default UNKNOWN | Content language | Optional; default UNKNOWN | `LanguageEnum.EN` |
| `body`               | str                     | 1-10000 chars, required    | Original chunk text | Required; min 1 char | `"def foo(): ..."` |
| `text`               | Optional[str]           | 0-10000 chars              | Normalized chunk text | Optional; autofilled from body if missing | `"def foo(): ..."` |
| `summary`            | Optional[str]           | 0-512 chars                | Content summary | Optional | `"Short summary"` |
| `ordinal`            | Optional[int]           | ≥0, default 0              | Chunk order in source | Optional; default 0 | `0` |
| `sha256`             | Optional[str]           | 64 hex chars               | SHA256 of text | Autogenerated; must match pattern | `"a3f5..."` |
| `created_at`         | Optional[str]           | ISO8601 with timezone      | Creation timestamp | Autogenerated if missing; must be ISO8601 | `"2024-06-01T12:00:00+00:00"` |
| `status`             | Optional[`ChunkStatus`] | [enum][4], default NEW     | Processing/lifecycle status | Optional; default NEW | `ChunkStatus.RAW` |
| `source_path`        | Optional[str]           | ≤512 chars                 | Path to source file | Optional | `"src/file.py"` |
| `quality_score`      | Optional[float]         | 0-1                        | [Metric][5] | Optional; validated | `0.95` |
| `coverage`           | Optional[float]         | 0-1                        | [Metric][5] | Optional; validated | `0.8` |
| `cohesion`           | Optional[float]         | 0-1                        | [Metric][5] | Optional; validated | `0.7` |
| `boundary_prev`      | Optional[float]         | 0-1                        | [Metric][5] | Optional; validated | `0.6` |
| `boundary_next`      | Optional[float]         | 0-1                        | [Metric][5] | Optional; validated | `0.9` |
| `used_in_generation` | Optional[bool]          | default None               | [Metric][5] | Optional; default None | `True` |
| `feedback_accepted`  | Optional[int]           | ≥0                         | [Metric][5] | Optional; default None | `2` |
| `feedback_rejected`  | Optional[int]           | ≥0                         | [Metric][5] | Optional; default None | `1` |
| `feedback_modifications` | Optional[int]       | ≥0                         | [Metric][5] | Optional; default None | `3` |
| `start`              | Optional[int]           | ≥0                         | Start offset in source | Optional | `0` |
| `end`                | Optional[int]           | ≥0, end ≥ start            | End offset in source | Optional; must be ≥ start | `56` |
| `category`           | Optional[str]           | ≤64 chars                  | Business category | Optional | `"documentation"` |
| `title`              | Optional[str]           | ≤256 chars                 | Title/short name | Optional | `"Intro"` |
| `year`               | Optional[int]           | 0-2100, default 0          | Year (e.g., publication) | Optional; default 0 | `2024` |
| `is_public`          | Optional[bool]          | default None               | Public flag | Optional | `True` |
| `is_deleted`         | Optional[bool]          | default None               | Soft delete flag | Optional | `False` |
| `source`             | Optional[str]           | ≤64 chars                  | Data source | Optional | `"user"` |
| `block_type`         | Optional[`BlockType`]   | [enum][6]                  | Source block type | Optional | `BlockType.PARAGRAPH` |
| `chunking_version`   | Optional[str]           | 1-32 chars, default '1.0'  | Chunking algorithm version | Optional; default '1.0' | `"1.0"` |
| `metrics`            | Optional[`ChunkMetrics`] | see [metrics][5]          | Full metrics object | Optional | — |
| `block_id`           | `ChunkId` (UUIDv4 str)  | UUIDv4                     | Source block ID | Optional; default UUID | `"0000...0000"` |
| `embedding`          | Optional[Any]           |                            | Vector embedding | Optional | `[0.1, 0.2, ...]` |
| `block_index`        | Optional[int]           | ≥0                         | Block order in source | Optional | `1` |
| `source_lines_start` | Optional[int]           | ≥0                         | Start line in source file | Optional | `10` |
| `source_lines_end`   | Optional[int]           | ≥0                         | End line in source file | Optional | `12` |
| `tags`               | Optional[List[str]]     | ≤32 items, ≤32 chars/item  | Tags (list in structured, comma-str in flat) | Optional; validated, split/join | `["tag1", "tag2"]` |
| `links`              | Optional[List[str]]     | ≤32 items, 'parent:uuid'/'related:uuid' | Chunk links | Optional; validated, split/join | `["parent:...", "related:..."]` |
| `block_meta`         | Optional[dict]          |                            | Extra block metadata | Optional | `{ "author": "user1" }` |
| `tags_flat`          | Optional[str]           | ≤1024 chars                | Comma-separated tags for flat storage | Optional; for flat model compatibility | `"tag1,tag2,tag3"` |
| `link_related`       | Optional[str]           |                            | Related chunk UUID | Optional; for flat model compatibility | `"uuid-string"` |
| `link_parent`        | Optional[str]           |                            | Parent chunk UUID | Optional; for flat model compatibility | `"uuid-string"` |
| `is_code`            | Optional[bool]          | computed field             | Whether chunk contains source code | Auto-computed based on type and language | `True` |

---

### Enum Fields

#### ChunkType

- DocBlock
- CodeBlock
- Message
- Draft
- Task
- Subtask
- TZ
- Comment
- Log
- Metric

#### ChunkRole

- system
- user
- assistant
- tool
- reviewer
- developer

#### ChunkStatus

- new
- raw
- cleaned
- verified
- validated
- reliable
- indexed
- obsolete
- rejected
- in_progress
- needs_review
- archived

#### BlockType

- paragraph
- message
- section
- other

#### LanguageEnum

**Natural Languages:**
- UNKNOWN
- en (English)
- ru (Russian)
- uk (Ukrainian)
- de (German)
- fr (French)
- es (Spanish)
- zh (Chinese)
- ja (Japanese)

**Programming Languages (from guesslang):**
- Assembly
- Batchfile
- C
- C# (CSHARP)
- C++ (CPP)
- Clojure
- CMake
- COBOL
- CoffeeScript
- CSS
- CSV
- Dart
- DM
- Dockerfile
- Elixir
- Erlang
- Fortran
- Go
- Groovy
- Haskell
- HTML
- INI
- Java
- JavaScript
- JSON
- Julia
- Kotlin
- Lisp
- Lua
- Makefile
- Markdown
- Matlab
- Objective-C
- OCaml
- Pascal
- Perl
- PHP
- PowerShell
- Prolog
- Python
- R
- Ruby
- Rust
- Scala
- Shell
- SQL
- Swift
- TeX
- TOML
- TypeScript
- Verilog
- Visual Basic
- XML
- YAML

**Additional Languages:**
- 1C (ONEC) - 1С programming language

**Methods:**
- `is_programming_language(value)` - Returns True if the language is a programming language (not a natural language or UNKNOWN)

---

### Metrics (ChunkMetrics, FeedbackMetrics)

| Field               | Type   | Constraints | Description |
|---------------------|--------|-------------|-------------|
| quality_score       | float  | 0-1         | Quality score |
| coverage           | float  | 0-1         | Coverage |
| cohesion           | float  | 0-1         | Cohesion |
| boundary_prev      | float  | 0-1         | Similarity with previous chunk |
| boundary_next      | float  | 0-1         | Similarity with next chunk |
| matches            | int    | ≥0          | Retrieval matches |
| used_in_generation | bool   |             | Used in generation |
| used_as_input      | bool   |             | Used as input |
| used_as_context    | bool   |             | Used as context |
| feedback           | FeedbackMetrics |     | User feedback |

**FeedbackMetrics:**
- accepted: int (≥0) — How many times accepted
- rejected: int (≥0) — How many times rejected
- modifications: int (≥0) — Number of modifications after generation

---

### Business Logic, Autofill, Validation

- **UUID fields**: Must be valid UUIDv4. If missing/empty, autofilled with `ChunkId.default_value()`.  
- **Enum fields**: Validated against allowed values. If missing, autofilled with `.default_value()`:
  - `type`: **required** field, validated against `ChunkType` enum
  - `role`: default `ChunkRole.SYSTEM`
  - `status`: default `ChunkStatus.NEW`
  - `language`: default `LanguageEnum.UNKNOWN`
  - `block_type`: optional, no default
- **String fields**: min_length/max_length strictly enforced. If required and missing, autofilled with 'x' chars.
- **Numeric fields**: Ranges strictly enforced (ge/le). If required and missing, autofilled with min value.
- **Timestamps**: Must be ISO8601 with timezone. Autogenerated if missing using `datetime.now(timezone.utc).isoformat()`.
- **Body/Text**: `body` is required. If `text` is missing, it's autofilled from `body`.
- **SHA256**: Autogenerated from `body` or `text` if missing using SHA256 hash.
- **Collections**: 
  - `tags`/`links` — validated for length, content, and format
  - In flat storage: `tags_flat` uses comma-separated strings, `link_related`/`link_parent` for individual links
- **Links**: Must match pattern `parent:uuid` or `related:uuid` with valid UUID.
- **Metrics**: All metrics are optional, but if present — strictly validated with ranges [0,1] for floats.
- **Business fields**: Autofilled with defaults:
  - `category`, `title`, `source`: empty string `""`
  - `year`: `0` (converted to `None` in post-processing if remains 0)
  - `is_public`: `False`
  - `tags`, `links`: empty list `[]`
- **Computed fields**: Automatically calculated during chunk creation:
  - `is_code`: `True` if chunk type is `CODE_BLOCK` OR language is a programming language (not natural language or UNKNOWN)

---

For edge cases, conversion rules, and more — see [Flat <-> Semantic Conversion Rules](flat_semantic_conversion.md), [Usage Guide](Usage.md), and [Component Interaction](Component_Interaction.md).

---

## ВАЖНО: Поведение flat dict и fail-safe

- Если в поле-список (например, `tags`, `links`) приходит строка, не являющаяся валидным JSON или CSV, она превращается в список с этой строкой: `["строка"]`.
- Автоматическое автозаполнение min_length для строк/списков не применяется ко всем новым полям по умолчанию — требуется ручная настройка.
- Для всех типов: пустые строки, None, "null" и т.п. приводятся к дефолтным значениям ([], {}, False, 0) через универсальную функцию `normalize_empty_value`.
- Поле `is_code` вычисляется автоматически на основе типа и языка, но может быть переопределено вручную.
- FlatSemanticChunk как отдельная модель не реализован — используется flat dict + builder для совместимости с хранилищами.
- Поля `tags_flat`, `link_related`, `link_parent` поддерживаются только для совместимости с flat-структурой, не обязательны в основной модели.

---

## Model Structure

- **SemanticChunk**: Structured model (all fields, lists, dicts, metrics, etc.)
  - `is_code()` method: Returns `True` if chunk represents source code. Checks if chunk type is `CODE_BLOCK` or language is a programming language (not natural language or UNKNOWN).
  - `is_code` field: Automatically computed boolean field that indicates whether the chunk contains source code. Value is computed during chunk creation and matches the `is_code()` method result.
- **FlatSemanticChunk**: Flat model for storage (all fields as primitives, lists as comma-separated strings, links as separate fields)
- **ChunkMetrics**: Quality and usage metrics (see [metrics][5])
- **FeedbackMetrics**: User feedback (accepted, rejected, modifications)
- **Enums**: [ChunkType][1], [ChunkRole][2], [LanguageEnum][3], [ChunkStatus][4], [BlockType][6]

See [Component Interaction](Component_Interaction.md) for class diagrams and integration.

---

## Conversion, Validation, Autofill

- **Conversion**: Use `ChunkMetadataBuilder.semantic_to_flat()` and `flat_to_semantic()` for lossless conversion between models. See [Usage Guide](Usage.md).
- **Validation**: All fields are strictly validated (UUIDv4, ISO8601, ranges, enums, etc). See [Validation Rules](#metadata-fields).
- **Autofill**: Optional fields are autofilled with defaults (see code, utils.py). Enums use `.default_value()`. Empty UUIDs use a special valid UUIDv4.
- **Edge cases**: See [flat_semantic_conversion.md](flat_semantic_conversion.md) for conversion/autofill rules and edge cases.

---

## Best Practices

- Always set `block_id` for aggregation.
- Use `block_type`, `block_index` for analytics and structure recovery.
- Validate all UUIDs, timestamps, and links.
- Use `ordinal` to preserve order.
- Store `sha256` for deduplication.
- See [Usage Guide](Usage.md) for code examples.

---

## See Also

- [ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum](../chunk_metadata_adapter/models.py)
- [ChunkMetrics, FeedbackMetrics](../chunk_metadata_adapter/models.py)
- [Usage Guide](Usage.md)
- [Component Interaction](Component_Interaction.md)
- [Data Lifecycle](data_lifecycle.en.md)
- [Flat <-> Semantic Conversion Rules](flat_semantic_conversion.md) 