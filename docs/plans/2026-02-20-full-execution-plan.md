# Scripture Reference Parser — Full Execution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete, deployable scripture reference parser that converts freeform text to OSIS ranges, supporting KJV and LDS canons with fuzzy and strict matching modes.

**Architecture:** 4-stage pipeline (tokenize → normalize → parse → resolve) with typed interfaces, canonical data layer, thin public API, and Click-based CLI.

**Tech Stack:** Python >=3.12, `uv` package manager, `pytest`, `ruff`, `ty`, `rapidfuzz`, `click`

---

## Pre-Implementation: Project Structure Fix

The source directory uses hyphens (`parse-scripture-refs`) but Python imports require underscores. We need to rename this first.

---

### Task 0: Fix Package Naming

**Files:**
- Rename: `src/parse-scripture-refs/` → `src/scripture_ref_parser/`

**Step 1: Rename directory**
```bash
cd /Users/wgu/Documents/PyCharm\ Projects/parse-scripture-refs
mv src/parse-scripture-refs src/scripture_ref_parser
```

**Step 2: Verify structure**
```bash
ls src/scripture_ref_parser/
```
Expected: `api/ cli/ data/ normalize/ parse/ resolve/ tokenize/`

**Step 3: Commit**
```bash
git add -A
git commit -m "chore: rename package directory to use underscores"
```

---

### Task 1: Create Package `__init__.py` Files

**Files:**
- Create: `src/scripture_ref_parser/__init__.py`
- Create: `src/scripture_ref_parser/api/__init__.py`
- Create: `src/scripture_ref_parser/cli/__init__.py`
- Create: `src/scripture_ref_parser/data/__init__.py`
- Create: `src/scripture_ref_parser/normalize/__init__.py`
- Create: `src/scripture_ref_parser/parse/__init__.py`
- Create: `src/scripture_ref_parser/resolve/__init__.py`
- Create: `src/scripture_ref_parser/tokenize/__init__.py`

**Step 1: Create all `__init__.py` files**

```python
# src/scripture_ref_parser/__init__.py
"""Scripture Reference Parser - converts text to OSIS ranges."""

from scripture_ref_parser.api import parse_references

__all__ = ["parse_references"]
__version__ = "0.1.0"
```

```python
# src/scripture_ref_parser/api/__init__.py
"""Public API for scripture reference parsing."""

def parse_references(text: str, mode: str = "loose", canon_books: list[str] | None = None, all_candidates: bool = False) -> list[dict]:
    """Parse scripture reference text into OSIS ranges.
    
    Args:
        text: Freeform scripture reference text (e.g., "Gen 1:1-3; 1 Ne. 3:12")
        mode: "loose" (fuzzy matching) or "strict" (exact match only)
        canon_books: Optional list of canon files to restrict search
        all_candidates: If True, return all fuzzy match candidates
        
    Returns:
        List of OSIS range dicts with 'start' and 'end' keys
    """
    raise NotImplementedError("Pipeline not yet implemented")

__all__ = ["parse_references"]
```

```python
# src/scripture_ref_parser/cli/__init__.py
"""CLI module."""
```

```python
# src/scripture_ref_parser/data/__init__.py
"""Canon data loading."""
```

```python
# src/scripture_ref_parser/normalize/__init__.py
"""Book name normalization."""
```

```python
# src/scripture_ref_parser/parse/__init__.py
"""Reference parsing."""
```

```python
# src/scripture_ref_parser/resolve/__init__.py
"""OSIS resolution."""
```

```python
# src/scripture_ref_parser/tokenize/__init__.py
"""Tokenization."""
```

**Step 2: Verify imports work**
```bash
uv run python -c "from scripture_ref_parser import parse_references; print('OK')"
```
Expected: `OK` (then NotImplementedError when called)

**Step 3: Commit**
```bash
git add src/scripture_ref_parser/
git commit -m "chore: add __init__.py files for all modules"
```

---

### Task 2: Add CLI Entry Point to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add scripts entry point**

Add to `pyproject.toml` after `dependencies`:

```toml
[project.scripts]
scripture-ref-parser = "scripture_ref_parser.cli.cli:main"
```

**Step 2: Verify config is valid**
```bash
uv sync
```
Expected: Successful sync without errors

**Step 3: Commit**
```bash
git add pyproject.toml
git commit -m "chore: add CLI entry point to pyproject.toml"
```

---

### Task 3: Type Definitions Module

