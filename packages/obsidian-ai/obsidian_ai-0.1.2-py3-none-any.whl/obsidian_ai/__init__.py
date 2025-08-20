__all__ = ["__version__", "main"]

try:
    from importlib.metadata import version as _dist_version

    __version__ = _dist_version("obsidian-ai")
except Exception:
    # Fallback for local, editable, or non-installed runs
    __version__ = "0.1.1"


def main() -> None:
    """Entry point for obsidian-ai CLI."""
    import sys

    args = sys.argv[1:]
    if args and args[0] in {"version", "--version", "-V"}:
        print(__version__)
        return

    from .interfaces.cli import main as cli_main

    cli_main()
