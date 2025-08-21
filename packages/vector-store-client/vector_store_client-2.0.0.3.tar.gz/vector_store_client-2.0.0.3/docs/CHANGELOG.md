# Changelog

All notable changes to the Vector Store Client project will be documented in this file.

## [2.0.0] - 2024-12-19

### Added
- Support for updated `embed_client>=2.0.0` package
- Support for updated `svo_client>=2.0.0` package
- New OpenAPI schema fetching functionality
- Updated models to match new server API schema
- Enhanced error handling for new package APIs

### Changed
- **BREAKING**: Updated `SemanticChunk` model structure:
  - Removed `source_id` as required field
  - Made `embedding` optional for creation
  - Updated field validation for new API format
  - Added support for new metadata fields: `category`, `title`, `tags`
- **BREAKING**: Updated `create_text_chunk` method signature:
  - Removed `source_id` parameter
  - Simplified parameter structure
- Updated embedding adapter to use new `embed_client` API methods
- Updated SVO adapter to use new `svo_client` API methods
- Updated chunk operations to match new server response format

### Fixed
- Fixed compatibility issues with new package versions
- Updated response parsing for new API format
- Fixed validation errors in updated models

### Dependencies
- Updated `embed_client` to `>=2.0.0`
- Updated `svo_client` to `>=2.0.0`
- Added `aiohttp>=3.8.0` for new client requirements

## [1.0.0] - 2024-12-18

### Added
- Initial release of Vector Store Client
- Support for chunk creation, search, and deletion
- Integration with embedding service
- Integration with SVO chunking service
- Comprehensive error handling and validation
- Async/await support throughout
- Type hints and documentation

### Features
- JSON-RPC 2.0 protocol support
- Automatic embedding generation
- Metadata filtering and search
- Health checks and monitoring
- Plugin and middleware systems
