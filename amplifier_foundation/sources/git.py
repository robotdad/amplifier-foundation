"""Git source handler for git+https:// URIs."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

from amplifier_foundation.exceptions import BundleNotFoundError
from amplifier_foundation.paths.resolution import ParsedURI
from amplifier_foundation.paths.resolution import ResolvedSource


class GitSourceHandler:
    """Handler for git+https:// URIs.

    Clones repositories to a cache directory and returns the local path.
    Uses shallow clones for efficiency.
    """

    def can_handle(self, parsed: ParsedURI) -> bool:
        """Check if this handler can handle the given URI."""
        return parsed.is_git

    async def resolve(self, parsed: ParsedURI, cache_dir: Path) -> ResolvedSource:
        """Resolve git URI to local cached path.

        Args:
            parsed: Parsed URI components.
            cache_dir: Directory for caching cloned repos.

        Returns:
            ResolvedSource with active_path and source_root.

        Raises:
            BundleNotFoundError: If clone fails or ref not found.
        """
        # Build git URL (without git+ prefix)
        scheme = parsed.scheme.replace("git+", "")
        git_url = f"{scheme}://{parsed.host}{parsed.path}"

        # Create cache key from URL and ref
        ref = parsed.ref or "HEAD"
        cache_key = hashlib.sha256(f"{git_url}@{ref}".encode()).hexdigest()[:16]
        repo_name = parsed.path.rstrip("/").split("/")[-1]
        cache_path = cache_dir / f"{repo_name}-{cache_key}"

        # Check if already cached
        if cache_path.exists():
            result_path = cache_path
            if parsed.subpath:
                result_path = cache_path / parsed.subpath
            if result_path.exists():
                return ResolvedSource(active_path=result_path, source_root=cache_path)

        # Clone repository
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove partial clone if exists
        if cache_path.exists():
            shutil.rmtree(cache_path)

        try:
            # Shallow clone with specific ref
            clone_args = ["git", "clone", "--depth", "1"]
            if parsed.ref:
                clone_args.extend(["--branch", parsed.ref])
            clone_args.extend([git_url, str(cache_path)])

            subprocess.run(
                clone_args,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise BundleNotFoundError(f"Failed to clone {git_url}@{ref}: {e.stderr}") from e

        # Return path with subpath if specified
        result_path = cache_path
        if parsed.subpath:
            result_path = cache_path / parsed.subpath

        if not result_path.exists():
            raise BundleNotFoundError(f"Subpath not found after clone: {parsed.subpath}")

        return ResolvedSource(active_path=result_path, source_root=cache_path)
