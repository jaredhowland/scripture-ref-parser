"""Tests for the parser stage."""
from scripture_ref_parser.parse.parser import parse_tokens
from scripture_ref_parser.types import Token, ParsedRef


def test_parse_simple_chapter_verse():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 1
    assert parsed[0].book_key == "Gen"
    assert parsed[0].start == (1, 1)
    assert parsed[0].end == (1, 1)


def test_parse_verse_range():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1-3", span=(4, 9)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, 1)
    assert parsed[0].end == (1, 3)


def test_parse_chapter_only():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1", span=(4, 5)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, None)
    assert parsed[0].end == (1, None)


def test_parse_chapter_range():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1-3", span=(4, 7)),
    ]
    parsed = parse_tokens(tokens)
    assert parsed[0].start == (1, None)
    assert parsed[0].end == (3, None)


def test_parse_multiple_references():
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
        Token(type="SEP", text=";", span=(7, 8)),
        Token(type="BOOK", text="Exod", span=(9, 13)),
        Token(type="NUM", text="2:3", span=(14, 17)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 2
    assert parsed[0].book_key == "Gen"
    assert parsed[1].book_key == "Exod"


def test_parse_implicit_book_continuation():
    # "Gen 1:1, 2:3" - second ref uses same book
    tokens = [
        Token(type="BOOK", text="Gen", span=(0, 3)),
        Token(type="NUM", text="1:1", span=(4, 7)),
        Token(type="SEP", text=",", span=(7, 8)),
        Token(type="NUM", text="2:3", span=(9, 12)),
    ]
    parsed = parse_tokens(tokens)
    assert len(parsed) == 2
    assert parsed[0].book_key == "Gen"
    assert parsed[1].book_key == "Gen"  # Inherited from previous
