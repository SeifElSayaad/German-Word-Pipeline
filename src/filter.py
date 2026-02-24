"""
filter.py
Tokenises German sentences and returns only B1–B2 level vocabulary:
- Strips punctuation, lowercases, removes numbers
- Removes words in the bundled A1/A2 basic-word list
- Removes words that are too short (< 5 chars, usually trivial)
- Deduplicates and pairs each word with its best context sentence
"""

import logging
import re
import os
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Path to bundled basic-word list (A1/A2)
# --------------------------------------------------------------------------- #
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BASIC_WORDS_PATH = os.path.join(_DATA_DIR, "basic_words_a1a2.txt")

# Minimum character length to keep a word (filters out short common words)
MIN_WORD_LENGTH = 5

# Maximum words to return per run (keeps translation API usage in check)
MAX_WORDS = 80


def load_basic_words() -> set:
    """Load the A1/A2 basic word list from disk into a set (lowercase)."""
    if not os.path.exists(BASIC_WORDS_PATH):
        logger.warning("Basic word list not found at %s — filtering disabled.", BASIC_WORDS_PATH)
        return set()
    with open(BASIC_WORDS_PATH, encoding="utf-8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    logger.info("Loaded %d basic words for filtering.", len(words))
    return words


def tokenise(sentence: str) -> List[str]:
    """
    Split a sentence into lowercase word tokens, stripping punctuation
    and numbers.
    """
    # Keep only letters (including German umlauts) and word boundaries
    tokens = re.findall(r"[a-züöäßÄÖÜ]{2,}", sentence, re.IGNORECASE)
    return [t.lower() for t in tokens]


def is_advanced(word: str, basic_words: set) -> bool:
    """Return True if the word qualifies as B1–B2 level vocabulary."""
    if len(word) < MIN_WORD_LENGTH:
        return False
    if word in basic_words:
        return False
    return True


def extract_advanced_words(
    sentences: List[str],
) -> List[Tuple[str, str]]:
    """
    Given a list of German sentences, return a list of
    (word, context_sentence) tuples for unique B1–B2 words.

    Words are sorted by length descending (longer = more complex).
    Result capped at MAX_WORDS entries.
    """
    basic_words = load_basic_words()
    seen: Dict[str, str] = {}  # word → first sentence it appeared in

    for sentence in sentences:
        tokens = tokenise(sentence)
        for word in tokens:
            if word not in seen and is_advanced(word, basic_words):
                seen[word] = sentence  # store original-case sentence

    # Sort by word length descending (heuristic for complexity)
    ranked = sorted(seen.items(), key=lambda kv: len(kv[0]), reverse=True)
    result = ranked[:MAX_WORDS]

    logger.info(
        "Extracted %d advanced (B1–B2) words from %d sentences.",
        len(result),
        len(sentences),
    )
    return result
