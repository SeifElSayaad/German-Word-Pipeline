"""
tests/test_scraper.py
Unit tests for scraper.py — all HTTP calls are mocked.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import MagicMock, patch
import scraper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_LISTING_HTML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item><link>https://www.dw.com/de/nachrichten/a-12345678</link></item>
    <item><link>https://www.dw.com/de/thema/a-23456789</link></item>
    <item><link>https://external.com/link</link></item>
  </channel>
</rss>
"""

MOCK_ARTICLE_HTML = """
<html><body>
  <div class="rich-text">
    <p>Die Bundesregierung hat heute eine wichtige Entscheidung getroffen.</p>
    <p>Das Parlament diskutiert über die neue Klimapolitik.</p>
    <p>Short.</p>
  </div>
</body></html>
"""


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@patch("scraper.requests.get")
def test_get_article_links_returns_urls(mock_get):
    mock_get.return_value = _make_mock_response(MOCK_LISTING_HTML)
    links = scraper.get_article_links(max_articles=5)
    assert len(links) >= 1
    for link in links:
        assert link.startswith("https://www.dw.com")
        assert "/a-" in link


@patch("scraper.requests.get")
def test_get_article_links_respects_max(mock_get):
    # Return the same listing page with 2 valid links
    mock_get.return_value = _make_mock_response(MOCK_LISTING_HTML)
    links = scraper.get_article_links(max_articles=1)
    assert len(links) <= 1


@patch("scraper.requests.get")
def test_scrape_article_sentences_extracts_paragraphs(mock_get):
    mock_get.return_value = _make_mock_response(MOCK_ARTICLE_HTML)
    sentences = scraper.scrape_article_sentences("https://www.dw.com/de/fake/a-99999")
    # Must return non-empty list of strings
    assert isinstance(sentences, list)
    assert len(sentences) >= 1
    # Short text (<= 20 chars) should be skipped
    for s in sentences:
        assert len(s) > 20


@patch("scraper.requests.get")
def test_scrape_article_returns_empty_on_no_body(mock_get):
    mock_get.return_value = _make_mock_response("<html><body>No article here.</body></html>")
    sentences = scraper.scrape_article_sentences("https://www.dw.com/de/fake/a-11111")
    assert sentences == []


@patch("scraper.requests.get")
def test_scrape_article_returns_empty_on_http_error(mock_get):
    import requests
    mock_get.side_effect = requests.RequestException("timeout")
    sentences = scraper.scrape_article_sentences("https://www.dw.com/de/fake/a-22222")
    assert sentences == []


@patch("scraper.requests.get")
@patch("scraper.time.sleep", return_value=None)
def test_scrape_all_returns_flat_sentence_list(mock_sleep, mock_get):
    mock_get.return_value = _make_mock_response(MOCK_ARTICLE_HTML)
    # Patch get_article_links to return two fake URLs
    with patch("scraper.get_article_links", return_value=[
        "https://www.dw.com/de/fake/a-11111",
        "https://www.dw.com/de/fake/a-22222",
    ]):
        sentences = scraper.scrape_all(max_articles=2)
    assert isinstance(sentences, list)
    assert len(sentences) > 0
