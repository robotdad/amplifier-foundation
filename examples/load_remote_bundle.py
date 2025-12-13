#!/usr/bin/env python3
"""Example: Load bundles from remote sources.

This example demonstrates loading bundles from:
1. Git repositories
2. Git repositories with subdirectory
3. Custom source resolver configuration
"""

import asyncio
from pathlib import Path

from amplifier_foundation import BundleResolver
from amplifier_foundation import SimpleBundleDiscovery
from amplifier_foundation import SimpleSourceResolver
from amplifier_foundation import load_bundle


async def load_from_git() -> None:
    """Load a bundle from a git repository."""
    print("=" * 60)
    print("Loading bundle from Git repository")
    print("=" * 60)

    # Load directly from git
    # Note: This will clone the repo to cache and load bundle.md
    uri = "git+https://github.com/microsoft/amplifier-foundation@main"

    print(f"\nLoading from: {uri}")
    try:
        bundle = await load_bundle(uri)
        print(f"Loaded: {bundle.name} v{bundle.version}")
        print(f"Tools: {len(bundle.tools)}")
    except Exception as e:
        print(f"Error (expected if no network): {e}")


async def load_from_git_subdirectory() -> None:
    """Load a bundle from a subdirectory within a git repository."""
    print("\n" + "=" * 60)
    print("Loading bundle from Git subdirectory")
    print("=" * 60)

    # Load from a specific subdirectory within a repo
    # The #subdirectory= fragment specifies the path inside the repo
    uri = "git+https://github.com/microsoft/amplifier-foundation@main#subdirectory=behaviors/logging"

    print(f"\nLoading from: {uri}")
    try:
        bundle = await load_bundle(uri)
        print(f"Loaded: {bundle.name} v{bundle.version}")
    except Exception as e:
        print(f"Error (expected if path doesn't exist): {e}")


async def custom_resolver_example() -> None:
    """Use a custom resolver with configured cache and pre-registered bundles."""
    print("\n" + "=" * 60)
    print("Using custom BundleResolver")
    print("=" * 60)

    # Configure cache directory
    cache_dir = Path.home() / ".cache" / "my-app" / "bundles"

    # Create discovery and pre-register known bundles
    discovery = SimpleBundleDiscovery()

    # Register bundles by name for easy lookup
    # In a real app, this might come from a config file or database
    discovery.register(
        "foundation",
        "git+https://github.com/microsoft/amplifier-foundation@main",
    )
    discovery.register(
        "my-local-bundle",
        f"file://{Path(__file__).parent.parent.resolve()}",
    )

    # Create resolver with custom configuration
    resolver = BundleResolver(
        source_resolver=SimpleSourceResolver(
            cache_dir=cache_dir,
            base_path=Path.cwd(),
        ),
        discovery=discovery,
    )

    print(f"\nCache directory: {cache_dir}")
    print("Registered bundles: foundation, my-local-bundle")

    # Load the local foundation bundle using the custom resolver
    local_path = Path(__file__).parent.parent
    try:
        bundle = await resolver.load(str(local_path))
        print(f"\nLoaded: {bundle.name} v{bundle.version}")
    except Exception as e:
        print(f"Error: {e}")


async def main() -> None:
    """Run all examples."""
    # Example 1: Load from git
    await load_from_git()

    # Example 2: Load from git subdirectory
    await load_from_git_subdirectory()

    # Example 3: Custom resolver
    await custom_resolver_example()

    print("\n" + "=" * 60)
    print("Examples complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
