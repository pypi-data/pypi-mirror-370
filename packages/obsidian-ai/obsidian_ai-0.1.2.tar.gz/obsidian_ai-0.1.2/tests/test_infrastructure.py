import pytest
import os
from pathlib import Path
from unittest.mock import patch

from obsidian_ai.infrastructure.config import Config
from obsidian_ai.infrastructure.file_system import iter_text_files, read_file_safe, _resolve_path
import string


class TestConfig:
    def test_default_config(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load()
            assert config.brain_dir == Path("~/brain").expanduser()
            assert config.model == "gpt-4o"
            assert config.max_tool_calls == 5
            assert ".git" in config.ignore_patterns
            assert ".obsidian" in config.ignore_patterns

    def test_env_override(self):
        with patch.dict(
            os.environ,
            {"OBSIDIAN_AI_BRAIN_DIR": "/custom/brain", "OBSIDIAN_AI_MODEL": "gpt-3.5-turbo", "OBSIDIAN_AI_MAX_TOOL_CALLS": "10"},
            clear=True,
        ):
            # Clear the cache
            Config.load.cache_clear()
            config = Config.load()
            assert config.brain_dir == Path("/custom/brain")
            assert config.model == "gpt-3.5-turbo"
            assert config.max_tool_calls == 10

    def test_ignore_patterns_env(self):
        with patch.dict(os.environ, {"OBSIDIAN_AI_IGNORE_PATTERNS": "temp/*,*.draft,private"}, clear=True):
            Config.load.cache_clear()
            config = Config.load()
            assert "temp/*" in config.ignore_patterns
            assert "*.draft" in config.ignore_patterns
            assert "private" in config.ignore_patterns
            # Default patterns should still be there
            assert ".git" in config.ignore_patterns

    def test_cache_dir_derived(self):
        with patch.dict(os.environ, {"OBSIDIAN_AI_BRAIN_DIR": "/test/brain"}, clear=True):
            Config.load.cache_clear()
            config = Config.load()
            assert config.cache_dir == Path("/test/brain/.obsidian_ai_cache")


class TestFileSystem:
    def test_iter_text_files(self, temp_brain):
        # Create test files
        (temp_brain / "note.md").write_text("markdown content")
        (temp_brain / "text.txt").write_text("text content")
        (temp_brain / "doc.org").write_text("org content")
        (temp_brain / "readme.rst").write_text("rst content")
        (temp_brain / "ignore.pdf").write_text("binary content")
        (temp_brain / "script.py").write_text("python code")

        # Create subdirectory
        subdir = temp_brain / "subdir"
        subdir.mkdir()
        (subdir / "subnote.md").write_text("sub content")
        (subdir / "ignore.tmp").write_text("temp file")

        files = list(iter_text_files(temp_brain))
        file_names = [f.name for f in files]

        # Should include text files
        assert "note.md" in file_names
        assert "text.txt" in file_names
        assert "doc.org" in file_names
        assert "readme.rst" in file_names
        assert "subnote.md" in file_names

        # Should exclude non-text files
        assert "ignore.pdf" not in file_names
        assert "script.py" not in file_names

    def test_iter_text_files_with_ignore_patterns(self, temp_brain):
        (temp_brain / "note.md").write_text("content")
        (temp_brain / "ignore.md").write_text("content")

        # Create .git directory
        git_dir = temp_brain / ".git"
        git_dir.mkdir()
        (git_dir / "config.md").write_text("git config")

        files = list(iter_text_files(temp_brain, ignore_patterns=[".git", "ignore.md"]))
        file_names = [f.name for f in files]

        assert "note.md" in file_names
        assert "ignore.md" not in file_names
        assert "config.md" not in file_names

    def test_read_file_safe_basic(self, temp_brain):
        test_file = temp_brain / "test.md"
        test_content = "# Test\nThis is test content."
        test_file.write_text(test_content)

        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            content = read_file_safe("test.md")
            assert content == test_content

    def test_read_file_safe_with_range(self, temp_brain):
        test_file = temp_brain / "test.md"
        test_content = string.digits * 10  # 100 chars
        test_file.write_text(test_content)

        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            content = read_file_safe("test.md", start_byte=10, max_bytes=20)
            assert content == test_content[10:30]

    def test_read_file_safe_absolute_path(self, temp_brain):
        test_file = temp_brain / "test.md"
        test_content = "Test content"
        test_file.write_text(test_content)

        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            content = read_file_safe(str(test_file))
            assert content == test_content

    def test_read_file_safe_not_found(self, temp_brain):
        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            with pytest.raises(ValueError, match="File not found"):
                read_file_safe("nonexistent.md")

    def test_resolve_path_security(self, temp_brain):
        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            # Try to access file outside brain directory
            with pytest.raises(ValueError, match="Path outside brain directory"):
                _resolve_path("../outside.md")

            # Absolute path outside brain directory
            with pytest.raises(ValueError, match="Path outside brain directory"):
                _resolve_path("/etc/passwd")

    def test_resolve_path_valid_integration(self, temp_brain):
        """Integration test for resolve_path with actual file system."""
        test_file = temp_brain / "valid.md"
        test_file.write_text("content")

        # Test the actual implementation with real paths
        from obsidian_ai.infrastructure.config import Config

        old_config = Config.load()

        # Temporarily override the config
        test_config = Config(
            brain_dir=temp_brain,
            model=old_config.model,
            max_tool_calls=old_config.max_tool_calls,
            cache_dir=temp_brain / ".cache",
            ignore_patterns=old_config.ignore_patterns,
        )

        with patch("obsidian_ai.infrastructure.file_system.config", test_config):
            # Relative path
            resolved = _resolve_path("valid.md")
            assert resolved.resolve() == test_file.resolve()

            # Absolute path within brain
            resolved = _resolve_path(str(test_file))
            assert resolved.resolve() == test_file.resolve()

    def test_read_file_safe_encoding_errors(self, temp_brain):
        test_file = temp_brain / "binary.md"
        # Write some binary data that might cause encoding issues
        test_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")

        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            # Should handle encoding errors gracefully
            content = read_file_safe("binary.md")
            assert isinstance(content, str)  # Should return string, not raise error

    def test_read_file_safe_large_file(self, temp_brain):
        test_file = temp_brain / "large.md"
        large_content = "x" * 100000  # 100KB
        test_file.write_text(large_content)

        with patch("obsidian_ai.infrastructure.file_system.config") as mock_config:
            mock_config.brain_dir = temp_brain

            # Read with default limit
            content = read_file_safe("large.md")
            assert len(content) <= 32768  # Default max_bytes

            # Read with custom limit
            content = read_file_safe("large.md", max_bytes=1000)
            assert len(content) <= 1000
