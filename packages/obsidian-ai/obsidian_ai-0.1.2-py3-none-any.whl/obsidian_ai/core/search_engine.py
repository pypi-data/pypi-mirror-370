from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..infrastructure.config import config
from ..infrastructure.file_system import iter_text_files


@dataclass(frozen=True)
class SearchResult:
    """A single search result."""

    path: str
    line: int
    text: str
    brain_dir: Path
    score: float = 1.0

    @property
    def relative_path(self) -> str:
        return str(Path(self.path).relative_to(self.brain_dir))


class SearchStrategy(Protocol):
    """Protocol for search strategies."""

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Execute the search strategy."""
        ...


class ExactPhraseSearch:
    """Search for exact phrases with case insensitive matching."""

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not query.strip():
            return []

        pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
        results: list[SearchResult] = []

        for path in iter_text_files(config.brain_dir, config.ignore_patterns):
            if len(results) >= max_results:
                break

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                lines = text.splitlines()

                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        # Get context around the match
                        context_lines = []
                        for i in range(max(0, line_num - 2), min(len(lines), line_num + 2)):
                            context_lines.append(lines[i].strip())
                        context = " | ".join(context_lines)

                        results.append(
                            SearchResult(
                                path=str(path),
                                line=line_num,
                                text=context[:300],
                                brain_dir=config.brain_dir,
                                score=2.0,  # Higher score for exact matches
                            )
                        )
                        break
            except Exception:
                continue

        return results


class KeywordSearch:
    """Search for individual keywords with scoring."""

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        keywords = [k.strip().lower() for k in query.split() if len(k.strip()) > 2]
        if not keywords:
            return []

        results: list[tuple[SearchResult, int]] = []  # (result, score)

        for path in iter_text_files(config.brain_dir, config.ignore_patterns):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                lines = text.splitlines()

                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    score = sum(1 for keyword in keywords if keyword in line_lower)

                    if score > 0:
                        results.append(
                            (SearchResult(path=str(path), line=line_num, text=line.strip()[:200], brain_dir=config.brain_dir, score=score), score)
                        )
            except Exception:
                continue

        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [result for result, _ in results[:max_results]]


class FilenameSearch:
    """Search filenames for partial matches."""

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        query_lower = query.lower()
        keywords = query_lower.split()
        results: list[SearchResult] = []

        for path in iter_text_files(config.brain_dir, config.ignore_patterns):
            filename_lower = path.name.lower()

            if any(keyword in filename_lower for keyword in keywords):
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    first_lines = "\n".join(text.splitlines()[:3])
                    results.append(
                        SearchResult(
                            path=str(path),
                            line=1,
                            text=f"📁 {path.name}: {first_lines[:150]}",
                            brain_dir=config.brain_dir,
                            score=1.5,  # Medium score for filename matches
                        )
                    )
                except Exception:
                    results.append(SearchResult(path=str(path), line=1, text=f"📁 {path.name}", brain_dir=config.brain_dir, score=1.0))

            if len(results) >= max_results:
                break

        return results


class UnifiedSearchEngine:
    """Unified search engine that combines multiple search strategies."""

    def __init__(self) -> None:
        self.strategies: list[SearchStrategy] = [ExactPhraseSearch(), KeywordSearch(), FilenameSearch()]

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Execute multi-strategy search and combine results."""
        all_results: list[SearchResult] = []
        seen_lines: set[str] = set()

        # Execute each strategy
        for strategy in self.strategies:
            strategy_results = strategy.search(query, max_results // 2)

            for result in strategy_results:
                key = f"{result.path}:{result.line}"
                if key not in seen_lines:
                    all_results.append(result)
                    seen_lines.add(key)

        # Sort by score and return top results
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:max_results]

    def search_json(self, query: str, max_results: int = 10) -> str:
        """Return search results as JSON string."""
        results = self.search(query, max_results)

        return json.dumps(
            {
                "query": query,
                "results": [{"path": result.relative_path, "line": result.line, "text": result.text, "score": result.score} for result in results],
                "count": len(results),
                "search_strategies": "exact_phrase, keywords, filename_matching",
            }
        )


# Global search engine instance
search_engine = UnifiedSearchEngine()
