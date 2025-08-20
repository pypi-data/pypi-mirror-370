# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with 80+ tests and 41% coverage
- MkDocs documentation with user guides and API reference
- GitHub Actions CI/CD workflows for testing, building, and deployment
- Ruff and MyPy configuration for code quality
- Developer tools and configurations

### Changed
- Improved test infrastructure with synthetic test data
- Enhanced OpenAI client with lazy initialization to prevent import errors
- Better error handling across components

### Fixed
- OpenAI client import issues during testing
- Test compatibility with different file systems
- Various test assertion issues

## [0.1.1] - 2025-01-19

### Added
- Initial release with core functionality
- Command-line interface for chat, search, and file reading
- Semantic search using TF-IDF embeddings
- Wikilink parsing and analysis
- OpenAI integration for chat capabilities
- File system utilities with safety checks
- Configuration management via environment variables

### Features
- Smart search with keyword, phrase, and semantic options
- Interactive REPL mode for extended conversations
- Safe file access with directory sandboxing
- Local caching for improved performance
- Rich terminal output with syntax highlighting
- Support for multiple file formats (.md, .txt, .org, .rst, etc.)

### Security
- Read-only operations to protect user data
- API key management via environment variables
- Directory traversal protection
- File size limits to prevent abuse