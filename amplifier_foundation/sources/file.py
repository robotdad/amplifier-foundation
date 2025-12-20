"""File source handler for local paths."""

from __future__ import annotations

from pathlib import Path

from amplifier_foundation.exceptions import BundleNotFoundError
from amplifier_foundation.paths.resolution import ParsedURI
from amplifier_foundation.paths.resolution import ResolvedSource


class FileSourceHandler:
    """Handler for file:// URIs and local paths."""

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize handler.

        Args:
            base_path: Base path for resolving relative paths.
        """
        self.base_path = base_path or Path.cwd()

    def can_handle(self, parsed: ParsedURI) -> bool:
        """Check if this handler can handle the given URI."""
        return parsed.is_file

    async def resolve(self, parsed: ParsedURI, cache_dir: Path) -> ResolvedSource:
        """Resolve file URI to local path.

        Args:
            parsed: Parsed URI components.
            cache_dir: Not used for local files.

        Returns:
            ResolvedSource with active_path and source_root.

        Raises:
            BundleNotFoundError: If file doesn't exist.
        """
        path_str = parsed.path

        # Handle relative paths
        if path_str.startswith("./") or path_str.startswith("../"):
            source_root = self.base_path / path_str
        else:
            source_root = Path(path_str)

        source_root = source_root.resolve()

        # Apply subpath if specified (from #subdirectory= fragment)
        active_path = source_root
        if parsed.subpath:
            active_path = source_root / parsed.subpath

        if not active_path.exists():
            raise BundleNotFoundError(f"File not found: {active_path}")

        return ResolvedSource(active_path=active_path, source_root=source_root)
