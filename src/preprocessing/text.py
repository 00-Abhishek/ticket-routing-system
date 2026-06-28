"""Reusable preprocessing for IT support ticket text."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b")
CONTROL_CHARS_PATTERN = re.compile(r"[\r\n\t]+")
NON_WORD_PATTERN = re.compile(r"[^a-z0-9\s._:/\\-]")
STANDALONE_PUNCTUATION_PATTERN = re.compile(r"(?<=\s)[._:/\\-]+(?=\s|$)")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_ticket_text(text: object) -> str:
    """Normalize raw ticket text while preserving useful technical tokens."""
    if pd.isna(text):
        return ""

    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = normalized.lower()
    normalized = URL_PATTERN.sub(" ", normalized)
    normalized = EMAIL_PATTERN.sub(" ", normalized)
    normalized = CONTROL_CHARS_PATTERN.sub(" ", normalized)
    normalized = NON_WORD_PATTERN.sub(" ", normalized)
    normalized = STANDALONE_PUNCTUATION_PATTERN.sub(" ", normalized)
    normalized = WHITESPACE_PATTERN.sub(" ", normalized)
    return normalized.strip()


def normalize_ticket_series(series: pd.Series) -> pd.Series:
    """Apply ticket text cleaning to a pandas Series."""
    return series.apply(clean_ticket_text)
