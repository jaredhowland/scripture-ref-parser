"""Tests for canon data loading."""
from scripture_ref_parser.data.loader import (
    load_canon_index,
    load_canon_file,
    get_book_metadata,
    get_verse_count,
)


def test_load_canon_index():
    index = load_canon_index()
    assert isinstance(index, dict)
    assert index.get("gen") == "Gen"
    assert index.get("genesis") == "Gen"
    assert index.get("1nephi") == "1Ne"


def test_load_canon_file_old_testament():
    data = load_canon_file("OldTestament")
    assert "Gen" in data
    assert data["Gen"]["num_chaps"] == 50


def test_get_book_metadata():
    meta = get_book_metadata("Gen")
    assert meta is not None
    assert meta["num_chaps"] == 50
    assert meta["num_verses"]["1"] == 31


def test_get_verse_count():
    count = get_verse_count("Gen", 1)
    assert count == 31
    count = get_verse_count("Gen", 50)
    assert count == 26


def test_get_verse_count_invalid():
    count = get_verse_count("Gen", 999)
    assert count is None
