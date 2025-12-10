"""URI parsing and path normalization utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class ParsedURI:
    """Parsed URI components."""

    scheme: str  # git, file, http, https, or empty for package names
    host: str  # github.com, etc.
    path: str  # /org/repo or local path
    ref: str  # @main, @v1.0.0, etc. (empty if not specified)
    subpath: str  # /path/within/repo (empty if not specified)

    @property
    def is_git(self) -> bool:
        """True if this is a git URI."""
        return self.scheme == "git" or self.scheme.startswith("git+")

    @property
    def is_file(self) -> bool:
        """True if this is a file URI or local path."""
        return self.scheme == "file" or (self.scheme == "" and "/" in self.path)

    @property
    def is_http(self) -> bool:
        """True if this is an HTTP/HTTPS URI."""
        return self.scheme in ("http", "https")

    @property
    def is_package(self) -> bool:
        """True if this looks like a package/bundle name."""
        return self.scheme == "" and "/" not in self.path


def parse_uri(uri: str) -> ParsedURI:
    """Parse a URI into components.

    Supports:
    - git+https://github.com/org/repo@ref/subpath
    - file:///path/to/file
    - /absolute/path
    - ./relative/path
    - package-name
    - package/subpath

    Args:
        uri: URI string to parse.

    Returns:
        ParsedURI with extracted components.
    """
    # Handle git+ prefix
    if uri.startswith("git+"):
        return _parse_git_uri(uri[4:])

    # Handle explicit file:// scheme
    if uri.startswith("file://"):
        path = uri[7:]
        return ParsedURI(scheme="file", host="", path=path, ref="", subpath="")

    # Handle absolute paths
    if uri.startswith("/"):
        return ParsedURI(scheme="file", host="", path=uri, ref="", subpath="")

    # Handle relative paths
    if uri.startswith("./") or uri.startswith("../"):
        return ParsedURI(scheme="file", host="", path=uri, ref="", subpath="")

    # Handle http/https URLs
    if uri.startswith("http://") or uri.startswith("https://"):
        parsed = urlparse(uri)
        return ParsedURI(
            scheme=parsed.scheme,
            host=parsed.netloc,
            path=parsed.path,
            ref="",
            subpath="",
        )

    # Assume package name or package/subpath
    if "/" in uri:
        # Could be package/subpath like "foundation/providers/anthropic"
        parts = uri.split("/", 1)
        return ParsedURI(
            scheme="",
            host="",
            path=parts[0],
            ref="",
            subpath=parts[1] if len(parts) > 1 else "",
        )

    return ParsedURI(scheme="", host="", path=uri, ref="", subpath="")


def _parse_git_uri(uri: str) -> ParsedURI:
    """Parse a git URI (without git+ prefix)."""
    parsed = urlparse(uri)

    # Extract ref and subpath from path
    path = parsed.path
    ref = ""
    subpath = ""

    # Check for @ref syntax
    if "@" in path:
        # Split on @ but be careful about paths that might have @ in them
        match = re.match(r"^([^@]+)@([^/]+)(.*)$", path)
        if match:
            path = match.group(1)
            ref = match.group(2)
            subpath = match.group(3).lstrip("/")

    return ParsedURI(
        scheme="git+" + parsed.scheme,
        host=parsed.netloc,
        path=path,
        ref=ref,
        subpath=subpath,
    )


def normalize_path(path: str | Path, relative_to: Path | None = None) -> Path:
    """Normalize a path, resolving relative paths if base provided.

    Args:
        path: Path to normalize.
        relative_to: Base path for relative paths.

    Returns:
        Normalized absolute Path.
    """
    p = Path(path)

    if p.is_absolute():
        return p.resolve()

    if relative_to:
        return (relative_to / p).resolve()

    return p.resolve()
