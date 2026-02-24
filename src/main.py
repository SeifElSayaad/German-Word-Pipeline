"""
main.py
Orchestrates the full German Word Extraction & Aggregation Pipeline:
    scraper -> filter -> translator -> csv_exporter

Run locally:
    python src/main.py

Or let GitHub Actions run it every day at 07:00 Cairo time.
"""

import logging
import sys
import os

# ---------------------------------------------------------------------------
# Allow imports from src/ whether the script is run from project root or
# from inside src/
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from scraper import scrape_all
from filter import extract_advanced_words
from translator import translate_batch
from csv_exporter import export

# ---------------------------------------------------------------------------
# Configuration — tweak these to adjust behaviour
# ---------------------------------------------------------------------------
MAX_ARTICLES = 10        # max DW articles to scrape per run
MAX_TRANSLATE = 60       # max words to send to the translation API per run

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def run() -> None:
    logger.info("=== German Word Pipeline starting ===")

    # 1. Scrape
    logger.info("Step 1/4 — Scraping Deutsche Welle (max %d articles)…", MAX_ARTICLES)
    sentences = scrape_all(max_articles=MAX_ARTICLES)
    logger.info("Scraped %d sentences from %d articles.", len(sentences), MAX_ARTICLES)

    if not sentences:
        logger.error("No sentences scraped. Aborting.")
        sys.exit(1)

    # 2. Filter
    logger.info("Step 2/4 — Filtering for advanced (B1–C1) vocabulary…")
    word_context_pairs = extract_advanced_words(sentences)
    logger.info("Found %d advanced word candidates.", len(word_context_pairs))

    if not word_context_pairs:
        logger.warning("No advanced words found. Nothing to translate.")
        sys.exit(0)

    # 3. Translate (cap to MAX_TRANSLATE to stay within free-tier limits)
    batch = word_context_pairs[:MAX_TRANSLATE]
    logger.info(
        "Step 3/4 — Translating %d words via MyMemory API…", len(batch)
    )
    translated = translate_batch(batch)
    logger.info("Successfully translated %d words.", len(translated))

    if not translated:
        logger.warning("Translation returned no results. Nothing to export.")
        sys.exit(0)

    # 4. Export
    logger.info("Step 4/4 — Exporting to CSV…")
    new_count = export(translated)

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    logger.info(
        "=== Pipeline complete | "
        "Articles: %d | "
        "Candidates: %d | "
        "Translated: %d | "
        "New words added: %d ===",
        MAX_ARTICLES,
        len(word_context_pairs),
        len(translated),
        new_count,
    )


if __name__ == "__main__":
    run()
