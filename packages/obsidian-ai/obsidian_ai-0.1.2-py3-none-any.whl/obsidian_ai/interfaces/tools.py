from __future__ import annotations

import json
from typing import Any

from ..core.search_engine import search_engine
from ..core.research_agent import research_agent
from ..infrastructure.file_system import read_file_safe
from ..services.embedding_service import embedding_service


def search_tool(query: str, max_results: int | None = None) -> str:
    """Enhanced multi-strategy keyword search across notes."""
    return search_engine.search_json(query, max_results or 10)


def semantic_search_tool(query: str, k: int | None = None) -> str:
    """Semantic similarity search using embeddings."""
    return embedding_service.semantic_search_json(query, k or 10)


def deep_research_tool(topic: str, max_iterations: int | None = None) -> str:
    """Comprehensive research with wikilink following and iterative discovery."""
    result = research_agent.conduct_research(topic, max_iterations or 4)
    return json.dumps(result, indent=2)


def read_file_tool(path: str, start: int | None = None, max_bytes: int | None = None) -> str:
    """Read file content with optional byte range."""
    try:
        content = read_file_safe(path, start or 0, max_bytes or 32768)
        return json.dumps({"path": path, "content": content, "start": start or 0, "bytes": len(content.encode())})
    except Exception as e:
        return json.dumps({"error": str(e)})


def dispatch_tool(name: str, args: dict[str, Any]) -> str:
    """Dispatch tool calls to appropriate handlers."""
    match name:
        case "search":
            return search_tool(args["query"], args.get("max_results"))
        case "semantic_search":
            return semantic_search_tool(args["query"], args.get("k"))
        case "deep_research":
            return deep_research_tool(args["topic"], args.get("max_iterations"))
        case "read_file":
            return read_file_tool(args["path"], args.get("start"), args.get("max_bytes"))
        case _:
            return json.dumps({"error": f"Unknown tool: {name}"})


# OpenAI function definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Enhanced multi-strategy search: exact phrases, keywords, filename matching",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query - can be phrases, keywords, or names"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "semantic_search",
            "description": "Semantic similarity search using embeddings for conceptual matches",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Conceptual search query"},
                    "k": {"type": "integer", "description": "Number of results", "default": 10},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deep_research",
            "description": "Comprehensive research that follows wikilinks, discovers connections, and builds understanding iteratively",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic or complex question"},
                    "max_iterations": {"type": "integer", "description": "Max research iterations", "default": 4},
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "start": {"type": "integer", "description": "Start byte", "default": 0},
                    "max_bytes": {"type": "integer", "description": "Max bytes to read", "default": 32768},
                },
                "required": ["path"],
            },
        },
    },
]
