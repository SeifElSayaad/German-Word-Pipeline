"""
translator.py
Translates a list of German words to English using the free MyMemory API.
No API key required for up to ~1000 words/day.
API docs: https://mymemory.translated.net/doc/spec.php
"""

import logging
import time
from typing import Dict, List, Tuple

import requests

logger = logging.getLogger(__name__)

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
LANG_PAIR = "de|en"
DELAY_BETWEEN_CALLS = 0.5   # seconds — stay well within rate limits
REQUEST_TIMEOUT = 8          # seconds


def translate_word(word: str) -> str:
    """
    Translate a single German word to English via MyMemory API.
    Returns the English translation string, or an empty string on failure.
    """
    params = {"q": word, "langpair": LANG_PAIR}
    try:
        resp = requests.get(MYMEMORY_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        translation = data.get("responseData", {}).get("translatedText", "")
        # MyMemory returns "INVALID TRANSLATION" on failure
        if translation and "INVALID" not in translation.upper():
            return translation.strip()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Translation failed for '%s': %s", word, exc)
    return ""


def translate_batch(
    word_context_pairs: List[Tuple[str, str]],
) -> List[Dict[str, str]]:
    """
    Translate a list of (german_word, context_sentence) pairs.

    Returns a list of dicts:
        [{"german": ..., "english": ..., "context": ...}, ...]

    Words that fail translation are skipped.
    """
    results = []
    total = len(word_context_pairs)

    for idx, (word, context) in enumerate(word_context_pairs, start=1):
        logger.info("[%d/%d] Translating: %s", idx, total, word)
        english = translate_word(word)
        if english:
            results.append(
                {"german": word, "english": english, "context": context}
            )
        if idx < total:
            time.sleep(DELAY_BETWEEN_CALLS)

    logger.info(
        "Translated %d/%d words successfully.", len(results), total
    )
    return results
