"""Bundle resolver - loads and resolves bundles with dependencies."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from amplifier_foundation.bundle import Bundle
from amplifier_foundation.cache.simple import SimpleCache
from amplifier_foundation.discovery.simple import SimpleBundleDiscovery
from amplifier_foundation.exceptions import BundleDependencyError
from amplifier_foundation.exceptions import BundleLoadError
from amplifier_foundation.exceptions import BundleNotFoundError
from amplifier_foundation.io.frontmatter import parse_frontmatter
from amplifier_foundation.io.yaml import read_yaml
from amplifier_foundation.sources.resolver import SimpleSourceResolver

if TYPE_CHECKING:
    from amplifier_foundation.cache.protocol import CacheProviderProtocol
    from amplifier_foundation.discovery.protocol import BundleDiscoveryProtocol
    from amplifier_foundation.sources.protocol import SourceResolverProtocol


class BundleResolver:
    """Resolves and loads bundles from various sources.

    Handles:
    - URI resolution (git, file, package)
    - Dependency loading (includes)
    - Caching of loaded bundles
    - Bundle composition

    Apps may extend for custom discovery and caching policies.
    """

    def __init__(
        self,
        source_resolver: SourceResolverProtocol | None = None,
        discovery: BundleDiscoveryProtocol | None = None,
        cache: CacheProviderProtocol | None = None,
    ) -> None:
        """Initialize resolver with optional custom implementations.

        Args:
            source_resolver: Resolver for URIs to local paths.
            discovery: Bundle name to URI discovery.
            cache: Cache for loaded bundles.
        """
        self.source_resolver = source_resolver or SimpleSourceResolver()
        self.discovery = discovery or SimpleBundleDiscovery()
        self.cache = cache or SimpleCache()
        self._loading: set[str] = set()  # Track bundles being loaded (cycle detection)

    async def load(self, source: str, auto_include: bool = True) -> Bundle:
        """Load a bundle from URI or name.

        Args:
            source: URI (git+https://, file://) or bundle name.
            auto_include: Whether to automatically load and compose includes.

        Returns:
            Loaded and composed Bundle.

        Raises:
            BundleNotFoundError: Bundle not found.
            BundleLoadError: Failed to load bundle.
            BundleDependencyError: Circular dependency detected.
        """
        # Check cache first
        if cached := self.cache.get(source):
            return cached

        # Resolve name to URI if needed
        uri = self._resolve_source(source)
        if uri is None:
            raise BundleNotFoundError(f"Bundle not found: {source}")

        # Detect circular dependencies
        if uri in self._loading:
            raise BundleDependencyError(f"Circular dependency detected: {uri}")

        self._loading.add(uri)
        try:
            # Resolve URI to local path
            local_path = await self.source_resolver.resolve(uri)
            if local_path is None:
                raise BundleNotFoundError(f"Could not resolve URI: {uri}")

            # Load bundle from path
            bundle = await self._load_from_path(local_path)

            # Register bundle name in discovery for namespace:path resolution
            if bundle.name:
                # Register with file:// URI pointing to the bundle's base path
                if bundle.base_path:
                    bundle_uri = f"file://{bundle.base_path.resolve()}"
                else:
                    bundle_uri = uri
                self.discovery.register(bundle.name, bundle_uri)

            # Load includes and compose
            if auto_include and bundle.includes:
                bundle = await self._compose_includes(bundle)

            # Cache result
            self.cache.set(source, bundle)
            if source != uri:
                self.cache.set(uri, bundle)

            return bundle
        finally:
            self._loading.discard(uri)

    def _resolve_source(self, source: str, base_path: Path | None = None) -> str | None:
        """Resolve source to URI.

        Resolution priority:
        1. URIs: git+, http://, https://, file:// → Resolve directly
        2. Local paths: Starting with ./, ../, ~/, / → Resolve as filesystem path
        3. Bundle references: namespace:path → Look up namespace, resolve path within it
        4. Plain names: foundation → Discovery lookup for bundle name

        Args:
            source: Bundle name, URI, or namespace:path reference.
            base_path: Base path for resolving relative paths within bundles.

        Returns:
            URI string, or None if not found.
        """
        # 1. Check if it's already a URI
        if "://" in source or source.startswith("git+"):
            return source

        # 2. Check if it's an explicit local path (starts with ./, ../, ~/, /)
        if source.startswith(("./", "../", "~/", "/")):
            path = Path(source).expanduser()
            if path.exists():
                return f"file://{path.resolve()}"
            return None

        # 3. Check for namespace:path syntax (bundle reference)
        if ":" in source:
            namespace, rel_path = source.split(":", 1)
            # Look up namespace to find the base bundle
            namespace_uri = self.discovery.find(namespace)
            if namespace_uri:
                # Resolve the path within the namespace's bundle directory
                # Convert URI to path if it's a file:// URI
                if namespace_uri.startswith("file://"):
                    namespace_path = Path(namespace_uri[7:])
                else:
                    # For non-file URIs (e.g., git+), we need to resolve through source_resolver
                    # For now, construct a combined reference that can be resolved later
                    return f"{namespace_uri}#{rel_path}"

                # Find the resource within the namespace bundle
                if namespace_path.is_file():
                    # If namespace points to a file, resolve relative to its parent
                    resource_path = namespace_path.parent / rel_path
                else:
                    # If namespace points to a directory, resolve relative to it
                    resource_path = namespace_path / rel_path

                # Try common extensions if path doesn't exist directly
                candidates = [
                    resource_path,
                    resource_path.with_suffix(".yaml"),
                    resource_path.with_suffix(".yml"),
                    resource_path.with_suffix(".md"),
                    resource_path / "bundle.yaml",
                    resource_path / "bundle.md",
                ]
                for candidate in candidates:
                    if candidate.exists():
                        return f"file://{candidate.resolve()}"

            return None

        # 4. Try discovery for plain names
        return self.discovery.find(source)

    async def _load_from_path(self, path: Path) -> Bundle:
        """Load bundle from local path.

        Args:
            path: Path to bundle file or directory.

        Returns:
            Bundle instance.

        Raises:
            BundleLoadError: Failed to load bundle.
        """
        if path.is_dir():
            # Directory bundle - look for bundle.md or bundle.yaml
            bundle_md = path / "bundle.md"
            bundle_yaml = path / "bundle.yaml"

            if bundle_md.exists():
                return await self._load_markdown_bundle(bundle_md)
            if bundle_yaml.exists():
                return await self._load_yaml_bundle(bundle_yaml)
            raise BundleLoadError(f"Not a valid bundle: missing bundle.md or bundle.yaml in {path}")

        # Single file bundle
        if path.suffix == ".md":
            return await self._load_markdown_bundle(path)
        if path.suffix in (".yaml", ".yml"):
            return await self._load_yaml_bundle(path)
        raise BundleLoadError(f"Unknown bundle format: {path}")

    async def _load_markdown_bundle(self, path: Path) -> Bundle:
        """Load bundle from markdown file with frontmatter.

        Args:
            path: Path to markdown file.

        Returns:
            Bundle instance.
        """
        content = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)

        bundle = Bundle.from_dict(frontmatter, base_path=path.parent)
        bundle.instruction = body.strip() if body.strip() else None

        return bundle

    async def _load_yaml_bundle(self, path: Path) -> Bundle:
        """Load bundle from YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Bundle instance.
        """
        data = await read_yaml(path)
        if data is None:
            data = {}

        return Bundle.from_dict(data, base_path=path.parent)

    async def _compose_includes(self, bundle: Bundle) -> Bundle:
        """Load and compose included bundles.

        Args:
            bundle: Bundle with includes to resolve.

        Returns:
            Composed Bundle.
        """
        if not bundle.includes:
            return bundle

        # Load all includes
        included_bundles: list[Bundle] = []
        for include in bundle.includes:
            # Handle different include formats
            include_source = self._parse_include(include)
            if include_source:
                try:
                    included = await self.load(include_source, auto_include=True)
                    included_bundles.append(included)
                except BundleNotFoundError:
                    # Includes are opportunistic - skip if not found
                    pass

        if not included_bundles:
            return bundle

        # Compose: includes first, then current bundle overrides
        result = included_bundles[0]
        for included in included_bundles[1:]:
            result = result.compose(included)

        # Current bundle overrides includes
        return result.compose(bundle)

    def _parse_include(self, include: str | dict[str, Any]) -> str | None:
        """Parse include directive to source string.

        Handles:
        - "bundle-name" (string)
        - {"bundle": "name"} (dict)
        - {"bundle": "name", "version": ">=1.0.0"} (with version)

        Args:
            include: Include directive.

        Returns:
            Source string to load, or None if invalid.
        """
        if isinstance(include, str):
            return include

        if isinstance(include, dict):
            bundle_ref = include.get("bundle")
            if bundle_ref:
                return str(bundle_ref)

        return None


async def load_bundle(
    source: str,
    auto_include: bool = True,
    resolver: BundleResolver | None = None,
) -> Bundle:
    """Convenience function to load a bundle.

    Args:
        source: URI or bundle name.
        auto_include: Whether to load includes.
        resolver: Optional custom resolver.

    Returns:
        Loaded Bundle.
    """
    resolver = resolver or BundleResolver()
    return await resolver.load(source, auto_include=auto_include)
