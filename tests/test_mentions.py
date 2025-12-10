"""Tests for mention parsing and resolution."""

from amplifier_foundation.mentions.parser import parse_mentions


class TestParseMentions:
    """Tests for parse_mentions function."""

    def test_no_mentions(self) -> None:
        """Text without mentions returns empty list."""
        assert parse_mentions("Hello world") == []

    def test_simple_mention(self) -> None:
        """Simple @mention is extracted."""
        mentions = parse_mentions("Check @file.md for details")
        assert mentions == ["@file.md"]

    def test_multiple_mentions(self) -> None:
        """Multiple mentions are extracted."""
        mentions = parse_mentions("See @first.md and @second.md")
        assert set(mentions) == {"@first.md", "@second.md"}

    def test_namespaced_mention(self) -> None:
        """Namespaced @bundle:resource mention is extracted."""
        mentions = parse_mentions("Follow @foundation:philosophy")
        assert mentions == ["@foundation:philosophy"]

    def test_mention_in_code_block_excluded(self) -> None:
        """Mentions inside code blocks are excluded."""
        text = """
Check @outside.md for info.

```python
# @inside.md is code
```

More @after.md content.
"""
        mentions = parse_mentions(text)
        assert "@outside.md" in mentions
        assert "@after.md" in mentions
        assert "@inside.md" not in mentions

    def test_mention_in_inline_code_excluded(self) -> None:
        """Mentions inside inline code are excluded."""
        mentions = parse_mentions("Use `@code.md` or @real.md")
        assert mentions == ["@real.md"]

    def test_mention_with_path(self) -> None:
        """Mention with path is extracted."""
        mentions = parse_mentions("Check @docs/guide.md")
        assert mentions == ["@docs/guide.md"]

    def test_deduplication(self) -> None:
        """Duplicate mentions are deduplicated."""
        mentions = parse_mentions("See @file.md and also @file.md")
        assert mentions == ["@file.md"]
