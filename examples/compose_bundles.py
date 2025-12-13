#!/usr/bin/env python3
"""Example: Compose bundles together.

This example demonstrates bundle composition:
1. Declarative composition via includes:
2. Imperative composition via compose()
3. Creating provider overlays
4. Understanding composition rules
"""

import asyncio
from pathlib import Path

from amplifier_foundation import Bundle
from amplifier_foundation import load_bundle


def print_bundle_summary(bundle: Bundle, title: str) -> None:
    """Print a summary of bundle contents."""
    print(f"\n--- {title} ---")
    print(f"Name: {bundle.name}")
    print(f"Version: {bundle.version}")

    mount_plan = bundle.to_mount_plan()

    if providers := mount_plan.get("providers", []):
        print(f"Providers: {[p.get('module', p) if isinstance(p, dict) else p for p in providers]}")

    if tools := mount_plan.get("tools", []):
        print(f"Tools: {[t.get('module', t) if isinstance(t, dict) else t for t in tools]}")

    if hooks := mount_plan.get("hooks", []):
        print(f"Hooks: {[h.get('module', h) if isinstance(h, dict) else h for h in hooks]}")


async def imperative_composition() -> None:
    """Compose bundles using the compose() method."""
    print("=" * 60)
    print("Imperative Composition with compose()")
    print("=" * 60)

    # Load the foundation bundle
    foundation_path = Path(__file__).parent.parent
    foundation = await load_bundle(str(foundation_path), auto_include=False)

    print_bundle_summary(foundation, "Foundation (base)")

    # Create a provider overlay bundle programmatically
    provider_bundle = Bundle(
        name="my-provider",
        version="1.0.0",
        providers=[
            {
                "module": "provider-anthropic",
                "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
                "config": {
                    "default_model": "claude-sonnet-4-5",
                    "api_key_env": "ANTHROPIC_API_KEY",
                },
            }
        ],
    )

    print_bundle_summary(provider_bundle, "Provider Overlay")

    # Compose: foundation + provider
    # Later bundles override earlier ones
    composed = foundation.compose(provider_bundle)

    print_bundle_summary(composed, "Composed Result")


async def composition_rules_demo() -> None:
    """Demonstrate how different sections are merged."""
    print("\n" + "=" * 60)
    print("Composition Rules Demo")
    print("=" * 60)

    # Base bundle with some configuration
    base = Bundle(
        name="base",
        version="1.0.0",
        session={
            "orchestrator": {"module": "loop-basic"},
            "context": {"module": "context-simple", "config": {"max_tokens": 100000}},
        },
        providers=[
            {"module": "provider-mock", "config": {"debug": False}},
        ],
        tools=[
            {"module": "tool-filesystem"},
            {"module": "tool-bash"},
        ],
        instruction="Base instructions.",
    )

    # Overlay that customizes configuration
    overlay = Bundle(
        name="overlay",
        version="1.0.0",
        session={
            # Deep merge: this will update context.config.max_tokens
            "context": {"config": {"max_tokens": 200000, "auto_compact": True}},
        },
        providers=[
            # Merge by module ID: updates provider-mock's config
            {"module": "provider-mock", "config": {"debug": True}},
            # Adds new provider
            {"module": "provider-anthropic", "config": {"default_model": "claude-sonnet-4-5"}},
        ],
        tools=[
            # Adds new tool (doesn't duplicate existing)
            {"module": "tool-web"},
        ],
        instruction="Overlay instructions.",  # Replaces base instruction
    )

    print("\n--- Base Bundle ---")
    print(f"Session: {base.session}")
    print(f"Providers: {base.providers}")
    print(f"Tools: {base.tools}")
    print(f"Instruction: {base.instruction}")

    print("\n--- Overlay Bundle ---")
    print(f"Session: {overlay.session}")
    print(f"Providers: {overlay.providers}")
    print(f"Tools: {overlay.tools}")
    print(f"Instruction: {overlay.instruction}")

    # Compose
    result = base.compose(overlay)

    print("\n--- Composed Result ---")
    print(f"Session: {result.session}")
    print(f"Providers: {result.providers}")
    print(f"Tools: {result.tools}")
    print(f"Instruction: {result.instruction}")

    # Explain the rules
    print("\n--- Composition Rules Applied ---")
    print("1. session: Deep merge (context.config merged, max_tokens updated)")
    print("2. providers: Merge by module (provider-mock config updated, provider-anthropic added)")
    print("3. tools: Merge by module (tool-web added, others preserved)")
    print("4. instruction: Later replaces earlier")


async def multi_layer_composition() -> None:
    """Compose multiple bundles in layers."""
    print("\n" + "=" * 60)
    print("Multi-Layer Composition")
    print("=" * 60)

    # Layer 1: Core tools
    core = Bundle(
        name="core",
        version="1.0.0",
        tools=[
            {"module": "tool-filesystem"},
            {"module": "tool-bash"},
        ],
    )

    # Layer 2: Add web capabilities
    web = Bundle(
        name="web",
        version="1.0.0",
        tools=[
            {"module": "tool-web"},
            {"module": "tool-search"},
        ],
    )

    # Layer 3: Add provider
    provider = Bundle(
        name="provider",
        version="1.0.0",
        providers=[
            {"module": "provider-anthropic", "config": {"default_model": "claude-sonnet-4-5"}},
        ],
    )

    # Layer 4: Project-specific customization
    project = Bundle(
        name="my-project",
        version="1.0.0",
        description="My project configuration",
        hooks=[
            {"module": "hooks-logging", "config": {"level": "info"}},
        ],
        instruction="You are a helpful assistant for my project.",
    )

    # Compose all layers
    result = core.compose(web, provider, project)

    print_bundle_summary(result, "Final Composed Bundle")

    # Get mount plan for AmplifierSession
    mount_plan = result.to_mount_plan()
    print("\nMount plan ready for AmplifierSession.create()")
    print(f"Total providers: {len(mount_plan.get('providers', []))}")
    print(f"Total tools: {len(mount_plan.get('tools', []))}")
    print(f"Total hooks: {len(mount_plan.get('hooks', []))}")


async def main() -> None:
    """Run all composition examples."""
    # Example 1: Imperative composition
    await imperative_composition()

    # Example 2: Composition rules
    await composition_rules_demo()

    # Example 3: Multi-layer composition
    await multi_layer_composition()

    print("\n" + "=" * 60)
    print("Composition examples complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
