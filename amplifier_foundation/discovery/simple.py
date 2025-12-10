"""Simple bundle discovery implementation."""

from __future__ import annotations


class SimpleBundleDiscovery:
    """Simple implementation of BundleDiscoveryProtocol.

    Uses an in-memory registry for name -> URI mappings.
    Apps can extend or replace with file-based registries, search paths, etc.
    """

    def __init__(self) -> None:
        """Initialize with empty registry."""
        self._registry: dict[str, str] = {}

    def find(self, name: str) -> str | None:
        """Find a bundle URI by name.

        Args:
            name: Bundle name.

        Returns:
            URI string for the bundle, or None if not found.
        """
        return self._registry.get(name)

    def register(self, name: str, uri: str) -> None:
        """Register a bundle name to URI mapping.

        Args:
            name: Bundle name.
            uri: URI for the bundle.
        """
        self._registry[name] = uri

    def register_many(self, mappings: dict[str, str]) -> None:
        """Register multiple name -> URI mappings.

        Args:
            mappings: Dict of name -> URI.
        """
        self._registry.update(mappings)
