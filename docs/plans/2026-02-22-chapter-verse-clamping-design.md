# Chapter/Verse Clamping Design

**Date:** 2026-02-22  
**Feature:** Clamp invalid chapter/verse numbers to valid ranges  
**Status:** Approved

## Overview

Add validation and clamping for chapter and verse numbers that exceed the actual content in a book. This ensures the parser returns valid OSIS references even when users provide out-of-bounds chapter/verse numbers.

## Requirements

1. **Loose mode:** Clamp invalid values to max valid and add a `warning` field
2. **Strict mode:** Return `not_found` with explanation instead of clamping
3. **Clamp both:** Chapter numbers (exceed `num_chaps`) and verse numbers (exceed chapter verse count)
4. **Range clamping:** For ranges like `1:1-50` where 50 exceeds max, clamp end verse

## Behavior Examples

| Input | Mode | Output |
|-------|------|--------|
| `4 Nephi 3` | loose | `{start: "4Ne.1.1", end: "4Ne.1.49", warning: "Clamped chapter from 3 to 1"}` |
| `4 Nephi 3` | strict | `{start: null, end: null, not_found: "Chapter 3 does not exist in 4 Nephi (only 1 chapter)"}` |
| `4 Nephi 1:1-50` | loose | `{start: "4Ne.1.1", end: "4Ne.1.49", warning: "Clamped verse from 50 to 49"}` |
| `4 Nephi 1:50` | loose | `{start: "4Ne.1.50", end: "4Ne.1.50", warning: "Clamped verse from 50 to 49"}` |

## Implementation Plan

### 1. Update `types.py`

Add `warning` field to `ResolvedRange`:

```python
@dataclass
class ResolvedRange:
    start: str | None
    end: str | None
    fuzzy_ratio: int | None = None
    not_found: str | None = None
    warning: str | None = None  # NEW
```

### 2. Update `resolver.py`

Add helper functions and modify resolution logic:

```python
def get_num_chapters(osis_key: str) -> int | None:
    """Get the number of chapters in a book."""
    meta = get_book_metadata(osis_key)
    return meta.get("num_chaps") if meta else None

def clamp_chapter(osis_key: str, chapter: int) -> tuple[int, str | None]:
    """Clamp chapter to valid range. Returns (clamped_chapter, warning_or_none)."""
    num_chaps = get_num_chapters(osis_key)
    if num_chaps is None:
        return chapter, None
    if chapter > num_chaps:
        return num_chaps, f"Clamped chapter from {chapter} to {num_chaps}"
    return chapter, None

def clamp_verse(osis_key: str, chapter: int, verse: int) -> tuple[int, str | None]:
    """Clamp verse to valid range for chapter. Returns (clamped_verse, warning_or_none)."""
    verse_count = get_verse_count(osis_key, chapter)
    if verse_count is None:
        return verse, None
    if verse > verse_count:
        return verse_count, f"Clamped verse from {verse} to {verse_count}"
    return verse, None
```

Modify `resolve_parsed()` to:
- In **loose mode**: Call clamping helpers, collect warnings
- In **strict mode**: Check bounds first, return `not_found` if invalid

### 3. Update `api/__init__.py`

Pass `warning` field through to output dict alongside `fuzzy_ratio`.

## Files to Modify

1. `src/scripture_ref_parser/types.py` - Add `warning` field
2. `src/scripture_ref_parser/resolve/resolver.py` - Add clamping logic
3. `src/scripture_ref_parser/api/__init__.py` - Pass warning to output

## Testing

Add tests for:
- Loose mode: chapter clamping, verse clamping, range clamping
- Strict mode: chapter out of bounds, verse out of bounds
- Edge cases: chapter 0, verse 0, negative numbers