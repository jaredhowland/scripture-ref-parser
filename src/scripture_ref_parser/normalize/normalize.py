"""Normalizer stage: maps book names to canonical OSIS keys."""

import re
from typing import Literal

from scripture_ref_parser.data.loader import load_canon_index
from scripture_ref_parser.types import NormalizedBook


def _clean_name(name: str) -> str:
    """Clean a book name for lookup: lowercase, remove punctuation/spaces."""
    # Remove periods and extra spaces, lowercase
    cleaned = re.sub(r"[.\s]+", "", name.lower())
    return cleaned


def normalize_book(
    name: str,
    mode: Literal["loose", "strict"] = "loose",
) -> NormalizedBook:
    """Normalize a book name to its canonical OSIS key.

    Args:
        name: Book name or abbreviation to normalize
        mode: "strict" for exact matches only, "loose" for fuzzy matching

    Returns:
        NormalizedBook with key (or None if not found in strict mode)
    """
    index = load_canon_index()
    cleaned = _clean_name(name)

    # Direct lookup
    if cleaned in index:
        return NormalizedBook(key=index[cleaned], mode=mode)

    # Strict mode: return None for unknown
    if mode == "strict":
        return NormalizedBook(key=None, mode=mode)

    # Loose mode: try fuzzy matching (implemented in Task 7)
    return _fuzzy_match(name, index, mode)


def _fuzzy_match(
    name: str,
    index: dict[str, str],
    mode: Literal["loose", "strict"],
) -> NormalizedBook:
    """Perform fuzzy matching for loose mode (placeholder)."""
    # Will be implemented in Task 7
    return NormalizedBook(key=None, mode=mode, candidates=[])
