# Obsidian-AI Examples

## Basic Usage

### Simple Question Answering

```bash
# Ask a direct question
obsidian-ai chat "When did Tara come to the US?"

# Search for specific topics
obsidian-ai chat "What's my research on AI safety?"

# Find information about people
obsidian-ai chat "Tell me about Steve Baker"
```

### Interactive Chat

```bash
# Start interactive session
obsidian-ai repl

# Example conversation:
You: when did tara first come to the us?
🔧 Calling search(query=Tara first came to the US)
   → {"query": "Tara first came to the US", "results": [...]}