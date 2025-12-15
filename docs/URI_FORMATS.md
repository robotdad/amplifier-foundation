# URI Formats

Complete reference for source URI formats supported by Amplifier Foundation.

## Overview

URIs specify where to load bundles and modules from. Foundation supports:

- Local paths (files and directories)
- Git URLs (HTTPS and SSH)

## Local Paths

### File Path

Load a single bundle file:

```
/path/to/bundle.md
./relative/bundle.md
~/home/bundle.md
```

Example:
```python
bundle = await load_bundle("/home/user/bundles/my-app.md")
bundle = await load_bundle("./bundles/dev.md")
```

### Directory Path

Load from a directory containing `bundle.md` or `bundle.yaml`:

```
/path/to/bundle/
./relative/bundle/
```

The loader looks for (in order):
1. `bundle.md`
2. `bundle.yaml`
3. `bundle.yml`

Example:
```python
# Loads /path/to/my-bundle/bundle.md
bundle = await load_bundle("/path/to/my-bundle")
```

### Path Resolution

- `./` and `../` are resolved relative to current working directory
- `~/` is expanded to home directory
- Absolute paths used as-is

## Git URLs

### HTTPS Format

```
git+https://github.com/org/repo@ref
git+https://gitlab.com/org/repo@ref
```

Components:
- `git+` prefix identifies git protocol
- `https://host/path` is the repository URL
- `@ref` specifies branch, tag, or commit

Examples:
```python
# Branch
bundle = await load_bundle("git+https://github.com/microsoft/amplifier-foundation-bundle@main")

# Tag
bundle = await load_bundle("git+https://github.com/org/repo@v1.0.0")

# Commit
bundle = await load_bundle("git+https://github.com/org/repo@abc123")
```

### SSH Format

For private repositories:

```
git+ssh://git@github.com/org/repo@ref
```

Example:
```python
bundle = await load_bundle("git+ssh://git@github.com/company/private-bundle@main")
```

Requires SSH key configured for the host.

### Subdirectory Access

Access bundles in subdirectories using the pip/uv standard `#subdirectory=` format:

```
git+https://github.com/org/monorepo@main#subdirectory=path/to/bundle
```

Example:
```python
# Bundle at bundles/dev in the repo
bundle = await load_bundle("git+https://github.com/org/repo@main#subdirectory=bundles/dev")
```

## Module Sources

In bundle configuration, modules specify their source:

```yaml
providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      default_model: claude-sonnet-4-5

tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
```

## URI Parsing

Use `parse_uri()` to inspect URIs:

```python
from amplifier_foundation import parse_uri

parsed = parse_uri("git+https://github.com/org/repo@main#subdirectory=bundles/dev")
print(parsed.scheme)     # "git+https"
print(parsed.host)       # "github.com"
print(parsed.path)       # "/org/repo"
print(parsed.ref)        # "main"
print(parsed.subpath)    # "bundles/dev"
```

## Resolution Process

1. **Parse URI** - Identify scheme and components
2. **Resolve source** - Clone repo or access local path
3. **Navigate to subpath** - If specified
4. **Find bundle file** - `bundle.md`, `bundle.yaml`
5. **Parse and load** - Create Bundle object

## Caching

Git sources are cached to avoid repeated downloads:

```python
from amplifier_foundation import BundleRegistry, DiskCache
from pathlib import Path

cache = DiskCache(Path("~/.amplifier/cache").expanduser())
registry = BundleRegistry(cache=cache)

# First load: clones repository
bundle = await registry.load("git+https://github.com/org/repo@main")

# Subsequent loads: uses cached clone
bundle = await registry.load("git+https://github.com/org/repo@main")
```

## Common Issues

### Authentication Errors

For private repos via HTTPS:
- Set `GIT_USERNAME` and `GIT_PASSWORD` environment variables
- Or use SSH format with configured key

For SSH:
- Ensure SSH key is added to agent: `ssh-add ~/.ssh/id_rsa`
- Verify host key: `ssh -T git@github.com`

### Network Issues

Git operations may fail due to:
- Network connectivity
- Firewall restrictions
- Repository access permissions

Use local paths during development to avoid network dependencies.

### Missing Ref

If the specified ref doesn't exist:

```
BundleLoadError: Could not find ref 'v2.0.0' in repository
```

Verify the ref exists with `git ls-remote`.
