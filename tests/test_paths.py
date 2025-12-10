"""Tests for path utilities."""

from pathlib import Path

from amplifier_foundation.paths.construction import construct_agent_path
from amplifier_foundation.paths.construction import construct_context_path
from amplifier_foundation.paths.resolution import normalize_path
from amplifier_foundation.paths.resolution import parse_uri


class TestParseUri:
    """Tests for parse_uri function."""

    def test_git_https_uri(self) -> None:
        """Parses git+https:// URIs."""
        result = parse_uri("git+https://github.com/user/repo@main")
        assert result.scheme == "git+https"
        assert result.host == "github.com"
        assert result.path == "/user/repo"
        assert result.ref == "main"

    def test_git_uri_with_subpath(self) -> None:
        """Parses git URI with subpath."""
        result = parse_uri("git+https://github.com/user/repo@main/path/to/bundle")
        assert result.scheme == "git+https"
        assert result.host == "github.com"
        assert result.path == "/user/repo"
        assert result.ref == "main"
        assert result.subpath == "path/to/bundle"

    def test_file_uri(self) -> None:
        """Parses file:// URIs."""
        result = parse_uri("file:///home/user/bundle")
        assert result.scheme == "file"
        assert result.path == "/home/user/bundle"

    def test_https_uri(self) -> None:
        """Parses https:// URIs."""
        result = parse_uri("https://example.com/bundle.yaml")
        assert result.scheme == "https"
        assert result.host == "example.com"
        assert result.path == "/bundle.yaml"

    def test_local_path(self) -> None:
        """Parses local paths as file URIs."""
        result = parse_uri("/home/user/bundle")
        assert result.scheme == "file"
        assert result.path == "/home/user/bundle"

    def test_relative_path(self) -> None:
        """Parses relative paths."""
        result = parse_uri("./bundles/my-bundle")
        assert result.scheme == "file"
        assert result.path == "./bundles/my-bundle"


class TestNormalizePath:
    """Tests for normalize_path function."""

    def test_absolute_path(self) -> None:
        """Absolute paths remain absolute."""
        result = normalize_path("/home/user/file.txt")
        assert result == Path("/home/user/file.txt")

    def test_relative_path_with_base(self) -> None:
        """Relative paths are resolved against base."""
        result = normalize_path("file.txt", relative_to=Path("/home/user"))
        assert result == Path("/home/user/file.txt")

    def test_relative_path_without_base(self) -> None:
        """Relative paths without base use cwd."""
        result = normalize_path("file.txt")
        assert result.is_absolute()

    def test_path_object_input(self) -> None:
        """Accepts Path objects."""
        result = normalize_path(Path("/home/user/file.txt"))
        assert result == Path("/home/user/file.txt")


class TestConstructPaths:
    """Tests for path construction utilities."""

    def test_construct_agent_path(self) -> None:
        """Constructs agent path."""
        base = Path("/bundle")
        result = construct_agent_path(base, "code-reviewer")
        assert result == Path("/bundle/agents/code-reviewer.md")

    def test_construct_context_path(self) -> None:
        """Constructs context path with any extension."""
        base = Path("/bundle")
        # Context files include their extension (unlike agents which auto-append .md)
        result = construct_context_path(base, "philosophy.md")
        assert result == Path("/bundle/context/philosophy.md")
        # Works with any extension
        result = construct_context_path(base, "config.yaml")
        assert result == Path("/bundle/context/config.yaml")
        # Works with nested paths
        result = construct_context_path(base, "examples/snippet.py")
        assert result == Path("/bundle/context/examples/snippet.py")

    def test_paths_are_standardized(self) -> None:
        """Paths use standard locations."""
        base = Path("/test")
        agent = construct_agent_path(base, "agent")
        context = construct_context_path(base, "ctx")
        assert "agents" in str(agent)
        assert "context" in str(context)
