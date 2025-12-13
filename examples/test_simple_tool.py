#!/usr/bin/env python3
"""Test script with only filesystem tool (no task tool)."""

import asyncio
from pathlib import Path

from amplifier_foundation import Bundle


async def main() -> None:
    """Test filesystem tool only."""
    print("=" * 60)
    print("Testing Filesystem Tool Only (no task tool)")
    print("=" * 60)

    # Create minimal bundle with just filesystem tool
    bundle = Bundle(
        name="test-minimal",
        version="1.0.0",
        session={
            "orchestrator": {
                "module": "loop-streaming",
                # Use local path (same as CLI settings.yaml)
                "source": "file://" + str(Path(__file__).parent.parent.parent / "amplifier-module-loop-streaming"),
                "config": {
                    "extended_thinking": True,  # Testing with extended_thinking enabled
                },
            },
            "context": {
                "module": "context-simple",
                "source": "file://" + str(Path(__file__).parent.parent.parent / "amplifier-module-context-simple"),
            },
        },
        providers=[
            {
                "module": "provider-anthropic",
                "source": "file://" + str(Path(__file__).parent.parent.parent / "amplifier-module-provider-anthropic"),
                "config": {"default_model": "claude-sonnet-4-5"},
            }
        ],
        tools=[
            {
                "module": "tool-filesystem",
                "source": "file://" + str(Path(__file__).parent.parent.parent / "amplifier-module-tool-filesystem"),
            }
        ],
    )

    print("\n[1/2] Preparing bundle...")
    prepared = await bundle.prepare()

    # Debug: Show resolved module paths
    print("\nResolved module paths:")
    for mod_id, path in prepared.resolver._paths.items():
        print(f"  {mod_id}: {path}")

    print("\nMount plan ready:")
    print(f"  Orchestrator: {prepared.mount_plan.get('session', {}).get('orchestrator', {}).get('module')}")
    print(f"  Tools: {[t.get('module') for t in prepared.mount_plan.get('tools', [])]}")

    print("\n[2/2] Testing execution...")
    print("-" * 60)

    try:
        session = await prepared.create_session()

        async with session:
            # Test: Use filesystem tool
            examples_path = Path(__file__).parent
            print(f"\n--- Test: Filesystem tool (list {examples_path}) ---")
            response = await session.execute(f"List the Python files in {examples_path}. Just show the filenames.")
            print(f"Response: {response}")

        print("\n" + "=" * 60)
        print("✓ Test completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
