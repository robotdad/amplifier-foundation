# Core Concepts

Mental model for Amplifier Foundation. For code examples, see [PATTERNS.md](PATTERNS.md).

## What is a Bundle?

A **Bundle** is a composable configuration unit that produces a **mount plan** for AmplifierSession.

```
Bundle → to_mount_plan() → Mount Plan → AmplifierSession
```

### Bundle Contents

| Section | Purpose |
|---------|---------|
| `bundle` | Metadata (name, version) |
| `session` | Orchestrator and context manager |
| `providers` | LLM backends |
| `tools` | Agent capabilities |
| `hooks` | Observability and control |
| `agents` | Named agent configurations |
| `context` | Context files to include |
| `instruction` | System instruction (markdown body) |

Bundles are markdown files with YAML frontmatter. See [PATTERNS.md](PATTERNS.md) for format examples.

## Composition

Bundles can be **composed** to layer configuration:

```python
result = base.compose(overlay)  # Later overrides earlier
```

### Merge Rules

| Section | Rule |
|---------|------|
| `session` | Deep merge (nested dicts merged) |
| `providers` | Merge by module ID |
| `tools` | Merge by module ID |
| `hooks` | Merge by module ID |
| `instruction` | Replace (later wins) |

**Module ID merge**: Same ID = update config, new ID = add to list.

## Mount Plan

A **mount plan** is the final configuration dict consumed by AmplifierSession.

Contains: `session`, `providers`, `tools`, `hooks`, `agents`

**Not included**: `includes` (resolved), `context` (processed separately), `instruction` (injected into context).

## Prepared Bundle

A **PreparedBundle** is a bundle ready for execution with all modules activated.

```python
bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()  # Downloads modules
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

`prepare()` downloads modules from git URLs, installs dependencies, and returns a PreparedBundle with module resolver.

## @Mention Resolution

Instructions can reference context files from composed bundles using `@namespace:path` syntax:

```markdown
See @foundation:context/guidelines.md for guidelines.
```

How it works:
1. During composition, each bundle's `base_path` is tracked by namespace (from `bundle.name`)
2. PreparedBundle resolves `@namespace:path` references against the original bundle's path
3. Content is loaded and included inline

This allows instructions to reference files from any included bundle without knowing absolute paths.

## Philosophy

### Mechanism, Not Policy

Foundation provides **mechanism** for bundle composition. It doesn't decide which bundles to use or how to configure them—those are **policy** decisions for your application.

### Text-First

- Bundles are markdown (human-readable)
- Configuration is YAML (diffable)
- No binary formats

## Next Steps

- **[API_REFERENCE.md](API_REFERENCE.md)** - API index pointing to source
- **[PATTERNS.md](PATTERNS.md)** - Common usage patterns with code examples
- **[URI_FORMATS.md](URI_FORMATS.md)** - Source URI reference
