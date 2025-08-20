# Obsidian-AI

A command-line AI assistant that chats with your personal knowledge base using OpenAI's GPT models. Search, read, and semantically explore your notes with natural language queries.

## Overview

Obsidian-AI transforms your note collection into an intelligent knowledge base. Using advanced search capabilities and AI-powered analysis, it helps you:

- **Discover connections** between your notes and ideas
- **Search semantically** using natural language queries  
- **Explore relationships** through wikilink analysis
- **Chat interactively** with your knowledge base

## Key Features

### 🔍 Smart Search
- **Keyword search** across filenames and content
- **Semantic search** using local TF-IDF embeddings
- **Exact phrase matching** for precise queries
- **Wikilink analysis** to find connected notes

### 🛡️ Safe & Secure
- **Read-only operations** - never modifies your files
- **Directory sandboxing** restricts access to your brain directory
- **No secrets in code** - API keys only via environment variables
- **Size limits** prevent processing of overly large files

### 💬 Interactive Experience
- **Single queries** for quick answers
- **REPL mode** for extended conversations
- **Rich terminal output** with syntax highlighting
- **Tool integration** with search, read, and semantic analysis

### 🚀 High Performance
- **Local caching** of embeddings and search indices
- **Efficient file processing** with configurable limits
- **Concurrent operations** for faster responses
- **Smart ignore patterns** to skip irrelevant files

## Quick Start

1. **Install** Obsidian-AI:
   ```bash
   pip install obsidian-ai
   ```

2. **Configure** your environment:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export OBSIDIAN_AI_BRAIN_DIR="$HOME/brain"
   ```

3. **Start chatting** with your notes:
   ```bash
   obsidian-ai chat "What notes do I have about machine learning?"
   ```

## Use Cases

### Research & Writing
- Find related notes when working on papers or articles
- Discover connections between different research topics
- Get summaries of your thoughts on specific subjects

### Personal Knowledge Management
- Explore relationships between people, projects, and ideas
- Find forgotten notes related to current interests
- Maintain context across long-term projects

### Learning & Study
- Review notes on specific topics
- Find examples and explanations in your knowledge base
- Connect new learning to existing knowledge

## Architecture

Obsidian-AI follows bacterial coding principles - small, modular, self-contained components that work together:

```
src/obsidian_ai/
├── core/           # Search engines and analysis tools
├── infrastructure/ # Configuration and file system
├── services/       # External API integrations
├── interfaces/     # CLI and chat interfaces
└── prompts/        # AI prompt templates
```

Each module is designed to be:
- **Small** - focused on a single responsibility
- **Modular** - easily swappable components  
- **Self-contained** - minimal dependencies
- **Copy-pasteable** - reusable in other projects

## Next Steps

- [Installation Guide](user-guide/installation.md) - Detailed setup instructions
- [Configuration](user-guide/configuration.md) - Customize for your workflow
- [Usage Examples](user-guide/examples.md) - Common patterns and workflows
- [API Reference](api/core.md) - Detailed code documentation

Ready to explore your knowledge base? Let's get started!