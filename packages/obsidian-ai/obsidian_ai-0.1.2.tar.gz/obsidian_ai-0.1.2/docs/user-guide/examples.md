# Usage Examples

This guide demonstrates common usage patterns and workflows with Obsidian-AI.

## Basic Operations

### Single Queries

Quick one-off questions about your notes:

```bash
# Find notes about a topic
obsidian-ai chat "What notes do I have about machine learning?"

# Get summaries
obsidian-ai chat "Summarize my thoughts on project management"

# Find connections
obsidian-ai chat "How do my notes on AI relate to my business ideas?"
```

### Search Operations

Direct search without AI interpretation:

```bash
# Keyword search
obsidian-ai search "neural networks"

# Exact phrase search
obsidian-ai search "machine learning project"

# Filename search
obsidian-ai search "project"
```

### File Reading

Read specific files:

```bash
# Read entire file
obsidian-ai read "projects/ai-assistant.md"

# Read file range (useful for large files)
obsidian-ai read "research/paper-notes.md" --start 0 --max-bytes 1024

# Read with ignore patterns
obsidian-ai --ignore "drafts/*" read "projects/current.md"
```

## Interactive Sessions

### REPL Mode

Start an interactive conversation:

```bash
obsidian-ai repl
```

Example session:
```
> What projects am I working on?
Based on your notes, you're currently working on several projects:

1. **AI Assistant Project** - Building a command-line tool for note analysis
2. **Research Paper** - Writing about transformer architectures
3. **Data Pipeline** - Developing automated data processing

> Tell me more about the AI Assistant project
The AI Assistant project involves creating a tool that can search and analyze
your personal knowledge base. Key features include:
- Semantic search capabilities
- Wikilink analysis
- Interactive chat interface

> Who am I collaborating with on these projects?
From your notes, I can see you're collaborating with:
- John Smith on the AI research
- Sarah Wilson on data analysis
- Mike Chen on software development

> exit
```

## Advanced Workflows

### Research and Writing

Find related content while writing:

```bash
# Find background material
obsidian-ai chat "What background research do I have on transformers?"

# Get writing inspiration
obsidian-ai chat "What examples of machine learning applications are in my notes?"

# Check for contradictions
obsidian-ai chat "Do I have any conflicting opinions about deep learning approaches?"
```

### Project Management

Track project status and relationships:

```bash
# Project overview
obsidian-ai chat "What's the current status of my AI project?"

# Team coordination
obsidian-ai chat "What tasks have I assigned to team members?"

# Resource planning
obsidian-ai chat "What resources do I need for upcoming projects?"
```

### Personal Knowledge Management

Discover patterns and connections:

```bash
# Learning progress
obsidian-ai chat "What have I learned about Python this month?"

# Idea development
obsidian-ai chat "How have my thoughts on AI ethics evolved?"

# Memory aids
obsidian-ai chat "What did I think about that conference last year?"
```

## Specialized Use Cases

### Academic Research

```bash
# Literature review
obsidian-ai chat "Summarize the key papers I've read on neural networks"

# Thesis writing
obsidian-ai chat "What evidence do I have to support my hypothesis about..."

# Citation finding
obsidian-ai chat "Which papers discuss transformer attention mechanisms?"
```

### Business Planning

```bash
# Market analysis
obsidian-ai chat "What market research have I collected on AI tools?"

# Competitive analysis
obsidian-ai chat "How do competitors compare in my analysis?"

# Strategy development
obsidian-ai chat "What strategic options have I considered?"
```

### Creative Writing

```bash
# Character development
obsidian-ai chat "What characters have I created for my story?"

# Plot consistency
obsidian-ai chat "Are there any plot holes in my story outline?"

# World building
obsidian-ai chat "What details have I established about my fictional world?"
```

## Command-Line Patterns

### Batch Operations

Process multiple queries:

```bash
# Create a script for daily review
#!/bin/bash
echo "=== Today's Tasks ==="
obsidian-ai chat "What tasks do I have for today?"

echo "=== Recent Progress ==="
obsidian-ai chat "What progress have I made this week?"

echo "=== Upcoming Deadlines ==="
obsidian-ai chat "What deadlines are coming up?"
```

### Filtered Searches

Use ignore patterns for focused results:

