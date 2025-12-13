# Amplifier Foundation Examples

Working examples demonstrating bundle loading and composition.

## Examples

### simple_app.py

Minimal example showing how to load a bundle and inspect its contents.

```bash
cd amplifier-foundation
uv run python examples/simple_app.py
```

### load_remote_bundle.py

Loading bundles from remote sources (Git, HTTP, Zip).

```bash
uv run python examples/load_remote_bundle.py
```

### compose_bundles.py

Bundle composition patterns: declarative includes, imperative compose(), and composition rules.

```bash
uv run python examples/compose_bundles.py
```

### end_to_end/

Interactive demo: Load foundation → Select provider → Enter prompt → Execute via AmplifierSession.

```bash
uv run python examples/end_to_end/main.py
```

See [end_to_end/README.md](end_to_end/README.md) for detailed usage and prerequisites.

## Running Examples

All examples can be run from the `amplifier-foundation` directory:

```bash
cd amplifier-foundation
uv run python examples/<example_name>.py
```
