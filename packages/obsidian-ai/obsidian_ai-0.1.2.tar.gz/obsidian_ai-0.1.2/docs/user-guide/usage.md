# Usage Guide

This guide covers the basic usage of Obsidian-AI.

## Command Line Interface

### Basic Search

Search your knowledge base using semantic search:

```bash
obsidian-ai search "machine learning algorithms"
```

### Interactive Chat

Start an interactive chat session:

```bash
obsidian-ai chat
```

### Research Mode

Generate research reports on specific topics:

```bash
obsidian-ai research "deep learning trends"
```

## Python API

### Basic Usage

```python
from obsidian_ai import search_engine, embedding_service

# Search your knowledge base
results = search_engine.search("neural networks", max_results=5)

# Semantic search
semantic_results = embedding_service.semantic_search("AI research", k=10)
```

### Configuration

```python
from obsidian_ai.infrastructure.config import config

# Access configuration
print(f"Brain directory: {config.brain_dir}")
print(f"Model: {config.model}")
```

## Features

### WikiLink Support

Obsidian-AI fully supports WikiLinks in your markdown files:

- `[[Simple Link]]`
- `[[Link|Display Text]]`
- `[[Link with [nested] brackets]]`

### File System Integration

- Automatic file discovery
- Respect for .gitignore patterns
- Safe file operations with security checks

### AI-Powered Features

- Semantic search using local embeddings
- Context-aware responses
- Research report generation
- Multi-step reasoning

## Best Practices

1. **Organization**: Keep your notes well-organized with clear titles
2. **Linking**: Use WikiLinks to connect related concepts
3. **Tagging**: Use consistent tagging for better search results
4. **Regular Updates**: Keep your knowledge base current

## Troubleshooting

### Common Issues

**Q: Search returns no results**
A: Check that your brain directory is correctly configured and contains markdown files.

**Q: OpenAI API errors**
A: Ensure your `OPENAI_API_KEY` environment variable is set.

**Q: Slow performance**
A: Consider adjusting the `max_tool_calls` configuration parameter.

For more help, see our [troubleshooting guide](../developer/testing.md) or [contribute](../developer/contributing.md) to the project.