"""
tests/test_csv_exporter.py
Unit tests for csv_exporter.py — uses temporary directories (no real output/ writes).
"""

import csv
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import csv_exporter


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_WORDS = [
    {"german": "Verantwortung", "english": "responsibility",
     "context": "Die Regierung trägt Verantwortung."},
    {"german": "Bevölkerung", "english": "population",
     "context": "Die Bevölkerung wächst schnell."},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_export_creates_daily_and_master_csv():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(csv_exporter, "OUTPUT_DIR", tmp), \
             patch.object(csv_exporter, "MASTER_FILE", os.path.join(tmp, "all_words.csv")):
            count = csv_exporter.export(SAMPLE_WORDS)

    assert count == 2


def test_export_csv_has_correct_headers():
    with tempfile.TemporaryDirectory() as tmp:
        master = os.path.join(tmp, "all_words.csv")
        with patch.object(csv_exporter, "OUTPUT_DIR", tmp), \
             patch.object(csv_exporter, "MASTER_FILE", master):
            csv_exporter.export(SAMPLE_WORDS)

        rows = _read_csv(master)
        assert set(rows[0].keys()) == {"German", "English", "Context", "Date"}


def test_export_deduplicates_on_second_run():
    with tempfile.TemporaryDirectory() as tmp:
        master = os.path.join(tmp, "all_words.csv")
        with patch.object(csv_exporter, "OUTPUT_DIR", tmp), \
             patch.object(csv_exporter, "MASTER_FILE", master):
            # First run
            csv_exporter.export(SAMPLE_WORDS)
            # Second run with the same words
            count_second = csv_exporter.export(SAMPLE_WORDS)

        assert count_second == 0  # nothing new to add
        rows = _read_csv(master)
        german_words = [r["German"].lower() for r in rows]
        assert german_words.count("verantwortung") == 1


def test_export_appends_new_words_on_second_run():
    extra = [{"german": "Klimapolitik", "english": "climate policy",
               "context": "Klimapolitik ist wichtig."}]
    with tempfile.TemporaryDirectory() as tmp:
        master = os.path.join(tmp, "all_words.csv")
        with patch.object(csv_exporter, "OUTPUT_DIR", tmp), \
             patch.object(csv_exporter, "MASTER_FILE", master):
            csv_exporter.export(SAMPLE_WORDS)
            count_second = csv_exporter.export(extra)

        rows = _read_csv(master)
        assert count_second == 1
        assert len(rows) == 3   # 2 original + 1 new


def test_export_returns_zero_on_empty_input():
    with tempfile.TemporaryDirectory() as tmp:
        master = os.path.join(tmp, "all_words.csv")
        with patch.object(csv_exporter, "OUTPUT_DIR", tmp), \
             patch.object(csv_exporter, "MASTER_FILE", master):
            count = csv_exporter.export([])
    assert count == 0