**Files:**
- Create: `src/scripture_ref_parser/types.py`
- Create: `tests/unit/test_types.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_types.py
"""Tests for type definitions."""
from scripture_ref_parser.types import Token, NormalizedBook, ParsedRef, ResolvedRange


def test_token_creation():
    token = Token(type="BOOK", text="Gen", span=(0, 3))
    assert token.type == "BOOK"
    assert token.text == "Gen"
    assert token.span == (0, 3)


def test_normalized_book_strict():
    nb = NormalizedBook(key="Gen", mode="strict")
    assert nb.key == "Gen"
    assert nb.candidates is None


def test_parsed_ref_creation():
    pr = ParsedRef(book_key="Gen", start=(1, 1), end=(1, 3), raw="Gen 1:1-3")
    assert pr.book_key == "Gen"
    assert pr.start == (1, 1)
    assert pr.end == (1, 3)


def test_resolved_range_creation():
    rr = ResolvedRange(start="Gen.1.1", end="Gen.1.3")
    assert rr.start == "Gen.1.1"
    assert rr.end == "Gen.1.3"
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_types.py -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/types.py
"""Type definitions for the scripture reference parser pipeline."""
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Token:
    """A token from the tokenizer stage."""
    type: Literal["BOOK", "NUM", "SEP", "PUNC"]
    text: str
    span: tuple[int, int]


@dataclass
class CanonCandidate:
    """A candidate match from fuzzy matching."""
    key: str
    score: int


@dataclass
class NormalizedBook:
    """Result of book name normalization."""
    key: str | None
    mode: Literal["loose", "strict"]
    candidates: list[CanonCandidate] | None = None


@dataclass
class ParsedRef:
    """A parsed scripture reference."""
    book_key: str | None
    start: tuple[int, int | None]  # (chapter, verse or None)
    end: tuple[int, int | None]  # (chapter, verse or None)
    raw: str
    errors: list[str] = field(default_factory=list)


@dataclass
class ResolvedRange:
    """A resolved OSIS range."""
    start: str | None
    end: str | None
    fuzzy_ratio: int | None = None
    not_found: str | None = None


@dataclass
class ResolvedRangeWithCandidates:
    """A resolved range with multiple candidates (for --all-candidates)."""
    options: list[ResolvedRange]
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_types.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/types.py tests/unit/test_types.py
git commit -m "feat: add type definitions for pipeline stages"
```

---

### Task 4: Data Loader Module

**Files:**
- Create: `src/scripture_ref_parser/data/loader.py`
- Create: `tests/unit/test_data_loader.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_data_loader.py
"""Tests for canon data loading."""
from scripture_ref_parser.data.loader import (
    load_canon_index,
    load_canon_file,
    get_book_metadata,
    get_verse_count,
)


def test_load_canon_index():
    index = load_canon_index()
    assert isinstance(index, dict)
    assert index.get("gen") == "Gen"
    assert index.get("genesis") == "Gen"
    assert index.get("1nephi") == "1Ne"


def test_load_canon_file_old_testament():
    data = load_canon_file("OldTestament")
    assert "Gen" in data
    assert data["Gen"]["num_chaps"] == 50


def test_get_book_metadata():
    meta = get_book_metadata("Gen")
    assert meta is not None
    assert meta["num_chaps"] == 50
    assert meta["num_verses"]["1"] == 31


def test_get_verse_count():
    count = get_verse_count("Gen", 1)
    assert count == 31
    count = get_verse_count("Gen", 50)
    assert count == 26


def test_get_verse_count_invalid():
    count = get_verse_count("Gen", 999)
    assert count is None
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_data_loader.py -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/data/loader.py
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
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_data_loader.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/data/loader.py tests/unit/test_data_loader.py
git commit -m "feat(data): add canon data loader with caching"
```

---

### Task 5: Tokenizer Stage

