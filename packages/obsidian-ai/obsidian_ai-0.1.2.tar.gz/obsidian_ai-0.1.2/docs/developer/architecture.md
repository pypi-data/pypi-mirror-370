# Architecture Overview

Obsidian-AI is designed with a modular, bacterial-inspired architecture that emphasizes small, composable, and easily transferable components.

## Core Principles

### Bacterial Code Philosophy

Our codebase follows bacterial coding principles:

- **Small modules**: Each component is self-contained and focused
- **Horizontal gene transfer**: Code can be easily "copy-pasted" between projects  
- **Energy efficiency**: Every line of code serves a purpose
- **Rapid adaptation**: Easy to modify and extend

### Design Patterns

- **Dependency injection** for loose coupling
- **Protocol-based interfaces** for flexibility
- **Functional programming** where appropriate
- **Immutable data structures** using dataclasses

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interfaces    │    │      Core       │    │  Infrastructure │
│                 │    │                 │    │                 │
│ • CLI           │────│ • Research      │────│ • Config        │
│ • Chat          │    │ • Search        │    │ • File System   │
│ • Tools         │    │ • WikiLinks     │    │ • Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Services     │
                    │                 │
                    │ • OpenAI        │
                    │ • Embeddings    │
                    │ • Search Engine │
                    └─────────────────┘
```

## Module Breakdown

### Core (`src/obsidian_ai/core/`)

Contains the main business logic:

#### Research Agent (`research_agent.py`)
- Multi-step reasoning engine
- Context synthesis and analysis
- Report generation

#### Search Engine (`search_engine.py`)
- Unified search interface
- Multiple search strategies:
  - Exact phrase matching
  - Keyword-based search
  - Filename search
- Result ranking and deduplication

#### WikiLink Parser (`wikilink_parser.py`)
- Parses WikiLink syntax `[[Link]]` and `[[Link|Display]]`
- Handles nested brackets
- Extracts key terms for search

### Infrastructure (`src/obsidian_ai/infrastructure/`)

Provides foundational services:

#### Configuration (`config.py`)
```python
@dataclass(frozen=True)
class Config:
    brain_dir: Path
    model: str
    max_tool_calls: int
    cache_dir: Path
    ignore_patterns: list[str]
```

#### File System (`file_system.py`)
- Safe file operations with security checks
- Text file discovery with ignore patterns
- Path resolution and validation

### Services (`src/obsidian_ai/services/`)

External service integrations:

#### OpenAI Client (`openai_client.py`)
- Lazy initialization to avoid import-time API calls
- Comprehensive error handling
- Multiple completion types (simple, structured, conversational)

#### Embedding Service (`embedding_service.py`) 
- Local embedding generation
- Semantic search capabilities
- Caching for performance

### Interfaces (`src/obsidian_ai/interfaces/`)

User-facing interfaces:

#### CLI (`cli.py`)
- Command-line interface using Typer
- Subcommands for different operations
- Rich formatting for output

#### Chat (`chat.py`)
- Interactive chat sessions
- Context management
- Tool integration

#### Tools (`tools.py`)
- Tool definitions for AI agent
- File operations and search functions

### Prompts (`src/obsidian_ai/prompts/`)

AI prompt management:

#### Base (`base.py`)
- Template management system
- Variable substitution
- Environment-based overrides

#### Chat & Research (`chat.py`, `research.py`)
- Specialized prompts for different use cases
- Configurable via environment variables

## Data Flow

### Search Request Flow

1. **User input** → CLI interface
2. **Query parsing** → Search engine
3. **Multiple strategies** → Exact phrase, keyword, filename search
4. **Result aggregation** → Deduplication and ranking  
5. **Response formatting** → JSON or text output

### Research Flow

1. **Topic analysis** → Extract key concepts
2. **Information gathering** → Search knowledge base
3. **Context synthesis** → Combine relevant information
4. **Report generation** → Structured output with sources

### Chat Flow

1. **Message processing** → Parse user input
2. **Context retrieval** → Search relevant knowledge
3. **Response generation** → AI completion with context
4. **Tool execution** → File operations if needed

## Security Considerations

### File System Security
- Path traversal prevention
- Sandbox to brain directory
- File existence validation

### API Security
- Safe API key handling
- Rate limiting considerations
- Error message sanitization

## Performance Characteristics

### Search Performance
- **File discovery**: O(n) where n = number of files
- **Text search**: O(m) where m = total content size
- **Result ranking**: O(k log k) where k = number of results

### Memory Usage
- **Lazy loading** of file contents
- **Streaming** for large files
- **Caching** for frequently accessed data

### Scalability
- Designed for personal knowledge bases (< 10k files)
- Can handle large individual files (up to 2MB default)
- Configurable limits for different use cases

## Extension Points

### Adding New Search Strategies
```python
class CustomSearch:
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        # Implementation here
        pass

# Add to UnifiedSearchEngine
engine.strategies.append(CustomSearch())
```

### Custom File Processors
```python
def custom_processor(path: Path) -> str:
    # Process file and return text content
    pass

# Register with file system
register_processor(".custom", custom_processor)
```

### New AI Models
```python
class CustomClient:
    def simple_completion(self, prompt: str) -> str:
        # Implementation for custom model
        pass
```

This architecture enables easy testing, maintenance, and extension while keeping the codebase modular and focused.