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
