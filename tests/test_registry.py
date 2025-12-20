"""Tests for BundleRegistry."""

import tempfile
from pathlib import Path

import pytest
from amplifier_foundation.registry import BundleRegistry


class TestFindNearestBundleFile:
    """Tests for _find_nearest_bundle_file method."""

    def test_finds_bundle_md_in_start_directory(self) -> None:
        """Finds bundle.md in the starting directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "bundle.md").write_text("---\nname: root\n---\n# Root")

            registry = BundleRegistry(home=base / "home")
            result = registry._find_nearest_bundle_file(start=base, stop=base)

            assert result == base / "bundle.md"

    def test_finds_bundle_yaml_in_start_directory(self) -> None:
        """Finds bundle.yaml in the starting directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "bundle.yaml").write_text("name: root")

            registry = BundleRegistry(home=base / "home")
            result = registry._find_nearest_bundle_file(start=base, stop=base)

            assert result == base / "bundle.yaml"

    def test_prefers_bundle_md_over_bundle_yaml(self) -> None:
        """When both exist, prefers bundle.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "bundle.md").write_text("---\nname: root\n---\n# Root")
            (base / "bundle.yaml").write_text("name: root")

            registry = BundleRegistry(home=base / "home")
            result = registry._find_nearest_bundle_file(start=base, stop=base)

            assert result == base / "bundle.md"

    def test_walks_up_to_find_bundle(self) -> None:
        """Walks up directories to find bundle file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            subdir = base / "behaviors" / "recipes"
            subdir.mkdir(parents=True)

            # Root has bundle.md
            (base / "bundle.md").write_text("---\nname: root\n---\n# Root")

            # Subdir has its own bundle.yaml
            (subdir / "bundle.yaml").write_text("name: recipes")

            registry = BundleRegistry(home=base / "home")

            # Start from subdir parent (behaviors), stop at root (base)
            result = registry._find_nearest_bundle_file(
                start=subdir.parent,  # behaviors
                stop=base,
            )

            # Should find root's bundle.md
            assert result == base / "bundle.md"

    def test_returns_none_when_not_found(self) -> None:
        """Returns None when no bundle file found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            subdir = base / "behaviors" / "recipes"
            subdir.mkdir(parents=True)

            # No bundle files anywhere

            registry = BundleRegistry(home=base / "home")
            result = registry._find_nearest_bundle_file(start=subdir, stop=base)

            assert result is None

    def test_stops_at_stop_directory(self) -> None:
        """Does not search above stop directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create nested structure
            repo_root = base / "repo"
            repo_root.mkdir()
            behaviors = repo_root / "behaviors"
            behaviors.mkdir()
            recipes = behaviors / "recipes"
            recipes.mkdir()

            # Put bundle.md at repo_root (outside stop boundary)
            (repo_root / "bundle.md").write_text("---\nname: root\n---")

            registry = BundleRegistry(home=base / "home")

            # Search from recipes to behaviors (stop before repo_root)
            result = registry._find_nearest_bundle_file(
                start=recipes,
                stop=behaviors,
            )

            # Should NOT find repo_root/bundle.md because we stopped at behaviors
            assert result is None


class TestSubdirectoryBundleLoading:
    """Tests for loading bundles from subdirectories with root access."""

    @pytest.mark.asyncio
    async def test_subdirectory_bundle_gets_source_base_paths(self) -> None:
        """Subdirectory bundle gets source_base_paths populated for root access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create root bundle (bundle.md with frontmatter)
            (base / "bundle.md").write_text("---\nbundle:\n  name: root-bundle\n  version: 1.0.0\n---\n# Root Bundle")

            # Create shared context
            context_dir = base / "context"
            context_dir.mkdir()
            (context_dir / "shared.md").write_text("# Shared Context")

            # Create subdirectory bundle (YAML needs nested bundle: key)
            behaviors = base / "behaviors"
            behaviors.mkdir()
            recipes = behaviors / "recipes"
            recipes.mkdir()
            (recipes / "bundle.yaml").write_text("bundle:\n  name: recipes\n  version: 1.0.0")

            # Create registry and load subdirectory bundle via file source
            registry = BundleRegistry(home=base / "home")

            # Load the subdirectory bundle with a subpath
            # This simulates loading via git+https://...#subdirectory=behaviors/recipes
            bundle = await registry._load_single(f"file://{base}#subdirectory=behaviors/recipes")

            # The bundle should have source_base_paths set up
            assert bundle.name == "recipes"
            assert bundle.source_base_paths.get("recipes") == base.resolve()

    @pytest.mark.asyncio
    async def test_root_bundle_no_extra_source_base_paths(self) -> None:
        """Loading root bundle directly doesn't add extra source_base_paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create root bundle (bundle.md with frontmatter)
            (base / "bundle.md").write_text("---\nbundle:\n  name: root-bundle\n  version: 1.0.0\n---\n# Root Bundle")

            registry = BundleRegistry(home=base / "home")
            bundle = await registry._load_single(f"file://{base}")

            # When loading root directly (not subdirectory), no extra source_base_paths
            # because active_path == source_root
            assert bundle.name == "root-bundle"
            # source_base_paths should be empty or not contain extra entries
            assert "root-bundle" not in bundle.source_base_paths

    @pytest.mark.asyncio
    async def test_subdirectory_without_root_bundle_no_source_base_paths(self) -> None:
        """Subdirectory without discoverable root bundle doesn't add source_base_paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # No root bundle.md or bundle.yaml

            # Create subdirectory bundle (YAML needs nested bundle: key)
            subdir = base / "components" / "auth"
            subdir.mkdir(parents=True)
            (subdir / "bundle.yaml").write_text("bundle:\n  name: auth\n  version: 1.0.0")

            registry = BundleRegistry(home=base / "home")
            bundle = await registry._load_single(f"file://{base}#subdirectory=components/auth")

            # Without a root bundle, source_base_paths won't be populated
            assert bundle.name == "auth"
            assert "auth" not in bundle.source_base_paths
