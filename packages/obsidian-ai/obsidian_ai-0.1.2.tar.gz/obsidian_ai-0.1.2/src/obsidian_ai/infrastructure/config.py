import os
from pathlib import Path
from dataclasses import dataclass
from functools import cache


@dataclass(frozen=True)
class Config:
    brain_dir: Path
    model: str
    max_tool_calls: int
    cache_dir: Path
    ignore_patterns: list[str]

    @classmethod
    @cache
    def load(cls) -> "Config":
        brain_dir = Path(os.getenv("OBSIDIAN_AI_BRAIN_DIR", "~/brain")).expanduser()

        # Default ignore patterns
        default_ignores = [".git", ".obsidian", ".obsidian_ai_cache", "node_modules", "__pycache__", ".DS_Store", "Thumbs.db"]

        # Add user-specified patterns from environment
        env_ignores = os.getenv("OBSIDIAN_AI_IGNORE_PATTERNS", "")
        if env_ignores:
            user_patterns = [p.strip() for p in env_ignores.split(",") if p.strip()]
            default_ignores.extend(user_patterns)

        return cls(
            brain_dir=brain_dir,
            model=os.getenv("OBSIDIAN_AI_MODEL", "gpt-4o"),
            max_tool_calls=int(os.getenv("OBSIDIAN_AI_MAX_TOOL_CALLS", "5")),
            cache_dir=brain_dir / ".obsidian_ai_cache",
            ignore_patterns=default_ignores,
        )


config = Config.load()
