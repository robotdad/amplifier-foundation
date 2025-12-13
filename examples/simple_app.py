#!/usr/bin/env python3
"""Simple example: Load a bundle and inspect it.

This example shows the minimal usage of amplifier-foundation:
1. Load a bundle from a local path
2. Inspect its contents
3. Get the mount plan for AmplifierSession
"""

import asyncio
from pathlib import Path

from amplifier_foundation import load_bundle


async def main() -> None:
    """Load the foundation bundle and display its contents."""
    # The foundation bundle is co-located in this package
    foundation_path = Path(__file__).parent.parent

    # Load the bundle
    print("Loading foundation bundle...")
    bundle = await load_bundle(str(foundation_path))

    # Display bundle metadata
    print(f"\nBundle: {bundle.name}")
    print(f"Version: {bundle.version}")
    print(f"Description: {bundle.description}")

    # Get the mount plan
    mount_plan = bundle.to_mount_plan()

    # Display configuration summary
    print("\n--- Mount Plan Summary ---")

    if "session" in mount_plan:
        session = mount_plan["session"]
        print("\nSession:")
        if "orchestrator" in session:
            orch = session["orchestrator"]
            if isinstance(orch, dict):
                print(f"  Orchestrator: {orch.get('module', 'unknown')}")
            else:
                print(f"  Orchestrator: {orch}")
        if "context" in session:
            ctx = session["context"]
            if isinstance(ctx, dict):
                print(f"  Context: {ctx.get('module', 'unknown')}")
            else:
                print(f"  Context: {ctx}")

    if providers := mount_plan.get("providers", []):
        print(f"\nProviders ({len(providers)}):")
        for p in providers:
            module = p.get("module", "unknown") if isinstance(p, dict) else p
            print(f"  - {module}")

    if tools := mount_plan.get("tools", []):
        print(f"\nTools ({len(tools)}):")
        for t in tools:
            module = t.get("module", "unknown") if isinstance(t, dict) else t
            print(f"  - {module}")

    if hooks := mount_plan.get("hooks", []):
        print(f"\nHooks ({len(hooks)}):")
        for h in hooks:
            module = h.get("module", "unknown") if isinstance(h, dict) else h
            print(f"  - {module}")

    if agents := mount_plan.get("agents", {}):
        print(f"\nAgents ({len(agents)}):")
        for name in sorted(agents.keys()):
            print(f"  - {name}")

    # Show instruction preview
    if instruction := bundle.get_system_instruction():
        preview = instruction[:200] + "..." if len(instruction) > 200 else instruction
        print(f"\nInstruction preview:\n{preview}")

    print("\n--- End ---")


if __name__ == "__main__":
    asyncio.run(main())
