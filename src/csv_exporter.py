"""
csv_exporter.py
Writes translated German vocabulary to Anki-compatible CSV files.

Daily file  : data/output/german_words_YYYY-MM-DD.csv
Master file : data/output/all_words.csv  (deduplicated across all runs)
"""

import csv
import logging
import os
from datetime import date
from typing import Dict, List

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
_ROOT = os.path.join(os.path.dirname(__file__), "..")
OUTPUT_DIR = os.path.join(_ROOT, "data", "output")
MASTER_FILE = os.path.join(OUTPUT_DIR, "all_words.csv")

FIELDNAMES = ["German", "English", "Context", "Date"]


def _ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _load_existing_german_words() -> set:
    """Return the set of German words already stored in the master CSV."""
    if not os.path.exists(MASTER_FILE):
        return set()
    with open(MASTER_FILE, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {row["German"].strip().lower() for row in reader if row.get("German")}


def _build_rows(
    translated: List[Dict[str, str]],
    today: str,
    existing: set,
) -> List[Dict[str, str]]:
    """Filter out already-known words and build row dicts for new words."""
    rows = []
    for entry in translated:
        word = entry["german"].strip().lower()
        if word in existing:
            continue
        rows.append(
            {
                "German": entry["german"],
                "English": entry["english"],
                "Context": entry["context"],
                "Date": today,
            }
        )
        existing.add(word)   # prevent duplicates within the same run
    return rows


def _write_csv(path: str, rows: List[Dict[str, str]], append: bool = False) -> None:
    """Write (or append) rows to a CSV file."""
    mode = "a" if append else "w"
    write_header = not (append and os.path.exists(path))
    with open(path, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def export(translated: List[Dict[str, str]]) -> int:
    """
    Export translated words to CSV files.

    Args:
        translated: list of dicts with keys 'german', 'english', 'context'

    Returns:
        Number of *new* words written (0 if all were already in master).
    """
    _ensure_output_dir()
    today = date.today().isoformat()
    existing = _load_existing_german_words()

    new_rows = _build_rows(translated, today, existing)

    if not new_rows:
        logger.info("No new words to export (all already in master).")
        return 0

    # Daily snapshot
    daily_path = os.path.join(OUTPUT_DIR, f"german_words_{today}.csv")
    _write_csv(daily_path, new_rows, append=False)
    logger.info("Daily CSV written: %s (%d words)", daily_path, len(new_rows))

    # Append to master
    _write_csv(MASTER_FILE, new_rows, append=True)
    logger.info("Master CSV updated: %s", MASTER_FILE)

    return len(new_rows)
