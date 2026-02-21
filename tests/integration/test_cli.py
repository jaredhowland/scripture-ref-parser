"""Integration tests for CLI."""

import json
import subprocess


def test_cli_simple():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Gen 1:1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Gen.1.1"


def test_cli_strict_mode():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Gen 1:1", "--mode", "strict"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Gen.1.1"


def test_cli_loose_mode():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Exodis 1:1", "--mode", "loose"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Exod.1.1"


def test_cli_all_candidates():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "E 1:1", "--all-candidates"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) >= 1


def test_cli_pretty_output():
    result = subprocess.run(
        ["uv", "run", "scripture-ref-parser", "Gen 1:1", "--pretty"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Pretty output should have newlines
    assert "\n" in result.stdout
    data = json.loads(result.stdout)
    assert data[0]["start"] == "Gen.1.1"