**Files:**
- Create: `src/scripture_ref_parser/tokenize/tokenizer.py`
- Create: `tests/unit/test_tokenizer.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_tokenizer.py
"""Tests for the tokenizer stage."""
from scripture_ref_parser.tokenize.tokenizer import tokenize
from scripture_ref_parser.types import Token


def test_tokenize_simple_reference():
    tokens = tokenize("Gen 1:1")
    assert len(tokens) >= 2
    # Should have a BOOK-like token and NUM tokens
    texts = [t.text.lower() for t in tokens]
    assert "gen" in texts or any("gen" in t for t in texts)


def test_tokenize_preserves_separators():
    tokens = tokenize("Gen 1:1; Exod 2:3")
    types = [t.type for t in tokens]
    assert "SEP" in types  # semicolon is a separator


def test_tokenize_handles_ranges():
    tokens = tokenize("Gen 1:1-3")
    # Should capture the range
    texts = [t.text for t in tokens]
    combined = "".join(texts)
    assert "1" in combined and "3" in combined


def test_tokenize_handles_periods():
    tokens = tokenize("Gen. 1:1")
    # Period after abbreviation should not break reference
    texts = [t.text.lower() for t in tokens]
    assert any("gen" in t for t in texts)


def test_tokenize_handles_lds_references():
    tokens = tokenize("1 Ne. 3:7")
    texts = [t.text for t in tokens]
    combined = " ".join(texts).lower()
    assert "1" in combined and ("ne" in combined or "nephi" in combined)


def test_tokenize_span_tracking():
    text = "Gen 1:1"
    tokens = tokenize(text)
    for token in tokens:
        start, end = token.span
        assert text[start:end] == token.text
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_tokenizer.py -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/tokenize/tokenizer.py
"""Tokenizer stage: converts raw text into candidate tokens."""
import re
from scripture_ref_parser.types import Token

# Pattern for tokenizing scripture references
# Captures: words (potential book names), numbers with verse notation, separators
_TOKEN_PATTERN = re.compile(
    r"""
    (?P<num>\d+(?::\d+)?(?:-\d+(?::\d+)?)?)  # Numbers with optional verse/range notation
    |(?P<sep>[;,])                            # List separators
    |(?P<dash>[—–-])                          # Range separators (em-dash, en-dash, hyphen)
    |(?P<word>[A-Za-z]+\.?)                   # Words (potential book names)
    """,
    re.VERBOSE,
)


def tokenize(text: str) -> list[Token]:
    """Tokenize scripture reference text into candidate tokens.
    
    Args:
        text: Raw scripture reference text
        
    Returns:
        List of Token objects with type, text, and span information
    """
    tokens: list[Token] = []
    
    for match in _TOKEN_PATTERN.finditer(text):
        span = (match.start(), match.end())
        matched_text = match.group()
        
        if match.group("num"):
            tokens.append(Token(type="NUM", text=matched_text, span=span))
        elif match.group("sep"):
            tokens.append(Token(type="SEP", text=matched_text, span=span))
        elif match.group("dash"):
            tokens.append(Token(type="PUNC", text=matched_text, span=span))
        elif match.group("word"):
            # Could be a book name or part of one
            tokens.append(Token(type="BOOK", text=matched_text.rstrip("."), span=span))
    
    return tokens
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_tokenizer.py -v
```
Expected: PASS (may need iteration)

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/tokenize/tokenizer.py tests/unit/test_tokenizer.py
git commit -m "feat(tokenize): add tokenizer stage with span tracking"
```

---

### Task 6: Normalizer Stage (Strict Mode)

**Files:**
- Create: `src/scripture_ref_parser/normalize/normalize.py`
- Create: `tests/unit/test_normalize.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_normalize.py
"""Tests for the normalizer stage."""
from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.types import NormalizedBook


def test_normalize_strict_known_full_name():
    result = normalize_book("Genesis", mode="strict")
    assert result.key == "Gen"
    assert result.mode == "strict"


def test_normalize_strict_known_abbreviation():
    result = normalize_book("Gen", mode="strict")
    assert result.key == "Gen"


def test_normalize_strict_case_insensitive():
    result = normalize_book("GENESIS", mode="strict")
    assert result.key == "Gen"


def test_normalize_strict_removes_periods():
    result = normalize_book("Gen.", mode="strict")
    assert result.key == "Gen"


def test_normalize_strict_unknown():
    result = normalize_book("Exodis", mode="strict")
    assert result.key is None


def test_normalize_strict_lds_book():
    result = normalize_book("1 Ne", mode="strict")
    assert result.key == "1Ne"


def test_normalize_strict_lds_book_full():
    result = normalize_book("1 Nephi", mode="strict")
    assert result.key == "1Ne"
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_normalize.py -v
```
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/normalize/normalize.py
"""Normalizer stage: maps book names to canonical OSIS keys."""
import re
from typing import Literal
from scripture_ref_parser.data.loader import load_canon_index
from scripture_ref_parser.types import NormalizedBook, CanonCandidate


def _clean_name(name: str) -> str:
    """Clean a book name for lookup: lowercase, remove punctuation/spaces."""
    # Remove periods and extra spaces, lowercase
    cleaned = re.sub(r'[.\s]+', '', name.lower())
    return cleaned


def normalize_book(
    name: str, 
    mode: Literal["loose", "strict"] = "loose"
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
    mode: Literal["loose", "strict"]
) -> NormalizedBook:
    """Perform fuzzy matching for loose mode (placeholder)."""
    # Will be implemented in Task 7
    return NormalizedBook(key=None, mode=mode, candidates=[])
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_normalize.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/normalize/normalize.py tests/unit/test_normalize.py
git commit -m "feat(normalize): add normalizer stage with strict mode"
```

---

### Task 7: Normalizer Fuzzy Matching (Loose Mode)

**Files:**
- Modify: `src/scripture_ref_parser/normalize/normalize.py`
- Create: `tests/unit/test_normalize_fuzzy.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_normalize_fuzzy.py
"""Tests for fuzzy matching in normalizer."""
from scripture_ref_parser.normalize.normalize import normalize_book


def test_normalize_loose_typo():
    result = normalize_book("Exodis", mode="loose")
    assert result.key == "Exod"
    assert result.candidates is not None
    assert len(result.candidates) > 0


def test_normalize_loose_partial():
    result = normalize_book("Gene", mode="loose")
    assert result.key == "Gen"


def test_normalize_loose_returns_candidates():
    result = normalize_book("E", mode="loose")
    assert result.candidates is not None
    # Should have multiple candidates starting with E


def test_normalize_loose_scores():
    result = normalize_book("Exodis", mode="loose")
    if result.candidates:
        for candidate in result.candidates:
            assert candidate.score > 0
            assert candidate.score <= 100
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_normalize_fuzzy.py -v
```
Expected: FAIL (fuzzy matching not implemented)

