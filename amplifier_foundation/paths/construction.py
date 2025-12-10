"""Path construction utilities for bundle resources."""

from __future__ import annotations

from pathlib import Path


def construct_agent_path(base: Path, name: str) -> Path:
    """Construct path to an agent file.

    Looks for agent in agents/ subdirectory with .md extension.

    Args:
        base: Base directory (bundle root).
        name: Agent name.

    Returns:
        Path to agent file.
    """
    # Try with and without .md extension
    if name.endswith(".md"):
        return base / "agents" / name
    return base / "agents" / f"{name}.md"


def construct_context_path(base: Path, name: str) -> Path:
    """Construct path to a context file.

    Looks for context in context/ subdirectory with .md extension.

    Args:
        base: Base directory (bundle root).
        name: Context file name.

    Returns:
        Path to context file.
    """
    # Try with and without .md extension
    if name.endswith(".md"):
        return base / "context" / name
    return base / "context" / f"{name}.md"
