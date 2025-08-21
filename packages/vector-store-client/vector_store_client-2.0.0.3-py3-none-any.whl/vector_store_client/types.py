"""
Vector Store Client Types.

This module defines type aliases, enums, and constants used throughout
the Vector Store client for type safety and data validation.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

from enum import Enum
from typing import Dict, List, Union, Any


# Type aliases for better code readability
ChunkId = str
Vector = List[float]
MetadataDict = Dict[str, Any]
SearchResult = List[Any]
JsonRpcId = Union[str, int, None]
JsonRpcResult = Union[Dict, List, str, bool, None]
MetadataFilter = Dict[str, Union[str, int, float, bool, List[str]]]
SearchParams = Dict[str, Union[str, int, float, MetadataFilter]]


class ChunkType(str, Enum):
    """
    Enumeration of chunk types.
    
    Defines the different types of content chunks that can be stored
    in the Vector Store, each with specific characteristics and use cases.
    """
    
    DRAFT = "Draft"
    """Draft content"""
    
    DOC_BLOCK = "DocBlock"
    """Document block - basic text content"""
    
    CODE_BLOCK = "CodeBlock"
    """Code block - programming code"""
    
    MESSAGE = "Message"
    """Message content"""
    
    SECTION = "Section"
    """Section content"""
    
    OTHER = "Other"
    """Other content type"""
    
    @classmethod
    def get_default(cls) -> "ChunkType":
        """Get default chunk type."""
        return cls.DOC_BLOCK
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid chunk type."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class LanguageEnum(str, Enum):
    """
    Enumeration of supported languages.
    
    Defines the languages supported by the Vector Store for content
    processing and search operations.
    """
    
    UNKNOWN = "UNKNOWN"
    """Unknown or unspecified language"""
    
    EN = "en"
    """English"""
    
    RU = "ru"
    """Russian"""
    
    DE = "de"
    """German"""
    
    FR = "fr"
    """French"""
    
    ES = "es"
    """Spanish"""
    
    ZH = "zh"
    """Chinese"""
    
    JA = "ja"
    """Japanese"""
    
    MARKDOWN = "markdown"
    """Markdown content"""
    
    PYTHON = "python"
    """Python code"""
    
    @classmethod
    def get_default(cls) -> "LanguageEnum":
        """Get default language."""
        return cls.EN
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid language."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class ChunkRole(str, Enum):
    """
    Enumeration of chunk roles in the system.
    
    Defines the different roles that chunks can have in the system,
    indicating their purpose and usage context.
    """
    
    SYSTEM = "system"
    """System-generated content"""
    
    USER = "user"
    """User-generated content"""
    
    ASSISTANT = "assistant"
    """Assistant-generated content"""
    
    TOOL = "tool"
    """Tool-generated content"""
    
    REVIEWER = "reviewer"
    """Reviewer-generated content"""
    
    DEVELOPER = "developer"
    """Developer-generated content"""
    
    @classmethod
    def get_default(cls) -> "ChunkRole":
        """Get default chunk role."""
        return cls.USER
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid chunk role."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class ChunkStatus(str, Enum):
    """
    Enumeration of chunk statuses.
    
    Defines the possible states of a chunk in the Vector Store,
    indicating its processing and availability status.
    """
    
    NEW = "NEW"
    """New chunk"""
    
    RAW = "RAW"
    """Raw unprocessed chunk"""
    
    CLEANED = "CLEANED"
    """Cleaned chunk"""
    
    VERIFIED = "VERIFIED"
    """Verified chunk"""
    
    VALIDATED = "VALIDATED"
    """Validated chunk"""
    
    RELIABLE = "RELIABLE"
    """Reliable chunk"""
    
    INDEXED = "INDEXED"
    """Indexed chunk"""
    
    OBSOLETE = "OBSOLETE"
    """Obsolete chunk"""
    
    REJECTED = "REJECTED"
    """Rejected chunk"""
    
    IN_PROGRESS = "IN_PROGRESS"
    """Chunk being processed"""
    
    NEEDS_REVIEW = "NEEDS_REVIEW"
    """Chunk needs review"""
    
    ARCHIVED = "ARCHIVED"
    """Archived chunk"""
    
    @classmethod
    def get_default(cls) -> "ChunkStatus":
        """Get default chunk status."""
        return cls.NEW
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid chunk status."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class BlockType(str, Enum):
    """
    Enumeration of block types.
    
    Defines the different types of content blocks that can be stored
    in the Vector Store.
    """
    
    PARAGRAPH = "paragraph"
    """Paragraph block"""
    
    MESSAGE = "message"
    """Message block"""
    
    SECTION = "section"
    """Section block"""
    
    OTHER = "other"
    """Other block type"""
    
    @classmethod
    def get_default(cls) -> "BlockType":
        """Get default block type."""
        return cls.PARAGRAPH
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid block type."""
        try:
            cls(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all valid block type values."""
        return [member.value for member in cls]


class SearchOrder(str, Enum):
    """
    Enumeration of search result ordering options.
    
    Defines how search results should be ordered when returned
    from the Vector Store.
    """
    
    RELEVANCE = "relevance"
    """Order by relevance score (default)"""
    
    DATE_CREATED = "date_created"
    """Order by creation date"""
    
    DATE_UPDATED = "date_updated"
    """Order by last update date"""
    
    UUID = "uuid"
    """Order by UUID"""
    
    TYPE = "type"
    """Order by chunk type"""
    
    LANGUAGE = "language"
    """Order by language"""
    
    @classmethod
    def get_default(cls) -> "SearchOrder":
        """Get default search order."""
        return cls.RELEVANCE
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid search order."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class EmbeddingModel(str, Enum):
    """
    Enumeration of supported embedding models.
    
    Defines the embedding models that can be used for vector generation
    in the Vector Store.
    """
    
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    """OpenAI Ada-002 model (1536 dimensions)"""
    
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    """OpenAI 3-Small model (1536 dimensions)"""
    
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    """OpenAI 3-Large model (3072 dimensions)"""
    
    ALL_MINILM_L6_V2 = "all-MiniLM-L6-v2"
    """Sentence Transformers MiniLM (384 dimensions)"""
    
    ALL_MPNET_BASE_V2 = "all-mpnet-base-v2"
    """Sentence Transformers MPNet (768 dimensions)"""
    
    CUSTOM_384 = "custom_384"
    """Custom 384-dimensional model"""
    
    CUSTOM_768 = "custom_768"
    """Custom 768-dimensional model"""
    
    CUSTOM_1536 = "custom_1536"
    """Custom 1536-dimensional model"""
    
    @classmethod
    def get_default(cls) -> "EmbeddingModel":
        """Get default embedding model."""
        return cls.ALL_MINILM_L6_V2
    
    @classmethod
    def get_dimensions(cls, model: "EmbeddingModel") -> int:
        """Get embedding dimensions for a model."""
        dimensions_map = {
            cls.TEXT_EMBEDDING_ADA_002: 1536,
            cls.TEXT_EMBEDDING_3_SMALL: 1536,
            cls.TEXT_EMBEDDING_3_LARGE: 3072,
            cls.ALL_MINILM_L6_V2: 384,
            cls.ALL_MPNET_BASE_V2: 768,
            cls.CUSTOM_384: 384,
            cls.CUSTOM_768: 768,
            cls.CUSTOM_1536: 1536,
        }
        return dimensions_map.get(model, 384)
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is a valid embedding model."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


# Validation constants
MIN_CHUNK_SIZE = 1
MAX_CHUNK_SIZE = 10000
MIN_SEARCH_LIMIT = 1
MAX_SEARCH_LIMIT = 1000
MIN_RELEVANCE_THRESHOLD = 0.0
MAX_RELEVANCE_THRESHOLD = 1.0
MIN_OFFSET = 0
MAX_OFFSET = 10000
MIN_TIMEOUT = 1.0
MAX_TIMEOUT = 300.0
EMBEDDING_DIMENSION = 384
UUID_LENGTH = 36
SHA256_LENGTH = 64

# Default values
DEFAULT_TIMEOUT = 30.0
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0
DEFAULT_RELEVANCE_THRESHOLD = 0.0
DEFAULT_CHUNK_TYPE = "DocBlock"
DEFAULT_LANGUAGE = "en"
DEFAULT_STATUS = "new"
DEFAULT_SEARCH_ORDER = SearchOrder.RELEVANCE
DEFAULT_EMBEDDING_MODEL = EmbeddingModel.ALL_MINILM_L6_V2

# JSON-RPC constants
JSON_RPC_VERSION = "2.0"
DEFAULT_JSON_RPC_ID = 1

# HTTP constants
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Retry constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_BACKOFF_FACTOR = 2.0

# Batch processing constants
DEFAULT_BATCH_SIZE = 100
MAX_BATCH_SIZE = 1000
DEFAULT_CONCURRENT_REQUESTS = 5
MAX_CONCURRENT_REQUESTS = 20

# Logging constants
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cache constants
DEFAULT_CACHE_TTL = 300  # 5 minutes
MAX_CACHE_TTL = 3600     # 1 hour
DEFAULT_CACHE_SIZE = 1000
MAX_CACHE_SIZE = 10000 