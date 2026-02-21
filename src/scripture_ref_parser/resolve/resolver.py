"""Resolver stage: expands parsed refs to OSIS identifiers."""

from scripture_ref_parser.data.loader import get_book_metadata, get_verse_count
from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.types import ParsedRef, ResolvedRange


def _format_osis(book: str, chapter: int, verse: int) -> str:
    """Format an OSIS identifier."""
    return f"{book}.{chapter}.{verse}"


def resolve_parsed(
    parsed_refs: list[ParsedRef], mode: str = "loose"
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

        results.append(
            ResolvedRange(start=start_osis, end=end_osis, fuzzy_ratio=fuzzy_ratio)
        )

    return results
