"""Normalizer stage: maps book names to canonical OSIS keys."""

import re
from typing import Literal

from rapidfuzz import fuzz, process

from scripture_ref_parser.data.loader import load_canon_index
from scripture_ref_parser.types import CanonCandidate, NormalizedBook


# Minimum score threshold for fuzzy matches
_MIN_FUZZY_SCORE = 60


def _clean_name(name: str) -> str:
    """Clean a book name for lookup: lowercase, remove punctuation/spaces."""
    cleaned = re.sub(r"[.\s]+", "", name.lower())
    return cleaned


def normalize_book(
    name: str,
    mode: Literal["loose", "strict"] = "loose",
    all_candidates: bool = False,
) -> NormalizedBook:
    """Normalize a book name to its canonical OSIS key.

    Args:
        name: Book name or abbreviation to normalize
        mode: "strict" for exact matches only, "loose" for fuzzy matching
        all_candidates: If True, include all candidates above threshold

    Returns:
        NormalizedBook with key (or None if not found in strict mode)
    """
    index = load_canon_index()
    cleaned = _clean_name(name)

    # Direct lookup
    if cleaned in index:
        exact_key = index[cleaned]
        # When all_candidates=True, still get fuzzy alternatives
        if all_candidates and mode == "loose":
            fuzzy_result = _fuzzy_match(cleaned, index, mode, all_candidates=True)
            # Return exact key but include all candidates
            return NormalizedBook(
                key=exact_key,
                mode=mode,
                is_exact=True,
                candidates=fuzzy_result.candidates,
            )
        return NormalizedBook(key=exact_key, mode=mode, is_exact=True)

    # Strict mode: return None for unknown
    if mode == "strict":
        return NormalizedBook(key=None, mode=mode, is_exact=True)

    # Loose mode: fuzzy matching
    return _fuzzy_match(cleaned, index, mode, all_candidates)


def _fuzzy_match(
    cleaned_name: str,
    index: dict[str, str],
    mode: Literal["loose", "strict"],
    all_candidates: bool = False,
) -> NormalizedBook:
    """Perform fuzzy matching for loose mode."""
    # Get all possible book name keys
    choices = list(index.keys())

    # Use rapidfuzz to find matches
    matches = process.extract(
        cleaned_name, choices, scorer=fuzz.ratio, limit=10 if all_candidates else 3
    )

    # Filter by minimum score
    candidates = [
        CanonCandidate(key=index[match[0]], score=int(match[1]))
        for match in matches
        if match[1] >= _MIN_FUZZY_SCORE
    ]

    # Deduplicate by OSIS key (keep highest score)
    seen: dict[str, CanonCandidate] = {}
    for c in candidates:
        if c.key not in seen or c.score > seen[c.key].score:
            seen[c.key] = c
    unique_candidates = sorted(seen.values(), key=lambda x: -x.score)

    if not unique_candidates:
        return NormalizedBook(key=None, mode=mode, is_exact=False, candidates=[])

    # Return best match as key, with candidates list
    # Always return at least the top candidate when fuzzy matching is used
    return NormalizedBook(
        key=unique_candidates[0].key,
        mode=mode,
        is_exact=False,
        candidates=unique_candidates if all_candidates else [unique_candidates[0]],
    )
