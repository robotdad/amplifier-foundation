"""Data models for @mention handling."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ContextFile:
    """A context file loaded from an @mention."""

    path: Path
    content: str
    content_hash: str  # SHA-256 hash for deduplication


@dataclass
class MentionResult:
    """Result of resolving a single @mention."""

    mention: str
    resolved_path: Path | None
    content: str | None
    error: str | None

    @property
    def found(self) -> bool:
        """True if the mention was successfully resolved."""
        return self.resolved_path is not None and self.content is not None
