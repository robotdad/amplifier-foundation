"""Protocol for source resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from amplifier_foundation.paths.resolution import ParsedURI


class SourceResolverProtocol(Protocol):
    """Protocol for resolving source URIs to local paths.

    Foundation provides SimpleSourceResolver with basic handlers.
    Apps may extend with additional source types or caching strategies.
    """

    async def resolve(self, uri: str) -> Path:
        """Resolve a URI to a local path.

        For remote sources (git, http), downloads to cache and returns
        the local cache path.

        Args:
            uri: URI string (git+https://..., file://..., /path, ./path, name).

        Returns:
            Local path to the resolved content.

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

    async def resolve(self, parsed: ParsedURI, cache_dir: Path) -> Path:
        """Resolve the URI to a local path.

        Args:
            parsed: Parsed URI components.
            cache_dir: Directory for caching downloaded content.

        Returns:
            Local path to the resolved content.

        Raises:
            BundleNotFoundError: If source cannot be resolved.
        """
        ...