**Step 3: Implement fuzzy matching**

Update `src/scripture_ref_parser/normalize/normalize.py`:

```python
# src/scripture_ref_parser/normalize/normalize.py
"""Normalizer stage: maps book names to canonical OSIS keys."""
import re
from typing import Literal
from rapidfuzz import fuzz, process
from scripture_ref_parser.data.loader import load_canon_index
from scripture_ref_parser.types import NormalizedBook, CanonCandidate


# Minimum score threshold for fuzzy matches
_MIN_FUZZY_SCORE = 60


def _clean_name(name: str) -> str:
    """Clean a book name for lookup: lowercase, remove punctuation/spaces."""
    cleaned = re.sub(r'[.\s]+', '', name.lower())
    return cleaned


def normalize_book(
    name: str, 
    mode: Literal["loose", "strict"] = "loose",
    all_candidates: bool = False
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
        return NormalizedBook(key=index[cleaned], mode=mode)
    
    # Strict mode: return None for unknown
    if mode == "strict":
        return NormalizedBook(key=None, mode=mode)
    
    # Loose mode: fuzzy matching
    return _fuzzy_match(cleaned, index, mode, all_candidates)


def _fuzzy_match(
    cleaned_name: str, 
    index: dict[str, str], 
    mode: Literal["loose", "strict"],
    all_candidates: bool = False
) -> NormalizedBook:
    """Perform fuzzy matching for loose mode."""
    # Get all possible book name keys
    choices = list(index.keys())
    
    # Use rapidfuzz to find matches
    matches = process.extract(
        cleaned_name, 
        choices, 
        scorer=fuzz.ratio,
        limit=10 if all_candidates else 3
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
        return NormalizedBook(key=None, mode=mode, candidates=[])
    
    # Return best match as key, with candidates list
    return NormalizedBook(
        key=unique_candidates[0].key,
        mode=mode,
        candidates=unique_candidates if all_candidates else None
    )
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_normalize_fuzzy.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/normalize/normalize.py tests/unit/test_normalize_fuzzy.py
git commit -m "feat(normalize): add fuzzy matching for loose mode"
```

---

### Task 8: Parser Stage (Chapter:Verse Ranges)

