#!/usr/bin/env python3
"""Test script to verify tools and agents work with prepared bundles."""

import asyncio
from pathlib import Path

from amplifier_foundation import Bundle
from amplifier_foundation import load_bundle


async def main() -> None:
    """Test tools and agent delegation."""
    print("=" * 60)
    print("Testing Tools and Agents with Bundle.prepare()")
    print("=" * 60)

    # Load foundation bundle
    foundation_path = Path(__file__).parent.parent
    print(f"\n[1/3] Loading foundation bundle from: {foundation_path}")

    foundation = await load_bundle(str(foundation_path), auto_include=False)
    print(f"      Loaded: {foundation.name} v{foundation.version}")
    print(f"      Tools: {len(foundation.tools)}")
    print(f"      Agents: {list(foundation.agents.keys())}")

    # Create provider bundle with local module overrides for testing
    # This uses local paths so we test against local code changes
    print("\n[2/3] Creating provider bundle with local module overrides...")
    amplifier_dev_root = Path(__file__).parent.parent.parent
    provider_bundle = Bundle(
        name="test-provider",
        version="1.0.0",
        session={
            # Override orchestrator to use local path (for testing local changes)
            "orchestrator": {
                "module": "loop-streaming",
                "source": "file://" + str(amplifier_dev_root / "amplifier-module-loop-streaming"),
                "config": {"extended_thinking": True},
            },
            # Override context to use local path
            "context": {
                "module": "context-simple",
                "source": "file://" + str(amplifier_dev_root / "amplifier-module-context-simple"),
            },
        },
        providers=[
            {
                "module": "provider-anthropic",
                "source": "file://" + str(amplifier_dev_root / "amplifier-module-provider-anthropic"),
                "config": {"default_model": "claude-sonnet-4-5"},
            }
        ],
    )

    # Compose and prepare
    composed = foundation.compose(provider_bundle)
    print("\n[3/3] Preparing bundle (downloading modules)...")
    prepared = await composed.prepare()

    print("\nMount plan ready:")
    print(f"  Tools: {[t.get('module') for t in prepared.mount_plan.get('tools', [])]}")
    print(f"  Agents: {list(prepared.mount_plan.get('agents', {}).keys())}")

    # Test with AmplifierSession using PreparedBundle.create_session()
    print("\n" + "=" * 60)
    print("Testing execution...")
    print("=" * 60)

    try:
        # Use the PreparedBundle's create_session() helper which properly mounts the resolver
        session = await prepared.create_session()

        async with session:
            # Test 1: Simple prompt (no tools)
            print("\n--- Test 1: Simple prompt ---")
            response = await session.execute("What is 2 + 2? Reply with just the number.")
            print(f"Response: {response}")

            # Test 2: Prompt that should use filesystem tool
            print("\n--- Test 2: Filesystem tool ---")
            examples_path = foundation_path / "examples"
            response = await session.execute(
                f"List the Python files in {examples_path}. Just show the filenames, nothing else."
            )
            print(f"Response: {response}")

        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
