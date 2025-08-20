import pytest
from unittest.mock import patch

from obsidian_ai.core.search_engine import SearchResult, ExactPhraseSearch, KeywordSearch, FilenameSearch, UnifiedSearchEngine


@pytest.fixture
def mock_brain(tmp_path):
    """Create a mock brain directory with test files."""
    brain = tmp_path / "brain"
    brain.mkdir()

    # Create test files
    (brain / "people.md").write_text(
        """
# People

## [[Tara]]
Tara is a friend who visited on [[2025-08-18]].

## [[Steve Baker]]
Met Steve at a conference about AI research.
""".strip()
    )

    (brain / "daily_notes").mkdir()
    (brain / "daily_notes" / "2025-08-18.md").write_text(
        """
# Daily Note - August 18, 2025

- Today is an interesting day, as it's the day that [[Tara]] comes to the US.
- Mixed feelings, if stuff goes well, might be one of the first primary interactions.
- Also meeting with [[Steve Baker]] about the AI project.
""".strip()
    )

    (brain / "projects").mkdir()
    (brain / "projects" / "ai_research.md").write_text(
        """
# AI Research Project

Working with [[Steve Baker]] on advanced AI systems.
Planning to implement deep learning models.

## Team
- [[Steve Baker]] - Lead researcher
- [[Tara]] - Data scientist (joining remotely)
""".strip()
    )

    return brain


@pytest.fixture
def mock_config(mock_brain):
    """Mock the config to use our test brain directory."""
    with patch("obsidian_ai.infrastructure.config.config") as mock_cfg:
        mock_cfg.brain_dir = mock_brain
        mock_cfg.ignore_patterns = [".git", "__pycache__"]
        yield mock_cfg


class TestExactPhraseSearch:
    def test_exact_phrase_found_integration(self, mock_brain):
        """Integration test using actual files."""
        from obsidian_ai.infrastructure.config import Config

        test_config = Config(
            brain_dir=mock_brain, model="gpt-4o", max_tool_calls=5, cache_dir=mock_brain / ".cache", ignore_patterns=[".git", "__pycache__"]
        )

        with patch("obsidian_ai.core.search_engine.config", test_config):
            search = ExactPhraseSearch()
            # Use a simpler search term that definitely exists
            results = search.search("Tara", max_results=10)

        assert len(results) >= 1
        assert any("Tara" in result.text for result in results)

    def test_case_insensitive_search(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = ExactPhraseSearch()
            results = search.search("STEVE BAKER", max_results=10)

        assert len(results) >= 1
        assert any("Steve Baker" in result.text for result in results)

    def test_empty_query(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = ExactPhraseSearch()
            results = search.search("", max_results=10)

        assert len(results) == 0

    def test_no_matches(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = ExactPhraseSearch()
            results = search.search("nonexistent phrase", max_results=10)

        assert len(results) == 0


class TestKeywordSearch:
    def test_single_keyword(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = KeywordSearch()
            results = search.search("Tara", max_results=10)

        assert len(results) >= 2  # Should find in multiple files
        paths = [result.relative_path for result in results]
        assert any("people.md" in path for path in paths)
        assert any("2025-08-18.md" in path for path in paths)

    def test_multiple_keywords_scoring(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = KeywordSearch()
            results = search.search("Steve Baker AI", max_results=10)

        # Should find results and score them
        assert len(results) >= 1
        # Results should be scored (files with more keyword matches first)
        ai_project_results = [r for r in results if "ai_research.md" in r.path]
        if ai_project_results:
            assert ai_project_results[0].score >= 2  # Should match multiple keywords

    def test_short_keywords_ignored(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = KeywordSearch()
            results = search.search("is a to", max_results=10)  # All short words

        assert len(results) == 0


class TestFilenameSearch:
    def test_filename_match(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = FilenameSearch()
            results = search.search("people", max_results=10)

        assert len(results) >= 1
        assert any("people.md" in result.path for result in results)
        assert any("📁" in result.text for result in results)  # Should include file icon

    def test_partial_filename_match(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            search = FilenameSearch()
            results = search.search("ai", max_results=10)

        assert len(results) >= 1
        assert any("ai_research.md" in result.path for result in results)


class TestUnifiedSearchEngine:
    def test_unified_search_combines_strategies(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            engine = UnifiedSearchEngine()
            results = engine.search("Tara", max_results=10)

        # Should find results from multiple strategies
        assert len(results) >= 2

        # Check that we have diverse result types
        paths = [result.relative_path for result in results]
        assert len(set(paths)) >= 2  # Multiple different files

    def test_search_json_format(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            engine = UnifiedSearchEngine()
            json_result = engine.search_json("Steve Baker", max_results=5)

        import json

        data = json.loads(json_result)

        assert data["query"] == "Steve Baker"
        assert "results" in data
        assert "count" in data
        assert "search_strategies" in data
        assert data["count"] >= 1

    def test_deduplication(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            engine = UnifiedSearchEngine()
            results = engine.search("Steve Baker", max_results=10)

        # Should not have duplicate results from same file/line
        seen_keys = set()
        for result in results:
            key = f"{result.path}:{result.line}"
            assert key not in seen_keys, f"Duplicate result: {key}"
            seen_keys.add(key)

    def test_score_based_ordering(self, mock_config):
        with patch("obsidian_ai.core.search_engine.config", mock_config):
            engine = UnifiedSearchEngine()
            results = engine.search("AI research", max_results=10)

        # Results should be ordered by score (descending)
        scores = [result.score for result in results]
        assert scores == sorted(scores, reverse=True)


class TestSearchResult:
    def test_relative_path_property(self, mock_brain):
        result = SearchResult(path=str(mock_brain / "people.md"), line=1, text="test", brain_dir=mock_brain, score=1.0)

        assert result.relative_path == "people.md"

    def test_search_result_immutable(self, mock_brain):
        result = SearchResult(path=str(mock_brain / "test.md"), line=1, text="test", brain_dir=mock_brain)

        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            result.text = "modified"