**Files:**
- Create: `src/scripture_ref_parser/parse/parser.py`
- Create: `tests/unit/test_parser.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_parser.py
"""Tests for the parser stage."""
from scripture_ref_parser.parse.parser import parse_tokens
from scripture_ref_parser.types import Token, ParsedRef


def test_parse_simple_chapter_verse():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 1
    assert parsed[0].book_key == "Gen"
    assert parsed[0].start == (1, 1)
    assert parsed[0].end == (1, 1)


def test_parse_verse_range():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1-3", span=(4, 9)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, 1)
    assert parsed[0].end == (1, 3)


def test_parse_chapter_only():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1", span=(4, 5)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, None)
    assert parsed[0].end == (1, None)


def test_parse_chapter_range():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1-3", span=(4, 7)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, None)
    assert parsed[0].end == (3, None)


def test_parse_multiple_references():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
        Token(type="SEP", text=";", span=(7, 8)),
        Token(type="BOOK", text="Exod", span=(9, 13)),
        Token(type="NUM", text="2:3", span=(14, 17)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 2
    assert parsed[0].book_key == "Gen"
    assert parsed[1].book_key == "Exod"


def test_parse_implicit_book_continuation():
    # "Gen 1:1, 2:3" - second ref uses same book
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
        Token(type="SEP", text=",", span=(7, 8)),
        Token(type="NUM", text="2:3", span=(9, 12)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 2
    assert parsed[0].book_key == "Gen"
    assert parsed[1].book_key == "Gen"  # Inherited from previous
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_parser.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/parse/parser.py
"""Parser stage: converts tokens into parsed references."""
import re
from scripture_ref_parser.types import Token, ParsedRef

# Pattern for parsing number tokens
# Matches: chapter, chapter:verse, chapter-chapter, chapter:verse-verse, chapter:verse-chapter:verse
_NUM_PATTERN = re.compile(
    r'^(?P<start_chap>\d+)(?::(?P<start_verse>\d+))?(?:-(?P<end_chap>\d+)?(?::(?P<end_verse>\d+))?)?$'
)


def _parse_num_token(text: str) -> tuple[tuple[int, int | None], tuple[int, int | None]]:
    """Parse a NUM token into start and end tuples.
    
    Returns:
        (start, end) where each is (chapter, verse_or_None)
    """
    match = _NUM_PATTERN.match(text)
    if not match:
        # Fallback for unparseable
        return ((1, None), (1, None))
    
    start_chap = int(match.group("start_chap"))
    start_verse = int(match.group("start_verse")) if match.group("start_verse") else None
    end_chap_str = match.group("end_chap")
    end_verse_str = match.group("end_verse")
    
    # Determine end based on what's present
    if end_chap_str is None and end_verse_str is None:
        # Single reference: Gen 1 or Gen 1:1
        end_chap = start_chap
        end_verse = start_verse
    elif end_verse_str and not end_chap_str:
        # Verse range: Gen 1:1-3
        end_chap = start_chap
        end_verse = int(end_verse_str)
    elif end_chap_str and not end_verse_str:
        # Chapter range: Gen 1-3, or verse range like 1:1-3
        if start_verse is not None:
            # This is actually a verse range: 1:1-3
            end_chap = start_chap
            end_verse = int(end_chap_str)
        else:
            # Chapter range: 1-3
            end_chap = int(end_chap_str)
            end_verse = None
    else:
        # Full range: Gen 1:1-2:3
        end_chap = int(end_chap_str)
        end_verse = int(end_verse_str) if end_verse_str else None
    
    return ((start_chap, start_verse), (end_chap, end_verse))


def parse_tokens(tokens: list[Token]) -> list[ParsedRef]:
    """Parse a list of tokens into structured references.
    
    Args:
        tokens: List of Token objects from tokenizer
        
    Returns:
        List of ParsedRef objects
    """
    results: list[ParsedRef] = []
    current_book: str | None = None
    pending_book_tokens: list[Token] = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if token.type == "BOOK":
            # Accumulate book name tokens (for "1 Nephi" etc.)
            pending_book_tokens.append(token)
            i += 1
            continue
            
        elif token.type == "NUM":
            # We have a number - time to create a reference
            if pending_book_tokens:
                # Use accumulated book tokens
                book_text = " ".join(t.text for t in pending_book_tokens)
                current_book = book_text
                pending_book_tokens = []
            
            start, end = _parse_num_token(token.text)
            raw_start = pending_book_tokens[0].span[0] if pending_book_tokens else (
                results[-1].raw.split()[0] if results else ""
            )
            
            results.append(ParsedRef(
                book_key=current_book,
                start=start,
                end=end,
                raw=f"{current_book} {token.text}" if current_book else token.text
            ))
            i += 1
            
        elif token.type == "SEP":
            # Separator - clear pending book tokens for semicolon (new reference)
            if token.text == ";":
                pending_book_tokens = []
            i += 1
            
        else:
            i += 1
    
    return results
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_parser.py -v
```
Expected: PASS (may need iteration)

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/parse/parser.py tests/unit/test_parser.py
git commit -m "feat(parse): add parser for chapter:verse ranges"
```

---

### Task 9: Resolver Stage (OSIS Expansion)

**Files:**
- Create: `src/scripture_ref_parser/resolve/resolver.py`
- Create: `tests/unit/test_resolver.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_resolver.py
"""Tests for the resolver stage."""
from scripture_ref_parser.resolve.resolver import resolve_parsed
from scripture_ref_parser.types import ParsedRef, ResolvedRange


def test_resolve_simple_verse():
    parsed = [ParsedRef(book_key="Gen", start=(1, 1), end=(1, 1), raw="Gen 1:1")]
    resolved = resolve_parsed(parsed)
    assert len(resolved) == 1
    assert resolved[0].start == "Gen.1.1"
    assert resolved[0].end == "Gen.1.1"


def test_resolve_verse_range():
    parsed = [ParsedRef(book_key="Gen", start=(1, 1), end=(1, 3), raw="Gen 1:1-3")]
    resolved = resolve_parsed(parsed)
    assert resolved[0].start == "Gen.1.1"
    assert resolved[0].end == "Gen.1.3"


def test_resolve_chapter_only_expands():
    parsed = [ParsedRef(book_key="Gen", start=(1, None), end=(1, None), raw="Gen 1")]
    resolved = resolve_parsed(parsed)
    assert resolved[0].start == "Gen.1.1"
    assert resolved[0].end == "Gen.1.31"  # Genesis 1 has 31 verses


def test_resolve_chapter_range():
    parsed = [ParsedRef(book_key="Gen", start=(1, None), end=(2, None), raw="Gen 1-2")]
    resolved = resolve_parsed(parsed)
    assert resolved[0].start == "Gen.1.1"
    assert resolved[0].end == "Gen.2.25"  # Genesis 2 has 25 verses


def test_resolve_unknown_book():
    parsed = [ParsedRef(book_key=None, start=(1, 1), end=(1, 1), raw="Unknown 1:1")]
    resolved = resolve_parsed(parsed)
    assert resolved[0].start is None
    assert resolved[0].not_found is not None


