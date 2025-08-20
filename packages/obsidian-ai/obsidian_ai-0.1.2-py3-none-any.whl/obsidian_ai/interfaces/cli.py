from __future__ import annotations

import os
import sys

import click
from loguru import logger
from rich.console import Console

from .chat import ChatSession
from ..core.search_engine import search_engine
from ..infrastructure.file_system import read_file_safe


console = Console()


def setup_logging(verbose: int) -> None:
    logger.remove()
    if verbose >= 1:
        logger.add(sys.stderr, level="DEBUG")
    elif verbose == 0:
        logger.add(sys.stderr, level="INFO")


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("--ignore", multiple=True, help="Additional ignore patterns (can be used multiple times)")
def cli(verbose: int, ignore: tuple[str, ...]) -> None:
    """Obsidian-AI: Chat with your notes."""
    setup_logging(verbose)

    # Store additional ignore patterns in environment for config to pick up
    if ignore:
        existing = os.getenv("OBSIDIAN_AI_IGNORE_PATTERNS", "")
        new_patterns = ",".join(ignore)
        if existing:
            os.environ["OBSIDIAN_AI_IGNORE_PATTERNS"] = f"{existing},{new_patterns}"
        else:
            os.environ["OBSIDIAN_AI_IGNORE_PATTERNS"] = new_patterns

        # Clear the cache so config reloads with new patterns
        from ..infrastructure.config import Config

        Config.load.cache_clear()


@cli.command()
@click.argument("query")
def chat(query: str) -> None:
    """Ask a question about your notes."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        sys.exit(1)

    session = ChatSession()
    response = session.chat_once(query)
    console.print(response)


@cli.command()
def repl() -> None:
    """Start interactive chat."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        sys.exit(1)

    session = ChatSession()
    session.chat_repl()


@cli.command()
@click.argument("query")
@click.option("--max-results", default=10, help="Maximum results")
def search(query: str, max_results: int) -> None:
    """Search notes for keywords."""
    results = search_engine.search(query, max_results)
    for result in results:
        console.print(f"[blue]{result.relative_path}:{result.line}[/blue] {result.text}")


@cli.command()
@click.argument("path")
@click.option("--start", default=0, help="Start byte")
@click.option("--max-bytes", default=4096, help="Max bytes to read")
def read(path: str, start: int, max_bytes: int) -> None:
    """Read a file from your notes."""
    try:
        content = read_file_safe(path, start, max_bytes)
        console.print(content)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def main() -> None:
    cli()
