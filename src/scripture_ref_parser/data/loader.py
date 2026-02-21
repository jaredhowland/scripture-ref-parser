"""Canon data loading utilities."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).parent

# Canon files in order of search priority
_CANON_FILES = [
    "OldTestament",
    "NewTestament",
    "BookOfMormon",
    "DoctrineAndCovenants",
    "PearlOfGreatPrice",
    "JstAppendix",
]


@lru_cache(maxsize=1)
def load_canon_index() -> dict[str, str]:
    """Load the canon index mapping lowercase names to OSIS abbreviations."""
    path = _DATA_DIR / "canon_index.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_canon_file(name: str) -> dict[str, Any]:
    """Load a specific canon file (e.g., 'OldTestament')."""
    path = _DATA_DIR / "canon" / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Canon file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def _build_book_metadata_cache() -> dict[str, dict[str, Any]]:
    """Build a cache mapping OSIS abbr to metadata from all canon files."""
    cache: dict[str, dict[str, Any]] = {}
    for canon_name in _CANON_FILES:
        try:
            data = load_canon_file(canon_name)
            for osis_abbr, meta in data.items():
                if osis_abbr not in cache:
                    cache[osis_abbr] = meta
        except FileNotFoundError:
            continue
    return cache


def get_book_metadata(osis_abbr: str) -> dict[str, Any] | None:
    """Get metadata for a book by its OSIS abbreviation."""
    cache = _build_book_metadata_cache()
    return cache.get(osis_abbr)


def get_verse_count(osis_abbr: str, chapter: int) -> int | None:
    """Get the verse count for a specific chapter of a book."""
    meta = get_book_metadata(osis_abbr)
    if meta is None:
        return None
    num_verses = meta.get("num_verses", {})
    return num_verses.get(str(chapter))


def get_all_book_names() -> list[str]:
    """Get all known book names/abbreviations for fuzzy matching."""
    index = load_canon_index()
    return list(index.keys())
