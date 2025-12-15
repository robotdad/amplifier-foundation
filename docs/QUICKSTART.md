# Quickstart

Get started with Amplifier Foundation in 5 minutes.

## Installation

```bash
pip install amplifier-foundation
```

Or with uv:

```bash
uv add amplifier-foundation
```

## Hello Bundle

```python
import asyncio
from amplifier_foundation import Bundle, load_bundle

async def main():
    # Create a simple bundle inline
    bundle = Bundle(
        name="my-bundle",
        version="1.0.0",
        session={
            "orchestrator": {"module": "loop-streaming"},
            "context": {"module": "context-simple"},
        },
        providers=[
            {
                "module": "provider-anthropic",
                "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
                "config": {"default_model": "claude-sonnet-4-5"},
            }
        ],
    )

    # See what's configured
    mount_plan = bundle.to_mount_plan()
    print(f"Providers: {len(mount_plan['providers'])}")

asyncio.run(main())
```

## Load from File

Most bundles live in files. Create `bundle.md`:

```markdown
---
bundle:
  name: my-app
  version: 1.0.0

session:
  orchestrator:
    module: loop-streaming
  context:
    module: context-simple

providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      default_model: claude-sonnet-4-5

tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
---

You are a helpful assistant with file access.
```

Then load it:

```python
from amplifier_foundation import load_bundle

bundle = await load_bundle("/path/to/bundle.md")
print(f"Loaded: {bundle.name} v{bundle.version}")
```

## Execute with LLM

The full workflow: load → prepare → execute.

```python
import os
from amplifier_foundation import load_bundle

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "your-key"

# Load and prepare
bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()

# Create session and execute
async with prepared.create_session() as session:
    response = await session.execute("Hello! What can you do?")
    print(response)
```

## Bundle Composition

Combine bundles to layer configuration:

```python
from amplifier_foundation import Bundle

# Base configuration
base = Bundle(
    name="base",
    version="1.0.0",
    providers=[{"module": "provider-mock", "config": {"delay": 0}}],
)

# Dev overlay
dev = Bundle(
    name="dev",
    version="1.0.0",
    providers=[{"module": "provider-mock", "config": {"debug": True}}],
)

# Compose: base + dev
result = base.compose(dev)
# Result has debug=True (dev config merged into base)
```

## Next Steps

- **[CONCEPTS.md](CONCEPTS.md)** - Understand bundles, composition, and mount plans
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[PATTERNS.md](PATTERNS.md)** - Common usage patterns
- **[../examples/](../examples/)** - Working code examples
