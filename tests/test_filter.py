"""
tests/test_filter.py
Unit tests for filter.py word-filtering logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch
import filter as f   # noqa: F401 — 'filter' shadows the builtin, use alias


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

A1_WORDS = {"sein", "haben", "werden", "und", "oder", "der", "die", "das", "ist", "nicht"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_tokenise_splits_correctly():
    tokens = f.tokenise("Die Bundesregierung hat entschieden.")
    assert "bundesregierung" in tokens
    assert "entschieden" in tokens
    # Numbers and punctuation should not appear
    for t in tokens:
        assert t.isalpha() or any(c in "äöüß" for c in t)


def test_tokenise_handles_umlauts():
    tokens = f.tokenise("Überzeugung und Müdigkeit.")
    assert "überzeugung" in tokens
    assert "müdigkeit" in tokens
    # 'und' is short but should still tokenise
    assert "und" in tokens


def test_is_advanced_rejects_short_words():
    assert f.is_advanced("ab", A1_WORDS) is False
    assert f.is_advanced("und", A1_WORDS) is False


def test_is_advanced_rejects_basic_words():
    assert f.is_advanced("sein", A1_WORDS) is False
    assert f.is_advanced("haben", A1_WORDS) is False


def test_is_advanced_accepts_complex_words():
    assert f.is_advanced("bundesregierung", A1_WORDS) is True
    assert f.is_advanced("klimapolitik", A1_WORDS) is True


@patch("filter.load_basic_words", return_value=A1_WORDS)
def test_extract_advanced_words_filters_basic(mock_load):
    sentences = [
        "Die Bundesregierung hat heute entschieden.",
        "Das ist nicht gut.",
    ]
    result = f.extract_advanced_words(sentences)
    words = [w for w, _ in result]
    # Basic A1 words should be absent
    for w in words:
        assert w not in A1_WORDS
    # Complex word should be present
    assert "bundesregierung" in words


@patch("filter.load_basic_words", return_value=A1_WORDS)
def test_extract_advanced_words_deduplicates(mock_load):
    sentences = [
        "Bundesregierung ist wichtig.",
        "Bundesregierung wurde gewählt.",
    ]
    result = f.extract_advanced_words(sentences)
    words = [w for w, _ in result]
    # 'bundesregierung' should appear only once
    assert words.count("bundesregierung") == 1


@patch("filter.load_basic_words", return_value=A1_WORDS)
def test_extract_advanced_words_caps_at_max(mock_load):
    # Build >MAX_WORDS unique long words by brute-force
    sentences = [f"Wort{'a' * (i + 6)} ist komplex." for i in range(200)]
    result = f.extract_advanced_words(sentences)
    assert len(result) <= f.MAX_WORDS


@patch("filter.load_basic_words", return_value=set())
def test_extract_returns_empty_on_no_text(mock_load):
    result = f.extract_advanced_words([])
    assert result == []
