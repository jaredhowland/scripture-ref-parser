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
    result = normalize_book("Exodiss", mode="loose", all_candidates=True)
    assert result.candidates is not None
    # Should have multiple candidates for typo


def test_normalize_loose_scores():
    result = normalize_book("Exodis", mode="loose", all_candidates=True)
    if result.candidates:
        for candidate in result.candidates:
            assert candidate.score > 0
            assert candidate.score <= 100
