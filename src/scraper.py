"""
scraper.py
Scrapes article text from Deutsche Welle's "Nachrichten leicht"
(simple German news) section.
"""

import logging
import time
from typing import List

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.dw.com"
LISTING_URL = "https://rss.dw.com/xml/rss-de-top"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 1.5  # polite crawl delay


def _get(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        # Use XML parser for RSS if URL contains 'rss' or 'xml'
        parser = "xml" if "rss" in url else "lxml"
        return BeautifulSoup(response.text, parser)
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def scrape_all(max_articles: int = 15) -> List[str]:
    """
    High-level entry point: scrape DW RSS feed directly.
    Extract the 'description' tag from each item as the sentence source.
    Returns a flat list of German sentences.
    """
    logger.info("Fetching RSS feed from %s", LISTING_URL)
    soup = _get(LISTING_URL)
    if not soup:
        return []

    all_sentences: List[str] = []
    items = soup.find_all("item")
    logger.info("Found %d items in RSS feed.", len(items))

    for idx, item in enumerate(items[:max_articles], start=1):
        desc = item.find("description")
        if desc and desc.text:
            text = desc.text.strip()
            # Split roughly by sentences or just append the whole description block
            if len(text) > 20:
                all_sentences.append(text)

    logger.info("Total description blocks collected: %d", len(all_sentences))
    return all_sentences

