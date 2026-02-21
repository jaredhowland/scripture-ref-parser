"""Tests for the resolver stage."""

from scripture_ref_parser.resolve.resolver import resolve_parsed
from scripture_ref_parser.types import ParsedRef


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
