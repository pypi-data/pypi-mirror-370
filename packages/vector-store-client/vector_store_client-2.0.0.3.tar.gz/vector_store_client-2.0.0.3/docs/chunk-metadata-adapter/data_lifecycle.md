# Data Lifecycle

- [Index](#index)
- [Glossary](#glossary)
- [Lifecycle Stages](#lifecycle-stages)
- [Detailed Stage Descriptions](#detailed-stage-descriptions)
- [Filtering and State Transitions](#filtering-and-state-transitions)
- [Benefits](#benefits)
- [See Also](#see-also)

---

## Index

- [Glossary](#glossary)
- [Lifecycle Stages](#lifecycle-stages)
- [Detailed Stage Descriptions](#detailed-stage-descriptions)
- [Filtering and State Transitions](#filtering-and-state-transitions)
- [Benefits](#benefits)
- [See Also](#see-also)

---

## Glossary

**ChunkStatus** — Enum for lifecycle and operational states (see [Metadata.md](Metadata.md)).

**RAW** — Unprocessed data as received.
**CLEANED** — Data after initial cleaning.
**VERIFIED** — Data checked against rules/standards.
**VALIDATED** — Data validated in context/cross-checks.
**RELIABLE** — Fully verified, ready for critical use.
**NEW, INDEXED, OBSOLETE, REJECTED, IN_PROGRESS, NEEDS_REVIEW, ARCHIVED** — Operational statuses (see [Metadata.md](Metadata.md)).

---

## Lifecycle Stages

| Status      | Value        | Description |
|-------------|-------------|-------------|
| RAW         | "raw"       | Original, unprocessed data |
| CLEANED     | "cleaned"   | Data after cleaning |
| VERIFIED    | "verified"  | Data verified against rules |
| VALIDATED   | "validated" | Data validated in context |
| RELIABLE    | "reliable"  | Fully verified, reliable |

See [Metadata.md](Metadata.md) for full enum list and field details.

---

## Detailed Stage Descriptions

Each stage is represented by a `ChunkStatus` value. See [Usage.md](Usage.md) for code examples.

- **RAW**: Data as received, may contain errors, noise, duplicates. Not suitable for direct use.
- **CLEANED**: Obvious errors fixed, format standardized, still needs verification.
- **VERIFIED**: Checked for compliance with rules, constraints, standards. Integrity and uniqueness verified.
- **VALIDATED**: Cross-checked with other data/sources, context validated. Ready for decision-making.
- **RELIABLE**: Passed all checks, high quality, ready for critical use. All metrics (quality_score, coverage, etc.) can be set.

---

## Filtering and State Transitions

- Use `filter_chunks_by_status(chunks, min_status)` to select chunks by minimum lifecycle stage (see [Usage.md](Usage.md)).
- Chunks can move between states sequentially or as needed (e.g., REJECTED, NEEDS_REVIEW, etc.).
- See [Metadata.md](Metadata.md) for all status values and their meaning.

---

## Benefits

- **Transparency**: Clear state at each stage
- **Data Quality**: Control and improve quality
- **Audit/Tracking**: Full processing history
- **Risk Management**: Use data of appropriate reliability
- **Compliance**: Regulatory adherence
- **Process Optimization**: Analyze and improve workflows

---

## See Also

- [Metadata Fields & Statuses](Metadata.md)
- [Usage Guide](Usage.md)
- [Component Interaction](Component_Interaction.md)
- [Flat <-> Semantic Conversion](flat_semantic_conversion.md)

## Overview

This library implements a detailed data lifecycle model that tracks the state of data throughout all processing stages - from initial collection to final validation and usage. This is a critical component for systems requiring high reliability and data transparency.

## Detailed Description of Stages

### 1. RAW (Raw Data)

**Definition**: Data in its original, unprocessed form as it entered the system.

**Characteristics**:
- May contain errors, typos, noise
- Structure may be inconsistent
- May contain duplicates or contradictory information
- Not suitable for direct use in critical processes

**Code Example**:
```python
raw_chunk = builder.build_semantic_chunk(
    text="User data: John Doe, john@eample.com, 123-45-6789",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RAW
)
```

### 2. CLEANED (Cleaned Data)

**Definition**: Data that has undergone initial processing and cleaning.

**Characteristics**:
- Obvious typos and formatting issues fixed
- Clearly incorrect values removed or flagged
- Data format standardized
- Structure unified
- Still requires additional verification

**Cleaning Processes**:
- Fixing typos and spelling errors
- Normalizing case and formatting
- Removing duplicates
- Standardizing dates, numbers, addresses, phone numbers, etc.
- Converting to unified encoding and format

**Code Example**:
```python
cleaned_chunk = SemanticChunk(**raw_chunk.model_dump())
cleaned_chunk.text = "User data: John Doe, john@example.com, 123-456-7890"
cleaned_chunk.status = ChunkStatus.CLEANED
```

### 3. VERIFIED (Verified Data)

**Definition**: Data that has been checked for compliance with specific rules, constraints, and standards.

**Characteristics**:
- Confirmed compliance with business rules
- Integrity and consistency verified
- Constraints checked (length, value range, etc.)
- Compliance with formats and standards confirmed

**Verification Processes**:
- Checking email, phone, document formats
- Validation using regular expressions
- Checking constraints (min/max length, value range)
- Verification against reference data and classifiers
- Checking uniqueness of key fields

**Code Example**:
```python
verified_chunk = SemanticChunk(**cleaned_chunk.model_dump())
verified_chunk.status = ChunkStatus.VERIFIED
# Add verification tags
verified_chunk.tags.append("verified_email")
verified_chunk.tags.append("verified_phone")
```

### 4. VALIDATED (Validated Data)

**Definition**: Data that has undergone comprehensive validation considering context and cross-checks.

**Characteristics**:
- Confirmed consistency with other datasets
- Checked against external data sources
- Temporal and logical dependencies verified
- Data can be used for decision-making

**Validation Processes**:
- Cross-checking with other systems (CRM, ERP, etc.)
- Verification against official sources (registries, databases)
- Temporal validation (checking change history)
- Comprehensive business process verification

**Code Example**:
```python
validated_chunk = SemanticChunk(**verified_chunk.model_dump())
validated_chunk.status = ChunkStatus.VALIDATED
# Add reference to validation source
validated_chunk.links.append(f"reference:{reference_id}")
validated_chunk.tags.append("crm_validated")
```

### 5. RELIABLE (Reliable Data)

**Definition**: Fully verified, reliable data ready for use in critical systems.

**Characteristics**:
- Passed all verification and validation stages
- Has high level of reliability
- Can be used for mission-critical processes
- Usually accompanied by verification metadata
- Can be published or transferred to other systems

**Additional Metrics**:
- High quality indicators (quality_score, coverage, cohesion, boundary_prev, boundary_next)
- Complete processing history
- References to all verification and validation sources

**Code Example**:
```python
reliable_chunk = SemanticChunk(**validated_chunk.model_dump())
reliable_chunk.status = ChunkStatus.RELIABLE
# Fill all quality metrics
reliable_chunk.metrics.quality_score = 0.98
reliable_chunk.metrics.coverage = 0.95
reliable_chunk.metrics.cohesion = 0.9
reliable_chunk.metrics.boundary_prev = 0.85
reliable_chunk.metrics.boundary_next = 0.92
```

## Additional Lifecycle Statuses

In addition to the main stages, the system supports the following operational statuses:

| Status | Value | Description |
|--------|---------|----------|
| `NEW` | "new" | New data, not yet processed |
| `INDEXED` | "indexed" | Data added to search index |
| `OBSOLETE` | "obsolete" | Outdated data requiring updates |
| `REJECTED` | "rejected" | Data rejected due to critical issues |
| `IN_PROGRESS` | "in_progress" | Data being processed |
| `NEEDS_REVIEW` | "needs_review" | Data requiring manual review |
| `ARCHIVED` | "archived" | Archived data |

## Filtering Data by Reliability Level

The library provides mechanisms for filtering data by reliability level:

```python
def filter_chunks_by_status(chunks, min_status):
    """
    Filters chunks by minimum required status in the data lifecycle.
    
    Status order: 
    RAW < CLEANED < VERIFIED < VALIDATED < RELIABLE
    
    Args:
        chunks: list of chunks to filter
        min_status: minimum required status (ChunkStatus)
        
    Returns:
        filtered list of chunks
    """
    status_order = {
        ChunkStatus.RAW.value: 1,
        ChunkStatus.CLEANED.value: 2,
        ChunkStatus.VERIFIED.value: 3,
        ChunkStatus.VALIDATED.value: 4, 
        ChunkStatus.RELIABLE.value: 5
    }
    
    min_level = status_order.get(min_status.value, 0)
    
    return [
        chunk for chunk in chunks 
        if status_order.get(chunk.status.value, 0) >= min_level
    ]
```

Usage example:
```python
# Get only reliable data
reliable_only = filter_chunks_by_status(all_chunks, ChunkStatus.RELIABLE)

# Get verified and above data
verified_and_above = filter_chunks_by_status(all_chunks, ChunkStatus.VERIFIED)
```

## State Transitions

Data can transition between states sequentially (from RAW to RELIABLE) or in arbitrary order depending on business logic. For example:

1. If data fails verification, it can be sent back to CLEANED status for additional processing
2. Data can be marked as NEEDS_REVIEW at any stage if manual verification is required
3. Data can be marked as REJECTED if critical issues are discovered
4. When data is updated, it may return to RAW stage and go through the entire cycle again

## Approach Benefits

The structured approach to data lifecycle provides several benefits:

1. **Transparency** - clear understanding of data state at each stage
2. **Data Quality** - ability to control and improve data quality
3. **Audit and Tracking** - complete data processing history
4. **Risk Management** - using appropriate reliability level data for different tasks
5. **Compliance** - ability to prove adherence to regulatory requirements (GDPR, etc.)
6. **Process Optimization** - analysis and improvement of data processing workflows

## Complete Lifecycle Example

```python
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, ChunkStatus
import uuid

# Create builder and source ID
builder = ChunkMetadataBuilder(project="DataQualityProject")
source_id = str(uuid.uuid4())

# 1. RAW - Initial data input
raw_chunk = builder.build_semantic_chunk(
    text="User: Peter Smith, psmith@eample.cоm, New York, 18005551234",
    language="text",
    type=ChunkType.DOC_BLOCK,
    source_id=source_id,
    status=ChunkStatus.RAW,
    tags=["user_data", "personal"]
)
print(f"RAW: {raw_chunk.uuid}, status: {raw_chunk.status.value}")

# 2. CLEANED - Data cleaning
cleaned_chunk = SemanticChunk(**raw_chunk.model_dump())
# Fix typos in email and format phone
cleaned_chunk.text = "User: Peter Smith, psmith@example.com, New York, +1 (800) 555-1234"
cleaned_chunk.status = ChunkStatus.CLEANED
cleaned_chunk.tags.append("cleaned_email")
cleaned_chunk.tags.append("formatted_phone")
print(f"CLEANED: {cleaned_chunk.uuid}, status: {cleaned_chunk.status.value}")

# 3. VERIFIED - Data verification
verified_chunk = SemanticChunk(**cleaned_chunk.model_dump())
verified_chunk.status = ChunkStatus.VERIFIED
verified_chunk.tags.append("verified_email")
verified_chunk.tags.append("verified_phone")
# Add verification metadata
verified_chunk.metrics.quality_score = 0.75  # Preliminary quality assessment
print(f"VERIFIED: {verified_chunk.uuid}, status: {verified_chunk.status.value}")

# 4. VALIDATED - Context validation
validated_chunk = SemanticChunk(**verified_chunk.model_dump())
validated_chunk.status = ChunkStatus.VALIDATED
# Add reference to CRM record
reference_id = str(uuid.uuid4())
validated_chunk.links.append(f"reference:{reference_id}")
validated_chunk.tags.append("crm_validated")
validated_chunk.metrics.quality_score = 0.85  # Increase quality score
print(f"VALIDATED: {validated_chunk.uuid}, status: {validated_chunk.status.value}")

# 5. RELIABLE - Reliable data
reliable_chunk = SemanticChunk(**validated_chunk.model_dump())
reliable_chunk.status = ChunkStatus.RELIABLE
reliable_chunk.metrics.quality_score = 0.95  # High quality score
print(f"RELIABLE: {reliable_chunk.uuid}, status: {reliable_chunk.status.value}")

# Using data of different quality levels for different tasks
chunks = [raw_chunk, cleaned_chunk, verified_chunk, validated_chunk, reliable_chunk]

# For analytics, use only verified data
analytics_data = filter_chunks_by_status(chunks, ChunkStatus.VERIFIED)
print(f"Chunks for analytics: {len(analytics_data)}")

# For critical operations, use only reliable data
critical_data = filter_chunks_by_status(chunks, ChunkStatus.RELIABLE)
print(f"Chunks for critical operations: {len(critical_data)}")
```

## Conclusion

The implemented data lifecycle approach provides a transparent and robust mechanism for data quality management. It allows flexible process management and the use of data with appropriate reliability levels for different tasks, which is crucial for systems requiring high data quality. 

The library supports extended chunk quality metrics: quality_score, coverage, cohesion, boundary_prev, boundary_next (all float, range [0, 1], optional). 