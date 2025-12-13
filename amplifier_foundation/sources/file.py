"""File source handler for local paths."""

from __future__ import annotations

from pathlib import Path

from amplifier_foundation.exceptions import BundleNotFoundError
from amplifier_foundation.paths.resolution import ParsedURI


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

    async def resolve(self, parsed: ParsedURI, cache_dir: Path) -> Path:
        """Resolve file URI to local path.

        Args:
            parsed: Parsed URI components.
            cache_dir: Not used for local files.

        Returns:
            Resolved local path.

        Raises:
            BundleNotFoundError: If file doesn't exist.
        """
        path_str = parsed.path

        # Handle relative paths
        if path_str.startswith("./") or path_str.startswith("../"):
            path = self.base_path / path_str
        else:
            path = Path(path_str)

        path = path.resolve()

        # Apply subpath if specified (from #subdirectory= fragment)
        if parsed.subpath:
            path = path / parsed.subpath

        if not path.exists():
            raise BundleNotFoundError(f"File not found: {path}")

        return path
