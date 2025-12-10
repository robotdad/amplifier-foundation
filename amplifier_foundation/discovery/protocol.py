"""Protocol for bundle discovery."""

from __future__ import annotations

from typing import Protocol


class BundleDiscoveryProtocol(Protocol):
    """Protocol for discovering bundles by name.

    Foundation provides SimpleBundleDiscovery with basic lookup.
    Apps extend with search paths, registries, etc.
    """

    def find(self, name: str) -> str | None:
        """Find a bundle URI by name.

        Args:
            name: Bundle name (e.g., "foundation", "foundation/providers/anthropic").

        Returns:
            URI string for the bundle, or None if not found.
        """
        ...

    def register(self, name: str, uri: str) -> None:
        """Register a bundle name to URI mapping.

        Args:
            name: Bundle name.
            uri: URI for the bundle.
        """
        ...