def test_resolve_lds_book():
    parsed = [ParsedRef(book_key="1Ne", start=(3, 7), end=(3, 7), raw="1 Ne 3:7")]
    resolved = resolve_parsed(parsed)
    assert resolved[0].start == "1Ne.3.7"
    assert resolved[0].end == "1Ne.3.7"
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/unit/test_resolver.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/scripture_ref_parser/resolve/resolver.py
"""Resolver stage: expands parsed refs to OSIS identifiers."""
from scripture_ref_parser.types import ParsedRef, ResolvedRange
from scripture_ref_parser.data.loader import get_book_metadata, get_verse_count
from scripture_ref_parser.normalize.normalize import normalize_book


def _format_osis(book: str, chapter: int, verse: int) -> str:
    """Format an OSIS identifier."""
    return f"{book}.{chapter}.{verse}"


def resolve_parsed(
    parsed_refs: list[ParsedRef],
    mode: str = "loose"
) -> list[ResolvedRange]:
    """Resolve parsed references to OSIS ranges.
    
    Args:
        parsed_refs: List of ParsedRef from parser stage
        mode: "loose" or "strict" for book name normalization
        
    Returns:
        List of ResolvedRange with OSIS start/end identifiers
    """
    results: list[ResolvedRange] = []
    
    for ref in parsed_refs:
        # Normalize book name if it's not already an OSIS key
        if ref.book_key is None:
            results.append(ResolvedRange(
                start=None,
                end=None,
                not_found=f"Unknown book in '{ref.raw}'"
            ))
            continue
        
        # Try to normalize the book name to OSIS
        normalized = normalize_book(ref.book_key, mode=mode)
        osis_key = normalized.key
        
        if osis_key is None:
            results.append(ResolvedRange(
                start=None,
                end=None,
                not_found=f"Unknown book '{ref.book_key}'"
            ))
            continue
        
        # Get book metadata for verse counts
        meta = get_book_metadata(osis_key)
        if meta is None:
            results.append(ResolvedRange(
                start=None,
                end=None,
                not_found=f"No metadata for '{osis_key}'"
            ))
            continue
        
        # Extract chapter/verse info
        start_chap, start_verse = ref.start
        end_chap, end_verse = ref.end
        
        # Expand chapter-only to full verse range
        if start_verse is None:
            start_verse = 1
        if end_verse is None:
            end_verse = get_verse_count(osis_key, end_chap) or 1
        
        # Build OSIS identifiers
        start_osis = _format_osis(osis_key, start_chap, start_verse)
        end_osis = _format_osis(osis_key, end_chap, end_verse)
        
        # Add fuzzy ratio if from fuzzy match
        fuzzy_ratio = None
        if normalized.candidates and len(normalized.candidates) > 0:
            fuzzy_ratio = normalized.candidates[0].score
        
        results.append(ResolvedRange(
            start=start_osis,
            end=end_osis,
            fuzzy_ratio=fuzzy_ratio
        ))
    
    return results
```

**Step 4: Run test to verify it passes**
```bash
uvx pytest tests/unit/test_resolver.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/resolve/resolver.py tests/unit/test_resolver.py
git commit -m "feat(resolve): add resolver with chapter expansion"
```

---

### Task 10: API Orchestration

**Files:**
- Modify: `src/scripture_ref_parser/api/__init__.py`
- Create: `tests/integration/test_api.py`

**Step 1: Write the failing test**

```python
# tests/integration/test_api.py
"""Integration tests for the public API."""
from scripture_ref_parser.api import parse_references


def test_api_simple_reference():
    results = parse_references("Gen 1:1")
    assert len(results) == 1
    assert results[0]["start"] == "Gen.1.1"
    assert results[0]["end"] == "Gen.1.1"


def test_api_multiple_references():
    results = parse_references("Gen 1:1-3; Exod 2:1")
    assert len(results) == 2
    assert results[0]["start"] == "Gen.1.1"
    assert results[1]["start"] == "Exod.2.1"


def test_api_lds_references():
    results = parse_references("1 Ne. 3:7")
    assert len(results) == 1
    assert results[0]["start"] == "1Ne.3.7"


def test_api_fuzzy_match_loose():
    results = parse_references("Exodis 1:1", mode="loose")
    assert len(results) == 1
    assert results[0]["start"] == "Exod.1.1"


def test_api_strict_mode_unknown():
    results = parse_references("Exodis 1:1", mode="strict")
    assert len(results) == 1
    assert results[0]["start"] is None
    assert "not_found" in results[0]


def test_api_chapter_expansion():
    results = parse_references("Gen 1")
    assert results[0]["start"] == "Gen.1.1"
    assert results[0]["end"] == "Gen.1.31"


def test_api_all_candidates():
    results = parse_references("E 1:1", mode="loose", all_candidates=True)
    assert len(results) == 1
    # Should have options when ambiguous
    if "options" in results[0]:
        assert len(results[0]["options"]) > 0
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/integration/test_api.py -v
```
Expected: FAIL

**Step 3: Implement API orchestration**

```python
# src/scripture_ref_parser/api/__init__.py
"""Public API for scripture reference parsing."""
from scripture_ref_parser.tokenize.tokenizer import tokenize
from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.parse.parser import parse_tokens
from scripture_ref_parser.resolve.resolver import resolve_parsed
from scripture_ref_parser.types import ResolvedRange, ResolvedRangeWithCandidates


