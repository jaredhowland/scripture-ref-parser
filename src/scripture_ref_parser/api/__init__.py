"""Public API for scripture reference parsing."""

from scripture_ref_parser.normalize.normalize import normalize_book
from scripture_ref_parser.parse.parser import parse_tokens
from scripture_ref_parser.resolve.resolver import resolve_parsed
from scripture_ref_parser.tokenize.tokenizer import tokenize


def parse_references(
    text: str,
    mode: str = "loose",
    canon_books: list[str] | None = None,
    all_candidates: bool = False,
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
    parsed = parse_tokens(tokens)

    # Track candidates for all_candidates mode
    candidates_map: dict[int, list] = {}
    if all_candidates:
        for i, ref in enumerate(parsed):
            if ref.book_key:
                normalized = normalize_book(ref.book_key, mode=mode, all_candidates=True)
                if normalized.candidates and len(normalized.candidates) > 1:
                    candidates_map[i] = normalized.candidates

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
        if all_candidates and i in candidates_map:
            options = []
            for candidate in candidates_map[i]:
                options.append(
                    {
                        "start": result["start"],
                        "end": result["end"],
                        "fuzzy_ratio": candidate.score,
                    }
                )
            if len(options) > 1:
                result["options"] = options

        results.append(result)

    return results


__all__ = ["parse_references"]
