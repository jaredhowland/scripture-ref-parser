"""Tests for the tokenizer stage."""
from scripture_ref_parser.tokenize.tokenizer import tokenize
from scripture_ref_parser.types import Token


def test_tokenize_simple_reference():
    tokens = tokenize("Gen 1:1")
    assert len(tokens) >= 2
    # Should have a BOOK-like token and NUM tokens
    texts = [t.text.lower() for t in tokens]
    assert "gen" in texts or any("gen" in t for t in texts)


def test_tokenize_preserves_separators():
    tokens = tokenize("Gen 1:1; Exod 2:3")
    types = [t.type for t in tokens]
    assert "SEP" in types  # semicolon is a separator


def test_tokenize_handles_ranges():
    tokens = tokenize("Gen 1:1-3")
    # Should capture the range
    texts = [t.text for t in tokens]
    combined = "".join(texts)
    assert "1" in combined and "3" in combined


def test_tokenize_handles_periods():
    tokens = tokenize("Gen. 1:1")
    # Period after abbreviation should not break reference
    texts = [t.text.lower() for t in tokens]
    assert any("gen" in t for t in texts)


def test_tokenize_handles_lds_references():
    tokens = tokenize("1 Ne. 3:7")
    texts = [t.text for t in tokens]
    combined = " ".join(texts).lower()
    assert "1" in combined and ("ne" in combined or "nephi" in combined)


def test_tokenize_span_tracking():
    text = "Gen 1:1"
    tokens = tokenize(text)
    for token in tokens:
        start, end = token.span
        assert text[start:end] == token.text
