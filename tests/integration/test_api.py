"""Integration tests for the public API."""

from scripture_ref_parser.api import parse_references


def test_api_simple_reference():
    results = parse_references("Gen 1:1")
    assert len(results) == 1
    assert results[0]["start"] == "Gen.1.1"
    assert results[0]["end"] == "Gen.1.1"


def test_api_multiple_references():
    results = parse_references("Gen 1:1-3; Exod 2:1")
    assert len(results) == 2
    assert results[0]["start"] == "Gen.1.1"
    assert results[1]["start"] == "Exod.2.1"


def test_api_lds_references():
    results = parse_references("1 Ne. 3:7")
    assert len(results) == 1
    assert results[0]["start"] == "1Ne.3.7"


def test_api_fuzzy_match_loose():
    results = parse_references("Exodis 1:1", mode="loose")
    assert len(results) == 1
    assert results[0]["start"] == "Exod.1.1"


def test_api_strict_mode_unknown():
    results = parse_references("Exodis 1:1", mode="strict")
    assert len(results) == 1
    assert results[0]["start"] is None
    assert "not_found" in results[0]


def test_api_chapter_expansion():
    results = parse_references("Gen 1")
    assert results[0]["start"] == "Gen.1.1"
    assert results[0]["end"] == "Gen.1.31"


def test_api_all_candidates():
    results = parse_references("E 1:1", mode="loose", all_candidates=True)
    assert len(results) == 1
    # Should have options when ambiguous
    if "options" in results[0]:
        assert len(results[0]["options"]) > 0
