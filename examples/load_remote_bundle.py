#!/usr/bin/env python3
"""Example: Load bundles from remote sources.

This example demonstrates loading bundles from:
1. Git repositories (convenience function)
2. Git repositories with subdirectory
3. BundleRegistry for central bundle management
"""

import asyncio
from pathlib import Path

from amplifier_foundation import Bundle
from amplifier_foundation import BundleRegistry
from amplifier_foundation import BundleState
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


async def registry_example() -> None:
    """Use BundleRegistry for central bundle management."""
    print("\n" + "=" * 60)
    print("Using BundleRegistry")
    print("=" * 60)

    # BundleRegistry provides central bundle management:
    # - Registration: name → URI mappings
    # - Loading: resolve URIs, cache remotes, load bundles
    # - State tracking: version, loaded_at, checked_at
    # - Persistence: save/load registry state

    # Create registry with custom home directory
    # Default: ~/.amplifier or AMPLIFIER_HOME env var
    home = Path.home() / ".cache" / "my-app"
    registry = BundleRegistry(home=home)

    # =========================================================================
    # WELL-KNOWN BUNDLES PATTERN
    # =========================================================================
    # Define bundles your app knows about with their remote URIs.
    # This is APP-LAYER POLICY - foundation provides the mechanism,
    # your app decides WHICH bundles are "well-known".
    #
    # Benefits:
    # - Bundles always resolve (remote URI works even if not locally installed)
    # - Users can reference by short name: "foundation" instead of full git URL
    # - App controls what's available by default
    #
    # Use register() to batch-register well-known bundles:
    registry.register(
        {
            "foundation": "git+https://github.com/microsoft/amplifier-foundation@main",
            # Add more well-known bundles your app supports...
            # "my-bundle": "git+https://github.com/myorg/my-bundle@main",
        }
    )

    # You can also register local bundles for development:
    local_path = Path(__file__).parent.parent
    registry.register(
        {
            "my-local-bundle": f"file://{local_path.resolve()}",
        }
    )

    print(f"\nRegistry home: {registry.home}")
    print(f"Registered bundles: {registry.list_registered()}")

    # Load by registered name
    try:
        bundle = await registry.load("my-local-bundle")
        # Type narrowing for single bundle load
        if isinstance(bundle, Bundle):
            print(f"\nLoaded: {bundle.name} v{bundle.version}")

            # Check state
            state = registry.get_state("my-local-bundle")
            if isinstance(state, BundleState):
                print(f"Loaded at: {state.loaded_at}")
                print(f"Local path: {state.local_path}")
    except Exception as e:
        print(f"Error: {e}")


async def main() -> None:
    """Run all examples."""
    # Example 1: Load from git
    await load_from_git()

    # Example 2: Load from git subdirectory
    await load_from_git_subdirectory()

    # Example 3: BundleRegistry
    await registry_example()

    print("\n" + "=" * 60)
    print("Examples complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
