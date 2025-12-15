# Amplifier Foundation Examples

**Learning Path**: Follow numbered examples in order for best understanding.

## Examples

### 01_load_and_inspect.py
**Teachable Moment**: `load_bundle()` + `to_mount_plan()`

Load a bundle from any source and inspect its contents.

```bash
uv run python examples/01_load_and_inspect.py
```

### 02_composition.py
**Teachable Moment**: How `bundle.compose(overlay)` merges configuration

Understand the merge rules for session, providers, tools, and instruction.

```bash
uv run python examples/02_composition.py
```

### 03_sources_and_registry.py
**Teachable Moment**: Source formats and `BundleRegistry`

Load from git URLs and use registry for named bundle management.

```bash
uv run python examples/03_sources_and_registry.py
```

### 04_full_workflow/
**Teachable Moment**: `prepare()` → `create_session()` → `execute()`

Complete interactive demo with provider selection and LLM execution.

```bash
# Set API key first
export ANTHROPIC_API_KEY="sk-..."

uv run python examples/04_full_workflow/main.py
```

## Running Examples

All examples run from the `amplifier-foundation` directory:

```bash
cd amplifier-foundation
uv run python examples/<example>.py
```

## Learning Philosophy

Each example teaches ONE concept:
- **01**: Loading bundles
- **02**: Composition rules
- **03**: Source formats and registry
- **04**: Full execution workflow

For deeper understanding, see the code comments explaining the "why" behind each pattern.
