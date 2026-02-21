"""Tests for type definitions."""

from scripture_ref_parser.types import (
    Token,
    NormalizedBook,
    ParsedRef,
    ResolvedRange,
    CanonCandidate,
)


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


def test_canon_candidate_creation():
    cc = CanonCandidate(key="Gen", score=95)
    assert cc.key == "Gen"
    assert cc.score == 95
