"""Resolver stage: expands parsed refs to OSIS identifiers."""

from typing import Literal

from scripture_ref_parser.data.loader import get_book_metadata, get_verse_count
from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.types import ParsedRef, ResolvedRange


def _format_osis(book: str, chapter: int, verse: int) -> str:
    """Format an OSIS identifier."""
    return f"{book}.{chapter}.{verse}"


def _clamp_chapter(osis_key: str, chapter: int) -> tuple[int, str | None]:
    """Clamp chapter to book's max chapters. Returns (chapter, warning)."""
    meta = get_book_metadata(osis_key)
    if meta is None:
        return chapter, None
    num_chaps = meta.get("num_chaps")
    if num_chaps is None:
        return chapter, None
    if chapter > num_chaps:
        return num_chaps, f"Clamped chapter from {chapter} to {num_chaps}"
    return chapter, None


def _clamp_verse(osis_key: str, chapter: int, verse: int) -> tuple[int, str | None]:
    """Clamp verse to chapter's max verses. Returns (verse, warning)."""
    verse_count = get_verse_count(osis_key, chapter)
    if verse_count is None:
        return verse, None
    if verse > verse_count:
        return verse_count, f"Clamped verse from {verse} to {verse_count}"
    return verse, None


def resolve_ref_with_book(
    parsed_ref: "ParsedRef",
    osis_key: str,
    fuzzy_ratio: int | None = None,
    mode: Literal["loose", "strict"] = "loose",
) -> "ResolvedRange":
    """Resolve a single parsed ref using a specific OSIS book key.

    Honors `mode`: in `loose` clamps out-of-bounds chapters/verses and returns warnings;
    in `strict` returns `not_found` when bounds are invalid.
    """
    meta = get_book_metadata(osis_key)
    if meta is None:
        return ResolvedRange(
            start=None, end=None, not_found=f"No metadata for '{osis_key}'"
        )

    display_name = meta.get("names", [osis_key])[0]

    start_chap, start_verse = parsed_ref.start
    end_chap, end_verse = parsed_ref.end

    # Validate chapters
    num_chaps = meta.get("num_chaps")
    if mode == "strict" and num_chaps is not None:
        if start_chap > num_chaps or end_chap > num_chaps:
            return ResolvedRange(
                start=None,
                end=None,
                not_found=(
                    f"Chapter {start_chap if start_chap>num_chaps else end_chap} does not exist in {display_name} (only {num_chaps} chapter{'s' if num_chaps!=1 else ''})"
                ),
            )

    warnings: list[str] = []

    # In loose mode clamp chapters
    if num_chaps is not None:
        orig_start_chap = start_chap
        orig_end_chap = end_chap
        if start_chap > num_chaps:
            start_chap = num_chaps
            warnings.append(f"Clamped chapter from {orig_start_chap} to {start_chap}")
        if end_chap > num_chaps:
            end_chap = num_chaps
            warnings.append(f"Clamped chapter from {orig_end_chap} to {end_chap}")

    # Expand chapter-only to full verse range
    if start_verse is None:
        start_verse = 1
    if end_verse is None:
        end_verse = get_verse_count(osis_key, end_chap) or 1

    # Validate verses in strict mode
    if mode == "strict":
        sv_count = get_verse_count(osis_key, start_chap)
        ev_count = get_verse_count(osis_key, end_chap)
        if start_verse is not None and sv_count is not None and start_verse > sv_count:
            return ResolvedRange(
                start=None,
                end=None,
                not_found=(
                    f"Verse {start_verse} does not exist in {display_name} {start_chap} (only {sv_count} verse{'s' if sv_count!=1 else ''})"
                ),
            )
        if end_verse is not None and ev_count is not None and end_verse > ev_count:
            return ResolvedRange(
                start=None,
                end=None,
                not_found=(
                    f"Verse {end_verse} does not exist in {display_name} {end_chap} (only {ev_count} verse{'s' if ev_count!=1 else ''})"
                ),
            )

    # Clamp verses in loose mode
    orig_start_verse = start_verse
    orig_end_verse = end_verse
    sv_clamped, sv_warn = _clamp_verse(osis_key, start_chap, start_verse)
    ev_clamped, ev_warn = _clamp_verse(osis_key, end_chap, end_verse)
    if sv_warn:
        warnings.append(sv_warn)
        start_verse = sv_clamped
    if ev_warn:
        warnings.append(ev_warn)
        end_verse = ev_clamped

    start_osis = _format_osis(osis_key, start_chap, start_verse)
    end_osis = _format_osis(osis_key, end_chap, end_verse)

    warning_text = "; ".join(warnings) if warnings else None

    return ResolvedRange(
        start=start_osis, end=end_osis, fuzzy_ratio=fuzzy_ratio, warning=warning_text
    )


def resolve_parsed(
    parsed_refs: list[ParsedRef], mode: Literal["loose", "strict"] = "loose"
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
            results.append(
                ResolvedRange(
                    start=None, end=None, not_found=f"Unknown book in '{ref.raw}'"
                )
            )
            continue

        # Try to normalize the book name to OSIS
        normalized = normalize_book(ref.book_key, mode=mode)
        osis_key = normalized.key

        if osis_key is None:
            results.append(
                ResolvedRange(
                    start=None, end=None, not_found=f"Unknown book '{ref.book_key}'"
                )
            )
            continue

        # Get book metadata for verse counts
        meta = get_book_metadata(osis_key)
        if meta is None:
            results.append(
                ResolvedRange(
                    start=None, end=None, not_found=f"No metadata for '{osis_key}'"
                )
            )
            continue

        # Delegate detailed resolution (including clamping/validation) to helper
        fuzzy_ratio = None
        if (
            not normalized.is_exact
            and normalized.candidates
            and len(normalized.candidates) > 0
        ):
            fuzzy_ratio = normalized.candidates[0].score

        rr = resolve_ref_with_book(ref, osis_key, fuzzy_ratio=fuzzy_ratio, mode=mode)
        results.append(rr)

    return results
