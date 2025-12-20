"""Protocol for source resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from amplifier_foundation.paths.resolution import ParsedURI
from amplifier_foundation.paths.resolution import ResolvedSource


class SourceResolverProtocol(Protocol):
    """Protocol for resolving source URIs to local paths.

    Foundation provides SimpleSourceResolver with basic handlers.
    Apps may extend with additional source types or caching strategies.
    """

    async def resolve(self, uri: str) -> ResolvedSource:
        """Resolve a URI to local paths.

        For remote sources (git, http), downloads to cache and returns
        the local cache path. Returns both the active path (what was
        requested, possibly a subdirectory) and the source root (the
        full clone/extract root).

        Args:
            uri: URI string (git+https://..., file://..., /path, ./path, name).

        Returns:
            ResolvedSource with active_path and source_root.

        Raises:
            BundleNotFoundError: If source cannot be resolved.
        """
        ...


class SourceHandlerProtocol(Protocol):
    """Protocol for handling a specific source type."""

    def can_handle(self, parsed: ParsedURI) -> bool:
        """Check if this handler can handle the given URI.

        Args:
            parsed: Parsed URI components.

        Returns:
            True if this handler can resolve this URI type.
        """
        ...

    async def resolve(self, parsed: ParsedURI, cache_dir: Path) -> ResolvedSource:
        """Resolve the URI to local paths.

        Args:
            parsed: Parsed URI components.
            cache_dir: Directory for caching downloaded content.

        Returns:
            ResolvedSource with active_path and source_root.

        Raises:
            BundleNotFoundError: If source cannot be resolved.
        """
        ...
