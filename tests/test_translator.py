"""
tests/test_translator.py
Unit tests for translator.py — MyMemory API calls are mocked.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import MagicMock, patch
import translator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(translated_text: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "responseData": {"translatedText": translated_text},
        "responseStatus": 200,
    }
    return mock_resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@patch("translator.requests.get")
def test_translate_word_returns_english(mock_get):
    mock_get.return_value = _mock_response("responsibility")
    result = translator.translate_word("Verantwortung")
    assert result == "responsibility"


@patch("translator.requests.get")
def test_translate_word_returns_empty_on_invalid(mock_get):
    mock_get.return_value = _mock_response("INVALID TRANSLATION")
    result = translator.translate_word("xyzxyz")
    assert result == ""


@patch("translator.requests.get")
def test_translate_word_returns_empty_on_http_error(mock_get):
    import requests
    mock_get.side_effect = requests.RequestException("network error")
    result = translator.translate_word("Verantwortung")
    assert result == ""


@patch("translator.requests.get")
@patch("translator.time.sleep", return_value=None)
def test_translate_batch_returns_correct_structure(mock_sleep, mock_get):
    mock_get.return_value = _mock_response("population")
    pairs = [("Bevölkerung", "Die Bevölkerung wächst.")]
    results = translator.translate_batch(pairs)
    assert len(results) == 1
    assert results[0]["german"] == "Bevölkerung"
    assert results[0]["english"] == "population"
    assert "context" in results[0]


@patch("translator.requests.get")
@patch("translator.time.sleep", return_value=None)
def test_translate_batch_skips_failed_translations(mock_sleep, mock_get):
    mock_get.return_value = _mock_response("INVALID TRANSLATION")
    pairs = [
        ("Bevölkerung", "Die Bevölkerung wächst."),
        ("Regierung", "Die Regierung entscheidet."),
    ]
    results = translator.translate_batch(pairs)
    # All translations invalid → empty results
    assert results == []


@patch("translator.requests.get")
@patch("translator.time.sleep", return_value=None)
def test_translate_batch_handles_empty_input(mock_sleep, mock_get):
    results = translator.translate_batch([])
    assert results == []
    mock_get.assert_not_called()
