"""Tests for _tokenize_text dispatch logic across TinySegmenter variants."""
import pytest

import custom_components.jp_segmenter_assistant.conversation as conversation_module
from custom_components.jp_segmenter_assistant.conversation import _tokenize_text


def test_tokenize_text_uses_tokenize_method(monkeypatch):
    class FakeSegmenter:
        def tokenize(self, text):
            return ["fake", "tokenize", "result"]

    monkeypatch.setattr(conversation_module, "segmenter", FakeSegmenter())

    assert _tokenize_text("anything") == ["fake", "tokenize", "result"]


def test_tokenize_text_uses_segment_method(monkeypatch):
    class FakeSegmenter:
        def segment(self, text):
            return ["fake", "segment", "result"]

    monkeypatch.setattr(conversation_module, "segmenter", FakeSegmenter())

    assert _tokenize_text("anything") == ["fake", "segment", "result"]


def test_tokenize_text_raises_when_neither_method_exists(monkeypatch):
    class FakeSegmenter:
        pass

    monkeypatch.setattr(conversation_module, "segmenter", FakeSegmenter())

    with pytest.raises(AttributeError):
        _tokenize_text("anything")
