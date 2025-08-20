from __future__ import annotations

import json
from typing import Any

from ..semsearch import semantic_search as _semantic_search


class EmbeddingService:
    """Service for semantic search using local embeddings."""

    def __init__(self) -> None:
        pass

    def semantic_search(self, query: str, k: int = 10) -> dict[str, Any]:
        """Perform semantic search and return structured results."""
        try:
            result_json = _semantic_search(query, k)
            return json.loads(result_json)  # type: ignore[no-any-return]
        except Exception as e:
            return {"query": query, "results": [], "error": str(e)}

    def semantic_search_json(self, query: str, k: int = 10) -> str:
        """Perform semantic search and return JSON string."""
        result = self.semantic_search(query, k)
        return json.dumps(result)


# Global embedding service instance
embedding_service = EmbeddingService()
