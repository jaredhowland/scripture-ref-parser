# parse-scripture-refs

A modular Python library and CLI that parses scripture references (KJV OT/NT and LDS canon: Book of Mormon, Doctrine & Covenants, Pearl of Great Price) and returns OSIS-based ranges.

## Installation

```bash
pip install parse-scripture-refs
```

Or with `uv`:

```bash
uv add parse-scripture-refs
```

## Usage

### Python API

```python
from scripture_ref_parser import parse_references

# Simple reference
results = parse_references("Gen 1:1")
# [{'start': 'Gen.1.1', 'end': 'Gen.1.1'}]

# Multiple references with ranges
results = parse_references("Gen 1:1-3; Exod 2:1")
# [{'start': 'Gen.1.1', 'end': 'Gen.1.3'}, {'start': 'Exod.2.1', 'end': 'Exod.2.1'}]

# LDS canon references
results = parse_references("1 Ne. 3:7")
# [{'start': '1Ne.3.7', 'end': '1Ne.3.7'}]

# Fuzzy matching (default: loose mode)
results = parse_references("Exodis 1:1", mode="loose")
# [{'start': 'Exod.1.1', 'end': 'Exod.1.1', 'fuzzy_ratio': 83}]

# Strict mode (no fuzzy matching)
results = parse_references("Exodis 1:1", mode="strict")
# [{'start': None, 'end': None, 'not_found': "Unknown book 'Exodis'"}]

# Chapter expansion
results = parse_references("Gen 1")
# [{'start': 'Gen.1.1', 'end': 'Gen.1.31'}]
```

### CLI

```bash
scripture-ref-parser "Gen 1:1-3; 1 Ne. 3:7"
# [{"start": "Gen.1.1", "end": "Gen.1.3"}, {"start": "1Ne.3.7", "end": "1Ne.3.7"}]

# With strict mode
scripture-ref-parser "Gen 1:1" --mode strict

# With pretty output
scripture-ref-parser "Gen 1:1" --pretty

# Get all fuzzy candidates
scripture-ref-parser "E 1:1" --all-candidates
```

## Supported Canons

- **KJV Old Testament** (Genesis - Malachi)
- **KJV New Testament** (Matthew - Revelation)
- **Book of Mormon** (1 Nephi - Moroni)
- **Doctrine & Covenants** (Sections 1-138)
- **Pearl of Great Price** (Moses, Abraham, JS-Matthew, JS-History, Articles of Faith)
- **JST Appendix**

## Pipeline Architecture

The parser operates in four stages:

1. **Tokenize**: Convert raw text into tokens (book names, numbers, separators)
2. **Normalize**: Map book names/abbreviations to canonical OSIS keys
3. **Parse**: Convert tokens into structured chapter:verse references
4. **Resolve**: Expand references to complete OSIS ranges

## Development

```bash
# Run tests
uvx pytest

# Format code
uvx ruff format

# Lint
uvx ruff check --fix

# Type check
uvx ty check
```

## License

MIT
