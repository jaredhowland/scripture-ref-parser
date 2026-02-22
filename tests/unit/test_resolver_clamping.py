"""Tests for chapter/verse clamping behavior in resolver and API."""

from scripture_ref_parser.api import parse_references


def test_loose_mode_clamps_chapter():
    results = parse_references("4 Nephi 3", mode="loose")
    assert len(results) == 1
    r = results[0]
    assert r["start"] == "4Ne.1.1"
    assert r["end"] == "4Ne.1.49"
    assert "warning" in r and "Clamped chapter" in r["warning"]


def test_strict_mode_rejects_out_of_bounds_chapter():
    results = parse_references("4 Nephi 3", mode="strict")
    assert len(results) == 1
    r = results[0]
    assert r["start"] is None
    assert r["end"] is None
    assert r.get("not_found") is not None
    assert "Chapter 3" in r["not_found"]


def test_loose_mode_clamps_verse_range_end():
    results = parse_references("4 Nephi 1:1-50", mode="loose")
    assert len(results) == 1
    r = results[0]
    assert r["start"] == "4Ne.1.1"
    assert r["end"] == "4Ne.1.49"
    assert "warning" in r and "Clamped verse" in r["warning"]
