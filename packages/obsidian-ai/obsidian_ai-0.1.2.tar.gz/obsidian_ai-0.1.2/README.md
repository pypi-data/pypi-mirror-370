# Obsidian-AI

A command-line AI assistant that chats with your personal knowledge base using OpenAI's GPT models. Search, read, and semantically explore your notes with natural language queries.

## Features

- **Smart Search**: Keyword and semantic search across your note collection
- **Safe File Access**: Read-only operations with directory sandboxing
- **Interactive Chat**: Both single-query and REPL modes
- **Local Embeddings**: TF-IDF based semantic search with local caching
- **Rich Output**: Beautiful terminal UI with syntax highlighting

## Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd obsidian-ai
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Configuration

```bash
export OPENAI_API_KEY="your-api-key-here"
export OBSIDIAN_AI_BRAIN_DIR="$HOME/brain"              # Optional: defaults to ~/brain
export OBSIDIAN_AI_MODEL="gpt-4o"                       # Optional: defaults to gpt-4o
export OBSIDIAN_AI_IGNORE_PATTERNS="*.tmp,cache/*,30. Areas/Roleplay"  # Optional: comma-separated ignore patterns
```

### Usage

```bash
# Single question
obsidian-ai chat "What notes do I have about machine learning?"

# Interactive chat
obsidian-ai repl

# Direct search
obsidian-ai search "project ideas"

# Read specific file
obsidian-ai read "projects/ai-assistant.md"

# Ignore specific patterns for this session
obsidian-ai --ignore "temp/*" --ignore "*.draft" chat "What are my project ideas?"
```

## How It Works

Obsidian-AI provides your chosen GPT model with three powerful tools to explore your notes:

1. **`search(query)`** - Keyword search across filenames and content
2. **`read_file(path)`** - Safe file reading with byte-range support  
3. **`semantic_search(query)`** - Similarity search using local TF-IDF embeddings

The assistant uses these tools to ground its responses in your actual notes, providing specific file citations and relevant excerpts.

## Architecture

```
src/obsidian_ai/
├── cli.py          # Command-line interface
├── chat.py         # OpenAI chat integration with tool calling
├── config.py       # Environment configuration
├── tools.py        # Tool definitions and dispatch
├── search.py       # Keyword search implementation
├── semsearch.py    # Semantic search with local embeddings
├── local_embed.py  # TF-IDF vectorizer implementation
└── fs.py          # File system utilities
```

## Supported File Types

- Markdown (`.md`)
- Text files (`.txt`)
- Org-mode (`.org`) 
- reStructuredText (`.rst`)
- Code files (`.py`, `.js`, `.ts`, `.java`, `.go`)
- Data files (`.csv`, `.json`, `.yaml`, `.yml`)

## Safety & Security

- **Read-only**: No file modification capabilities
- **Directory sandboxing**: File access restricted to configured brain directory
- **No secrets in code**: API keys only via environment variables
- **Size limits**: Files over 2MB are skipped to prevent abuse

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `OBSIDIAN_AI_BRAIN_DIR` | `~/brain` | Directory containing your notes |
| `OBSIDIAN_AI_MODEL` | `gpt-4o` | OpenAI model to use |
| `OBSIDIAN_AI_MAX_TOOL_CALLS` | `5` | Maximum tool calls per query |
| `OBSIDIAN_AI_IGNORE_PATTERNS` | Built-in defaults | Comma-separated patterns to ignore |
| `OPENAI_API_KEY` | *required* | Your OpenAI API key |

## Advanced Usage

### Ignore Patterns

Control which directories and files are excluded from search:

```bash
# Environment variable (persistent)
export OBSIDIAN_AI_IGNORE_PATTERNS="30. Areas/Roleplay,temp/*,*.draft,private/*"

# Command-line flags (session-only)
obsidian-ai --ignore "temp/*" --ignore "*.draft" search "project ideas"
obsidian-ai --ignore "30. Areas/Roleplay" chat "Tell me about my notes"
```

**Built-in ignore patterns:**
- `.git`, `.obsidian`, `.obsidian_ai_cache`
- `node_modules`, `__pycache__`
- `.DS_Store`, `Thumbs.db`

**Pattern matching:**
- `*` matches any characters: `temp/*` ignores anything in temp directories
- `*.ext` matches files with specific extensions
- `dirname` matches exact directory names anywhere in the path
- `path/to/dir` matches specific paths relative to brain directory

### Semantic Search Caching

The semantic search builds a local TF-IDF index cached in `.obsidian_ai_cache/`. The index automatically rebuilds when files change.

### File Reading with Ranges

```bash
# Read first 1KB of a large file
obsidian-ai read "large-document.md" --start 0 --max-bytes 1024

# Read from specific byte offset
obsidian-ai read "large-document.md" --start 1024 --max-bytes 2048
```

### Verbose Logging

```bash
# Enable debug logging
obsidian-ai -v chat "your question"
obsidian-ai -vv repl  # Even more verbose
```

## Development

### Testing

```bash
# Run tests
uv run pytest tests/

# Run specific test
uv run pytest tests/test_search.py -v
```

### Project Structure

The codebase follows bacterial coding principles - small, modular, self-contained functions that could easily be copied and reused. Each module has a single clear purpose:

- `fs.py` - File system iteration
- `search.py` - Text search logic
- `local_embed.py` - Embedding vectorization
- `semsearch.py` - Semantic search coordination
- `tools.py` - OpenAI tool integration
- `chat.py` - Conversation management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Created by [Sumuk Shashidhar](mailto:sumukuuu@gmail.com)