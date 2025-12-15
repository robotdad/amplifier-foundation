# Full Workflow Example

Interactive demo showing the complete amplifier-foundation workflow.

## The Core Pattern

```python
# 1. Load and compose bundles
foundation = await load_bundle(foundation_path)
provider = await load_bundle(provider_path)
composed = foundation.compose(provider)

# 2. Prepare (resolves module sources)
prepared = await composed.prepare()

# 3. Create session and execute
session = await prepared.create_session()
async with session:
    response = await session.execute(prompt)
```

## Running

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-..."
# or
export OPENAI_API_KEY="sk-..."

# Run the demo
cd amplifier-foundation
uv run python examples/04_full_workflow/main.py
```

## Code Sections

The example is organized into clearly marked sections:

1. **FOUNDATION MECHANISM** - The essential pattern to copy
2. **APP-LAYER HELPERS** - Provider discovery, interactive selection
3. **OPTIONAL: @Mentions** - Loading files referenced in prompts
4. **OPTIONAL: Spawning** - Sub-session delegation for agents

Sections 3-4 are optional advanced features. Start with sections 1-2.
