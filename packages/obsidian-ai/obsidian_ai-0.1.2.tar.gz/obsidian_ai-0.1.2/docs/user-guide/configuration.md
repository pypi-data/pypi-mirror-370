# Configuration

Obsidian-AI is designed to work out of the box with minimal configuration. This guide covers all available configuration options.

## Environment Variables

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OBSIDIAN_AI_BRAIN_DIR` | `~/brain` | Directory containing your notes |
| `OBSIDIAN_AI_MODEL` | `gpt-4o` | OpenAI model to use |
| `OBSIDIAN_AI_MAX_TOOL_CALLS` | `5` | Maximum tool calls per query |
| `OBSIDIAN_AI_IGNORE_PATTERNS` | See below | Comma-separated patterns to ignore |

## Brain Directory Setup

Your brain directory should contain your notes in supported formats:

```
brain/
├── projects/
│   ├── project-alpha.md
│   └── project-beta.md
├── people/
│   ├── john-smith.md
│   └── sarah-wilson.md
├── daily/
│   ├── 2024-01-15.md
│   └── 2024-01-16.md
└── concepts/
    ├── machine-learning.md
    └── deep-learning.md
```

### Supported File Types

- **Markdown**: `.md`
- **Text**: `.txt`
- **Org-mode**: `.org`
- **reStructuredText**: `.rst`
- **Code files**: `.py`, `.js`, `.ts`, `.java`, `.go`
- **Data files**: `.csv`, `.json`, `.yaml`, `.yml`

## Ignore Patterns

Control which files and directories are excluded from processing.

### Default Ignore Patterns

These patterns are always ignored:

- `.git` - Git repositories
- `.obsidian` - Obsidian app files
- `.obsidian_ai_cache` - Cache directory
- `node_modules` - Node.js dependencies
- `__pycache__` - Python cache
- `.DS_Store` - macOS metadata
- `Thumbs.db` - Windows metadata

### Custom Ignore Patterns

Add your own patterns via environment variable:

```bash
export OBSIDIAN_AI_IGNORE_PATTERNS="temp/*,*.draft,private/*,30. Areas/Roleplay"
```

Or use command-line flags for session-specific ignoring:

```bash
obsidian-ai --ignore "temp/*" --ignore "*.draft" search "project ideas"
```

### Pattern Syntax

- `*` matches any characters: `temp/*` ignores anything in temp directories
- `*.ext` matches files with specific extensions
- `dirname` matches exact directory names anywhere in the path
- `path/to/dir` matches specific paths relative to brain directory

### Examples

```bash
# Ignore temporary files
export OBSIDIAN_AI_IGNORE_PATTERNS="*.tmp,*.temp"

# Ignore specific directories
export OBSIDIAN_AI_IGNORE_PATTERNS="archive/*,old-notes/*"

# Ignore private content
export OBSIDIAN_AI_IGNORE_PATTERNS="private/*,personal/*,diary/*"

# Complex patterns
export OBSIDIAN_AI_IGNORE_PATTERNS="*.draft,temp/*,archive/*,30. Areas/Roleplay"
```

## Model Selection

Choose the OpenAI model that best fits your needs:

### Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `gpt-4o` | Latest GPT-4 (default) | Complex reasoning, analysis |
| `gpt-4` | Standard GPT-4 | High-quality responses |
| `gpt-3.5-turbo` | Faster, less expensive | Quick queries, simple tasks |

### Configuration

```bash
# High quality (default)
export OBSIDIAN_AI_MODEL="gpt-4o"

# Fast and economical
export OBSIDIAN_AI_MODEL="gpt-3.5-turbo"

# Standard GPT-4
export OBSIDIAN_AI_MODEL="gpt-4"
```

## Performance Tuning

### File Size Limits

Large files are automatically skipped to prevent performance issues:

- Default limit: 2MB per file
- Files exceeding the limit are ignored
- This prevents processing of large binary files or exports

### Cache Configuration

Obsidian-AI caches embeddings and search indices for better performance:

```
.obsidian_ai_cache/
├── embeddings/     # TF-IDF vectors
├── search_index/   # Search indices
└── metadata/       # File modification times
```

The cache automatically rebuilds when files change.

### Memory Usage

For large note collections:

- TF-IDF embeddings are memory-efficient
- Search indices are built incrementally
- Only modified files are reprocessed

## Security Settings

### API Key Management

Best practices for API key security:

```bash
# Use a secure credential manager
export OPENAI_API_KEY=$(security find-generic-password -s openai -w)

# Or use a .env file (not committed to git)
echo "OPENAI_API_KEY=your-key" > .env
source .env
```

### Directory Sandboxing

Obsidian-AI restricts file access to your brain directory:

- Prevents reading files outside the configured directory
- Blocks directory traversal attacks
- All file paths are validated and resolved safely

## Advanced Configuration

### Custom Prompts

While not exposed via environment variables, you can modify prompts by:

1. Forking the repository
2. Editing files in `src/obsidian_ai/prompts/`
3. Installing your custom version

### Integration Scripts

Create wrapper scripts for common workflows:

```bash
#!/bin/bash
# ai-daily.sh - Find today's notes and related content

DATE=$(date +%Y-%m-%d)
obsidian-ai chat "Show me notes from $DATE and anything related to today's work"
```

```bash
#!/bin/bash
# ai-project.sh - Project-specific queries

PROJECT=${1:-"default"}
obsidian-ai --ignore "personal/*" chat "What do I know about project $PROJECT?"
```

## Configuration Examples

### Research Setup

For academic or research notes:

```bash
export OBSIDIAN_AI_BRAIN_DIR="$HOME/Research"
export OBSIDIAN_AI_MODEL="gpt-4o"
export OBSIDIAN_AI_IGNORE_PATTERNS="drafts/*,archive/*,*.bib"
```

### Personal Knowledge Base

For personal notes and journals:

```bash
export OBSIDIAN_AI_BRAIN_DIR="$HOME/Documents/Notes"
export OBSIDIAN_AI_MODEL="gpt-3.5-turbo"
export OBSIDIAN_AI_IGNORE_PATTERNS="private/*,diary/*"
```

### Team Documentation

For shared team knowledge:

```bash
export OBSIDIAN_AI_BRAIN_DIR="/shared/team-docs"
export OBSIDIAN_AI_MODEL="gpt-4"
export OBSIDIAN_AI_IGNORE_PATTERNS="wip/*,personal/*"
```

## Troubleshooting Configuration

### Common Issues

**Configuration not applied**
- Restart your terminal after setting environment variables
- Check that variables are exported: `echo $OBSIDIAN_AI_BRAIN_DIR`

**Files not found**
- Verify the brain directory path is correct
- Check file permissions are readable
- Ensure files have supported extensions

**API errors**
- Validate your API key format
- Check OpenAI account status and credits
- Verify the model name is correct

### Debugging Configuration

View current configuration:

```bash
# Check environment variables
env | grep OBSIDIAN_AI

# Test with verbose output
obsidian-ai -v search "test"

# Verify brain directory contents
obsidian-ai search "*" | head -20
```

## Next Steps

- Learn [common usage patterns](examples.md)
- Explore the [API reference](../api/core.md)
- Set up [development environment](../developer/contributing.md)