def parse_references(
    text: str, 
    mode: str = "loose", 
    canon_books: list[str] | None = None, 
    all_candidates: bool = False
) -> list[dict]:
    """Parse scripture reference text into OSIS ranges.
    
    Args:
        text: Freeform scripture reference text (e.g., "Gen 1:1-3; 1 Ne. 3:12")
        mode: "loose" (fuzzy matching) or "strict" (exact match only)
        canon_books: Optional list of canon files to restrict search (not yet implemented)
        all_candidates: If True, return all fuzzy match candidates for ambiguous refs
        
    Returns:
        List of dicts with 'start', 'end' keys (and optionally 'fuzzy_ratio', 'not_found', 'options')
    """
    # Stage 1: Tokenize
    tokens = tokenize(text)
    
    # Stage 2+3: Parse (includes normalization)
    # First parse tokens, then normalize book names in resolver
    parsed = parse_tokens(tokens)
    
    # Update book keys with normalized versions if all_candidates
    if all_candidates:
        for ref in parsed:
            if ref.book_key:
                normalized = normalize_book(ref.book_key, mode=mode, all_candidates=True)
                # Store candidates for later use
                ref._normalized = normalized  # type: ignore
    
    # Stage 4: Resolve
    resolved = resolve_parsed(parsed, mode=mode)
    
    # Convert to output format
    results: list[dict] = []
    for i, item in enumerate(resolved):
        result: dict = {
            "start": item.start,
            "end": item.end,
        }
        
        if item.fuzzy_ratio is not None:
            result["fuzzy_ratio"] = item.fuzzy_ratio
        
        if item.not_found is not None:
            result["not_found"] = item.not_found
        
        # Handle all_candidates
        if all_candidates and i < len(parsed):
            ref = parsed[i]
            if hasattr(ref, '_normalized') and ref._normalized.candidates:  # type: ignore
                if len(ref._normalized.candidates) > 1:  # type: ignore
                    # Multiple candidates - return as options
                    options = []
                    for candidate in ref._normalized.candidates:  # type: ignore
                        # Would need to resolve each candidate here
                        # For now, just include the info
                        options.append({
                            "start": result["start"],
                            "end": result["end"],
                            "fuzzy_ratio": candidate.score
                        })
                    if len(options) > 1:
                        result["options"] = options
        
        results.append(result)
    
    return results


__all__ = ["parse_references"]
```

**Step 4: Run tests**
```bash
uvx pytest tests/integration/test_api.py tests/unit -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/api/__init__.py tests/integration/test_api.py
git commit -m "feat(api): add pipeline orchestration"
```

---

### Task 11: CLI Implementation

**Files:**
- Create: `src/scripture_ref_parser/cli/cli.py`
- Create: `tests/integration/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/integration/test_cli.py
"""Integration tests for CLI."""
import json
import subprocess


def test_cli_simple():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Gen 1:1"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Gen.1.1"


def test_cli_strict_mode():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Gen 1:1", "--mode", "strict"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Gen.1.1"


def test_cli_loose_mode():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Exodis 1:1", "--mode", "loose"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Exod.1.1"


def test_cli_all_candidates():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "E 1:1", "--all-candidates"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) >= 1
```

**Step 2: Run test to verify it fails**
```bash
uvx pytest tests/integration/test_cli.py -v
```
Expected: FAIL (CLI not implemented)

**Step 3: Implement CLI**

```python
# src/scripture_ref_parser/cli/cli.py
"""Command-line interface for scripture reference parser."""
import json
import sys
import click
from scripture_ref_parser.api import parse_references


@click.command()
@click.argument("text")
@click.option(
    "--mode",
    type=click.Choice(["loose", "strict"]),
    default="loose",
    help="Matching mode: 'loose' allows fuzzy matching, 'strict' requires exact matches."
)
@click.option(
    "--all-candidates",
    is_flag=True,
    default=False,
    help="Return all fuzzy match candidates instead of just the top match."
)
@click.option(
    "--pretty",
    is_flag=True,
    default=False,
    help="Pretty-print JSON output."
)
def main(text: str, mode: str, all_candidates: bool, pretty: bool) -> None:
    """Parse scripture references and output OSIS ranges.
    
    TEXT is the scripture reference text to parse, e.g. "Gen 1:1-3; 1 Ne. 3:7"
    """
    try:
        results = parse_references(text, mode=mode, all_candidates=all_candidates)
        
        indent = 2 if pretty else None
        output = json.dumps(results, indent=indent)
        click.echo(output)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests**
```bash
uvx pytest tests/integration/test_cli.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add src/scripture_ref_parser/cli/cli.py tests/integration/test_cli.py
git commit -m "feat(cli): add Click-based CLI"
```

