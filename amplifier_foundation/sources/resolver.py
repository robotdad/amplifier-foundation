"""Simple source resolver implementation."""

from __future__ import annotations

from pathlib import Path

from amplifier_foundation.exceptions import BundleNotFoundError
from amplifier_foundation.paths.resolution import parse_uri

from .file import FileSourceHandler
from .git import GitSourceHandler
from .protocol import SourceHandlerProtocol


class SimpleSourceResolver:
    """Simple implementation of SourceResolverProtocol.

    Supports:
    - file:// and local paths via FileSourceHandler
    - git+https:// via GitSourceHandler

    Apps can extend by adding custom handlers.
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        base_path: Path | None = None,
    ) -> None:
        """Initialize resolver.

        Args:
            cache_dir: Directory for caching remote content.
            base_path: Base path for resolving relative paths.
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "amplifier" / "bundles"
        self.base_path = base_path or Path.cwd()

        # Default handlers
        self._handlers: list[SourceHandlerProtocol] = [
            FileSourceHandler(base_path=self.base_path),
            GitSourceHandler(),
        ]

    def add_handler(self, handler: SourceHandlerProtocol) -> None:
        """Add a custom source handler.

        Handlers are tried in order, first match wins.

        Args:
            handler: Handler to add.
        """
        self._handlers.insert(0, handler)  # Custom handlers take priority

    async def resolve(self, uri: str) -> Path:
        """Resolve a URI to a local path.

        Args:
            uri: URI string.

        Returns:
            Local path to the resolved content.

        Raises:
            BundleNotFoundError: If no handler can resolve the URI.
        """
        parsed = parse_uri(uri)

        for handler in self._handlers:
            if handler.can_handle(parsed):
                return await handler.resolve(parsed, self.cache_dir)

        raise BundleNotFoundError(f"No handler for URI: {uri}")