```bash
# Work-only search
obsidian-ai --ignore "personal/*" --ignore "diary/*" chat "What work projects need attention?"

# Recent notes only
obsidian-ai --ignore "archive/*" --ignore "old/*" search "machine learning"

# Exclude drafts
obsidian-ai --ignore "*.draft" --ignore "wip/*" chat "What completed research do I have?"
```

### Integration with Other Tools

Pipe results to other commands:

```bash
# Save search results
obsidian-ai search "project ideas" > ideas.txt

# Count results
obsidian-ai search "meeting" | wc -l

# Format for other tools
obsidian-ai chat "List my project names" | grep "^-" | sort
```

## Output Formatting

### Verbose Output

Get detailed information about operations:

```bash
# See search process
obsidian-ai -v search "machine learning"

# Debug mode
obsidian-ai -vv chat "What's in my notes?"
```

### JSON Output

For programmatic processing:

```bash
# Get structured search results
obsidian-ai search --format json "neural networks"

# Parse with jq
obsidian-ai search --format json "AI" | jq '.results[].path'
```

## Performance Optimization

### Large Note Collections

For collections with thousands of files:

```bash
# Use specific ignore patterns
export OBSIDIAN_AI_IGNORE_PATTERNS="archive/*,old/*,*.tmp"

# Focus searches
obsidian-ai --ignore "archive/*" search "recent project"

# Use semantic search for better relevance
obsidian-ai chat "Find the most relevant notes about machine learning"
```

### Memory Management

For systems with limited memory:

```bash
# Process in smaller batches
obsidian-ai --ignore "large-files/*" search "topic"

# Clear cache if needed
rm -rf ~/.obsidian_ai_cache

# Use lighter models
export OBSIDIAN_AI_MODEL="gpt-3.5-turbo"
```

## Error Handling

### Common Scenarios

Handle missing files gracefully:

```bash
# Check if file exists before reading
if obsidian-ai search "filename.md" | grep -q "filename.md"; then
    obsidian-ai read "filename.md"
else
    echo "File not found"
fi
```

### Debugging

Troubleshoot issues:

```bash
# Check configuration
obsidian-ai chat "test" -v

# Verify brain directory
ls -la "$OBSIDIAN_AI_BRAIN_DIR"

# Test API connection
obsidian-ai chat "hello"
```

## Automation Examples

### Daily Workflows

```bash
#!/bin/bash
# daily-review.sh
DATE=$(date +%Y-%m-%d)

echo "=== Daily Review for $DATE ==="
obsidian-ai chat "What did I work on yesterday?"
obsidian-ai chat "What are my priorities for today?"
obsidian-ai chat "Any upcoming deadlines I should know about?"
```

### Weekly Reports

```bash
#!/bin/bash
# weekly-summary.sh
WEEK=$(date +%Y-W%U)

echo "=== Weekly Summary $WEEK ==="
obsidian-ai chat "What did I accomplish this week?"
obsidian-ai chat "What challenges did I encounter?"
obsidian-ai chat "What should I focus on next week?"
```

### Project Status

```bash
#!/bin/bash
# project-status.sh
PROJECT=$1

if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

echo "=== Status for $PROJECT ==="
obsidian-ai chat "What's the current status of $PROJECT?"
obsidian-ai chat "What are the next steps for $PROJECT?"
obsidian-ai chat "Any blockers or risks for $PROJECT?"
```

## Best Practices

### Effective Queries

Write clear, specific questions:

```bash
# Good: Specific and actionable
obsidian-ai chat "What Python libraries have I evaluated for data analysis?"

# Better: Include context
obsidian-ai chat "For my current data science project, what Python libraries have I researched and what are their pros and cons?"

# Best: Multiple related questions
obsidian-ai repl
> What Python libraries have I researched for data analysis?
> Which ones did I decide to use and why?
> What issues did I encounter with these libraries?
```

### Organizing Results

Structure your workflow:

1. **Explore** with broad questions
2. **Focus** with specific queries  
3. **Verify** by reading source files
4. **Document** insights in new notes

### Maintaining Context

Use REPL mode for related questions:

```bash
obsidian-ai repl
> Tell me about my AI project
> Who are the team members?
> What's our current progress?
> What are the main challenges?
> exit
```

This maintains context across the conversation, leading to more coherent and useful responses.

## Next Steps

- Learn about the [API reference](../api/core.md)
- Explore [development setup](../developer/contributing.md)
- Check the [architecture guide](../developer/architecture.md)