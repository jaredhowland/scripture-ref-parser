"""Public API for scripture reference parsing."""

from typing import Literal

from scripture_ref_parser.data.loader import get_book_metadata, get_verse_count
from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.parse.parser import parse_tokens
from scripture_ref_parser.resolve.resolver import resolve_parsed
from scripture_ref_parser.tokenize.tokenizer import tokenize


def _format_osis(book: str, chapter: int, verse: int) -> str:
    """Format an OSIS identifier."""
    return f"{book}.{chapter}.{verse}"


def _resolve_ref_with_book(
    parsed_ref, osis_key: str, fuzzy_ratio: int | None = None
) -> dict | None:
    """Resolve a parsed ref with a specific OSIS book key."""
    meta = get_book_metadata(osis_key)
    if meta is None:
        return None

    start_chap, start_verse = parsed_ref.start
    end_chap, end_verse = parsed_ref.end

    # Expand chapter-only to full verse range
    if start_verse is None:
        start_verse = 1
    if end_verse is None:
        end_verse = get_verse_count(osis_key, end_chap) or 1

    result: dict = {
        "start": _format_osis(osis_key, start_chap, start_verse),
        "end": _format_osis(osis_key, end_chap, end_verse),
    }
    if fuzzy_ratio is not None:
        result["fuzzy_ratio"] = fuzzy_ratio
    return result


def parse_references(
    text: str,
    mode: Literal["loose", "strict"] = "loose",
    all_candidates: bool = False,
) -> list[dict]:
    """Parse scripture reference text into OSIS ranges.

    Args:
        text: Freeform scripture reference text (e.g., "Gen 1:1-3; 1 Ne. 3:12")
        mode: "loose" (fuzzy matching) or "strict" (exact match only)
        all_candidates: If True, return all fuzzy match candidates for ambiguous refs

    Returns:
        List of dicts with 'start', 'end' keys (and optionally 'fuzzy_ratio', 'not_found', 'options')
    """
    # Stage 1: Tokenize
    tokens = tokenize(text)

    # Stage 2+3: Parse (includes normalization)
    parsed = parse_tokens(tokens)

    # For all_candidates mode, handle each ref specially
    if all_candidates:
        results: list[dict] = []
        for ref in parsed:
            if ref.book_key is None:
                results.append(
                    {
                        "start": None,
                        "end": None,
                        "not_found": f"Unknown book in '{ref.raw}'",
                    }
                )
                continue

            normalized = normalize_book(ref.book_key, mode=mode, all_candidates=True)
            if normalized.key is None:
                results.append(
                    {
                        "start": None,
                        "end": None,
                        "not_found": f"Unknown book '{ref.book_key}'",
                    }
                )
                continue

            # Build options for each candidate
            options = []
            if normalized.candidates:
                for candidate in normalized.candidates:
                    resolved = _resolve_ref_with_book(
                        ref, candidate.key, candidate.score
                    )
                    if resolved:
                        options.append(resolved)

            if len(options) > 1:
                # Multiple candidates - return options array
                results.append({"options": options})
            elif len(options) == 1:
                # Single candidate - return it directly (strip fuzzy_ratio for exact match)
                result = options[0]
                if normalized.is_exact:
                    result.pop("fuzzy_ratio", None)
                results.append(result)
            else:
                results.append(
                    {
                        "start": None,
                        "end": None,
                        "not_found": f"No metadata for '{normalized.key}'",
                    }
                )

        return results

    # Standard mode (no all_candidates)
    # Stage 4: Resolve
    resolved = resolve_parsed(parsed, mode=mode)

    # Convert to output format
    results = []
    for item in resolved:
        result: dict = {
            "start": item.start,
            "end": item.end,
        }

        if item.fuzzy_ratio is not None:
            result["fuzzy_ratio"] = item.fuzzy_ratio

        if item.not_found is not None:
            result["not_found"] = item.not_found

        results.append(result)

    return results


__all__ = ["parse_references"]
