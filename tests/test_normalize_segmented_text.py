"""Tests for _normalize_segmented_text (pure string logic, no HA fixtures)."""
from tinysegmenter import TinySegmenter

from custom_components.jp_segmenter_assistant.conversation import (
    _normalize_segmented_text,
    _tokenize_text,
)


def test_merge_contiguous_hiragana():
    """Two adjacent hiragana-only tokens merge into one chunk."""
    assert _normalize_segmented_text(["み", "ゆき"]) == "みゆき"


def test_particle_blocks_hiragana_merge_on_both_sides():
    """A particle token between two hiragana tokens prevents merging in
    either direction, even though without it they would merge (see
    test_merge_contiguous_hiragana above)."""
    assert _normalize_segmented_text(["み", "の", "ゆき"]) == "み の ゆき"


def test_merge_kanji_tail_and_hiragana_name():
    """Kanji-tail token + following hiragana (len >= 2, not a particle)
    merges into a name-like token."""
    assert _normalize_segmented_text(["中島", "みゆき"]) == "中島みゆき"


def test_single_hiragana_char_does_not_merge_into_name():
    """The len(token) >= 2 guard prevents a single hiragana char from
    merging into the preceding kanji-tail token."""
    assert _normalize_segmented_text(["中島", "み"]) == "中島 み"


def test_empty_and_whitespace_tokens_are_filtered():
    """Empty/whitespace-only tokens are dropped; remaining tokens are
    joined with single spaces."""
    assert _normalize_segmented_text(["", "  ", "犬", "\t", "猫"]) == "犬 猫"


def test_apostrophe_rejoin():
    """A latin letter token followed by an apostrophe-prefixed token is
    rejoined without the space (e.g. 'B'z', not 'B 'z')."""
    assert _normalize_segmented_text(["B", "'z"]) == "B'z"


def test_end_to_end_readme_example():
    """The project's own documented example: tokenizing and normalizing
    "B'zのLOVE PHANTOMを流して" should keep "B'z" and "LOVE PHANTOM" intact
    as contiguous substrings."""
    segmenter = TinySegmenter()
    tokenize = getattr(segmenter, "tokenize", None) or getattr(segmenter, "segment")
    tokens = tokenize("B'zのLOVE PHANTOMを流して")

    result = _normalize_segmented_text(tokens)

    assert "B'z" in result
    assert "LOVE PHANTOM" in result

    # Also confirm the equivalent path via _tokenize_text produces the same
    # tokens (it just dispatches to tokenize/segment on the module-level
    # segmenter, which is a real TinySegmenter instance).
    assert _tokenize_text("B'zのLOVE PHANTOMを流して") == tokens
