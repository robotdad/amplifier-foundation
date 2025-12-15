# URI Formats

Quick reference for source URIs. For complete details, see `parse_uri()` docstring in `paths/resolution.py`.

## Supported Formats

| Format | Example |
|--------|---------|
| **Local file** | `/path/to/bundle.md`, `./relative.md` |
| **Local directory** | `/path/to/bundle/` (finds `bundle.md` inside) |
| **Git HTTPS** | `git+https://github.com/org/repo@main` |
| **Git SSH** | `git+ssh://git@github.com/org/repo@main` |
| **Subdirectory** | `git+https://github.com/org/repo@main#subdirectory=path/to/bundle` |

## Common Examples

```python
from amplifier_foundation import load_bundle

# Local
bundle = await load_bundle("./bundles/dev.md")

# Git with branch
bundle = await load_bundle("git+https://github.com/microsoft/amplifier-foundation-bundle@main")

# Git with subdirectory
bundle = await load_bundle("git+https://github.com/org/repo@main#subdirectory=bundles/dev")
```

## Parsing URIs

```python
from amplifier_foundation import parse_uri, ParsedURI

parsed = parse_uri("git+https://github.com/org/repo@main#subdirectory=bundles/dev")
# parsed.scheme = "git+https"
# parsed.host = "github.com"
# parsed.path = "/org/repo"
# parsed.ref = "main"
# parsed.subpath = "bundles/dev"
```

## Reading the Source

For complete URI parsing logic:

```bash
python -c "from amplifier_foundation import parse_uri; help(parse_uri)"
```

Or read `amplifier_foundation/paths/resolution.py` directly.
