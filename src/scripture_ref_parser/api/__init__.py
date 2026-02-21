"""Public API for scripture reference parsing."""


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
        canon_books: Optional list of canon files to restrict search
        all_candidates: If True, return all fuzzy match candidates

    Returns:
        List of OSIS range dicts with 'start' and 'end' keys
    """
    raise NotImplementedError("Pipeline not yet implemented")


__all__ = ["parse_references"]
