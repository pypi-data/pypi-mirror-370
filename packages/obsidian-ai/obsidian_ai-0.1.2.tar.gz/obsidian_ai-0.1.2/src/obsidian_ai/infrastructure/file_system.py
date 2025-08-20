from __future__ import annotations

from pathlib import Path
from collections.abc import Iterator

from .config import config


def iter_text_files(brain_dir: Path, ignore_patterns: list[str] | None = None) -> Iterator[Path]:
    """Iterate over text files in brain directory, respecting ignore patterns."""
    ignore_patterns = ignore_patterns or []

    for path in brain_dir.rglob("*"):
        if not path.is_file():
            continue

        # Check if file should be ignored
        if any(pattern in str(path) for pattern in ignore_patterns):
            continue

        # Only include text files
        if path.suffix.lower() in {".md", ".txt", ".org", ".rst"}:
            yield path


def read_file_safe(path: str, start_byte: int = 0, max_bytes: int = 32768) -> str:
    """Safely read a file with error handling."""
    try:
        file_path = _resolve_path(path)
        with file_path.open("rb") as f:
            f.seek(max(0, start_byte))
            data = f.read(max(1, max_bytes))
        return data.decode("utf-8", errors="ignore")
    except Exception as e:
        raise ValueError(f"Cannot read {path}: {e}")


def _resolve_path(path: str) -> Path:
    """Resolve and validate a file path within the brain directory."""
    if Path(path).is_absolute():
        resolved = Path(path).resolve()
    else:
        resolved = (config.brain_dir / path).resolve()

    # Security check: ensure path is within brain directory
    if not str(resolved).startswith(str(config.brain_dir.resolve())):
        raise ValueError("Path outside brain directory")

    if not resolved.exists():
        raise ValueError("File not found")

    return resolved
