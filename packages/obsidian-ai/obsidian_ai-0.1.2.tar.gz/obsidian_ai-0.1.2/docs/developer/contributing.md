# Contributing to Obsidian-AI

We welcome contributions to Obsidian-AI! This guide will help you get started.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sumukshashidhar/obsidian-ai.git
   cd obsidian-ai
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

### Code Style

We follow bacterial coding principles:

- **Small functions** (20 lines max)
- **Single responsibility** per function
- **Self-documenting code** with verbose variable names
- **Early returns** and exception bubbling

### Code Standards

- Use **Python 3.12+ features** aggressively
- **Type annotations** everywhere
- **Dataclasses** for data structures
- **Modern Python** syntax (walrus operator, union types, etc.)

### Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/obsidian_ai --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_core.py -v
```

### Linting and Formatting

```bash
# Check linting
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
```

## Contribution Guidelines

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes
4. **Add tests** for new functionality
5. **Run** the test suite and linting
6. **Submit** a pull request

### Commit Message Format

Use conventional commit format:

```
feat: add semantic search functionality
fix: resolve wikilink parsing edge case
docs: update installation instructions
test: add integration tests for search engine
```

### Code Review Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)

## Areas for Contribution

### High Priority

- **Performance optimization** for large knowledge bases
- **Additional file format support** (org-mode, rst, etc.)
- **Enhanced AI reasoning** capabilities
- **Better error handling** and user feedback

### Medium Priority

- **GUI interface** development
- **Plugin system** for extensibility
- **Cloud sync** capabilities
- **Mobile app** companion

### Low Priority

- **Additional language models** support
- **Custom embedding models**
- **Advanced visualization** features

## Development Tips

### Code Organization

```
src/obsidian_ai/
├── core/           # Core business logic
├── infrastructure/ # Configuration, file system
├── interfaces/     # CLI, API interfaces
├── services/       # External service integrations
└── prompts/        # AI prompt management
```

### Testing Philosophy

- **Unit tests** for individual functions
- **Integration tests** for component interactions
- **End-to-end tests** for complete workflows
- **Synthetic data** for reproducible tests

### Debugging

Use the built-in logging:

```python
from loguru import logger

logger.debug("Debug information")
logger.info("Important info")
logger.error("Error occurred")
```

## Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/sumukshashidhar/obsidian-ai/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/sumukshashidhar/obsidian-ai/discussions)
- **Documentation**: Check our [architecture guide](architecture.md) for technical details

Thank you for contributing to Obsidian-AI!