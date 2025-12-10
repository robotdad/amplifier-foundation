"""Base @mention resolver implementation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amplifier_foundation.bundle import Bundle


class BaseMentionResolver:
    """Base implementation of MentionResolverProtocol.

    Supports two patterns:
    - @bundle-name:context-name - From bundle's context namespace
    - @path - Relative to base path

    Apps extend this class to add shortcuts like @user:, @project:.
    """

    def __init__(
        self,
        bundles: dict[str, Bundle] | None = None,
        base_path: Path | None = None,
    ) -> None:
        """Initialize resolver.

        Args:
            bundles: Dict mapping bundle names to Bundle instances.
            base_path: Base path for relative @path mentions.
        """
        self.bundles = bundles or {}
        self.base_path = base_path or Path.cwd()

    def resolve(self, mention: str) -> Path | None:
        """Resolve an @mention to a file path.

        Args:
            mention: The mention string (including @ prefix).

        Returns:
            Path to the resolved file, or None if not found.
        """
        if not mention.startswith("@"):
            return None

        mention_body = mention[1:]  # Remove @ prefix

        # Pattern 1: @bundle-name:context-name
        if ":" in mention_body:
            namespace, name = mention_body.split(":", 1)
            if bundle := self.bundles.get(namespace):
                return bundle.resolve_context_path(name)
            return None

        # Pattern 2: @path (relative to base)
        path = self.base_path / mention_body
        if path.exists():
            return path

        # Try with .md extension
        path_md = self.base_path / f"{mention_body}.md"
        if path_md.exists():
            return path_md

        return None

    def register_bundle(self, name: str, bundle: Bundle) -> None:
        """Register a bundle for namespace resolution.

        Args:
            name: Bundle name (namespace for @mentions).
            bundle: Bundle instance.
        """
        self.bundles[name] = bundle
