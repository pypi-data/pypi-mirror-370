# Installation

This guide covers different ways to install and set up Obsidian-AI.

## Prerequisites

- Python 3.12 or higher
- OpenAI API key
- A directory containing your notes (markdown, text, etc.)

## Installation Methods

### Option 1: Install from PyPI (Recommended)

```bash
pip install obsidian-ai
```

### Option 2: Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/sumukshashidhar/obsidian-ai.git
cd obsidian-ai

# Install with uv (recommended)
uv sync
source .venv/bin/activate

# Or install with pip
pip install -e .
```

### Option 3: Using pipx (Isolated Installation)

```bash
pipx install obsidian-ai
```

## Environment Setup

### Required Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

!!! warning "API Key Security"
    Never commit your API key to version control. Use environment variables or a secure credential manager.

### Optional Configuration

Configure your brain directory (defaults to `~/brain`):

```bash
export OBSIDIAN_AI_BRAIN_DIR="$HOME/Documents/MyNotes"
```

Choose your preferred OpenAI model:

```bash
export OBSIDIAN_AI_MODEL="gpt-4o"  # or gpt-3.5-turbo, gpt-4, etc.
```

Set ignore patterns for files you want to exclude:

```bash
export OBSIDIAN_AI_IGNORE_PATTERNS="*.tmp,cache/*,private/*"
```

## Verification

Test your installation:

```bash
# Check version
obsidian-ai --version

# Test basic functionality
obsidian-ai search "test"
```

## Shell Integration

### Bash/Zsh

Add to your `.bashrc` or `.zshrc`:

```bash
# Obsidian-AI configuration
export OPENAI_API_KEY="your-api-key"
export OBSIDIAN_AI_BRAIN_DIR="$HOME/brain"

# Convenient aliases
alias ai-chat="obsidian-ai chat"
alias ai-search="obsidian-ai search"
alias ai-repl="obsidian-ai repl"
```

### Fish Shell

Add to your `config.fish`:

```fish
# Obsidian-AI configuration
set -x OPENAI_API_KEY "your-api-key"
set -x OBSIDIAN_AI_BRAIN_DIR "$HOME/brain"

# Convenient aliases
alias ai-chat="obsidian-ai chat"
alias ai-search="obsidian-ai search"
alias ai-repl="obsidian-ai repl"
```

## Docker Installation

Run Obsidian-AI in a container:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install obsidian-ai

# Mount your brain directory
VOLUME ["/brain"]

ENV OBSIDIAN_AI_BRAIN_DIR="/brain"
ENTRYPOINT ["obsidian-ai"]
```

```bash
# Build and run
docker build -t obsidian-ai .
docker run -it \
  -e OPENAI_API_KEY="your-key" \
  -v "$HOME/brain:/brain" \
  obsidian-ai chat "What notes do I have?"
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'obsidian_ai'**
- Ensure you're using the correct Python environment
- Try reinstalling: `pip uninstall obsidian-ai && pip install obsidian-ai`

**OpenAI API Error**
- Verify your API key is set correctly
- Check your OpenAI account has sufficient credits
- Ensure the model you specified is available

**Permission Denied**
- Check that the brain directory exists and is readable
- Verify file permissions on your notes directory

**No Files Found**
- Ensure your brain directory contains supported file types (.md, .txt, .org, .rst)
- Check that files aren't being excluded by ignore patterns

### Getting Help

If you encounter issues:

1. Check the [configuration guide](configuration.md)
2. Review [common usage patterns](examples.md)
3. Search existing [GitHub issues](https://github.com/sumukshashidhar/obsidian-ai/issues)
4. Create a new issue with details about your setup

## Next Steps

- [Configure Obsidian-AI](configuration.md) for your workflow
- Explore [usage examples](examples.md)
- Learn about [advanced features](../api/core.md)