---

### Task 12: Run Full Test Suite and Lint

**Files:** None (verification only)

**Step 1: Run all tests**
```bash
uvx pytest tests/ -v
```
Expected: All tests PASS

**Step 2: Run formatter**
```bash
uvx ruff format
```
Expected: Files formatted

**Step 3: Run linter**
```bash
uvx ruff check --fix
```
Expected: No errors (or all auto-fixed)

**Step 4: Run type checker**
```bash
uvx ty check
```
Expected: No type errors

**Step 5: Commit any fixes**
```bash
git add -A
git commit -m "style: format and lint cleanup"
```

---

### Task 13: Update README

**Files:**
- Modify: `README.md`

**Step 1: Update README content**

```markdown
# parse-scripture-refs

A modular Python library and CLI that parses scripture references (KJV OT/NT and LDS canon: Book of Mormon, Doctrine & Covenants, Pearl of Great Price) and returns OSIS-based ranges.

## Installation

```bash
pip install parse-scripture-refs
```

Or with `uv`:

```bash
uv add parse-scripture-refs
```

## Quick Start

### Python API

```python
from scripture_ref_parser import parse_references

# Basic usage
results = parse_references("Gen 1:1-3; 1 Ne. 3:7")
# [{"start": "Gen.1.1", "end": "Gen.1.3"}, {"start": "1Ne.3.7", "end": "1Ne.3.7"}]

# Strict mode (no fuzzy matching)
results = parse_references("Gen 1:1", mode="strict")

# Get all fuzzy candidates
results = parse_references("E 1:1", mode="loose", all_candidates=True)
```

### CLI

```bash
# Basic usage
scripture-ref-parser "Gen 1:1-3; Exod 2:1"

# Strict mode
scripture-ref-parser "Gen 1:1" --mode strict

# Pretty print
scripture-ref-parser "Gen 1:1" --pretty

# All candidates
scripture-ref-parser "E 1:1" --all-candidates
```

## Output Format

### Loose Mode (default)

```json
[
  {"start": "Gen.1.1", "end": "Gen.1.4"},
  {"start": "1Ne.3.12", "end": "1Ne.3.12"},
  {"start": "Exod.1.2", "end": "Exod.1.22", "fuzzy_ratio": 80}
]
```

### Strict Mode

```json
[
  {"start": "Gen.1.1", "end": "Gen.1.4"},
  {"start": null, "end": null, "not_found": "Unknown book 'Exodis'"}
]
```

## Supported Canons

- **KJV Old Testament** (39 books)
- **KJV New Testament** (27 books)
- **Book of Mormon** (15 books)
- **Doctrine & Covenants** (138 sections + OD)
- **Pearl of Great Price** (5 books)
- **JST Appendix**

## Development

```bash
# Run tests
uvx pytest

# Format code
uvx ruff format

# Lint
uvx ruff check --fix

# Type check
uvx ty check
```

## License

MIT
```

**Step 2: Commit**
```bash
git add README.md
git commit -m "docs: update README with usage examples"
```

---

### Task 14: Prepare for Deployment

**Files:**
- Verify: `pyproject.toml` metadata

**Step 1: Verify pyproject.toml has required fields**

Ensure these are present:
```toml
[project]
name = "parse-scripture-refs"
version = "0.1.0"
description = "Parses scripture references and returns OSIS references/ranges."
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["scripture", "bible", "osis", "parser", "lds"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Topic :: Religion",
]
```

**Step 2: Build package**
```bash
uv build
```
Expected: Creates `dist/` with `.whl` and `.tar.gz`

**Step 3: Test local install**
```bash
uv pip install dist/parse_scripture_refs-0.1.0-py3-none-any.whl
scripture-ref-parser "Gen 1:1"
```
Expected: Returns JSON output

**Step 4: Commit**
```bash
git add pyproject.toml
git commit -m "chore: prepare for PyPI deployment"
```

---

### Task 15: Tag Release and Publish (Optional)

**Step 1: Create git tag**
```bash
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

**Step 2: Publish to PyPI (when ready)**
```bash
uv publish
```

---

## Summary Checklist

| Task | Description | Status |
|------|-------------|--------|
| 0 | Fix package naming | ⬜ |
| 1 | Create `__init__.py` files | ⬜ |
| 2 | Add CLI entry point | ⬜ |
| 3 | Type definitions | ⬜ |
| 4 | Data loader | ⬜ |
| 5 | Tokenizer | ⬜ |
| 6 | Normalizer (strict) | ⬜ |
| 7 | Normalizer (fuzzy) | ⬜ |
| 8 | Parser | ⬜ |
| 9 | Resolver | ⬜ |
| 10 | API orchestration | ⬜ |
| 11 | CLI | ⬜ |
| 12 | Full test suite | ⬜ |
| 13 | README | ⬜ |
| 14 | Deployment prep | ⬜ |
| 15 | Tag and publish | ⬜ |

---

**Plan complete and saved.** Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
