# scripture-ref-parser

A modular Python library and CLI that parses scripture references (KJV OT/NT and LDS canon: Book of Mormon, Doctrine & Covenants, Pearl of Great Price) and returns OSIS-based ranges.

## Installation

```bash
pip install scripture-ref-parser
```

Or with `uv`:

```bash
uv add scripture-ref-parser
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

# Fuzzy matching (includes fuzzy_ratio)
scripture-ref-parser "Exodis 1:1"
# [{"start": "Exod.1.1", "end": "Exod.1.1", "fuzzy_ratio": 83}]

# With strict mode
scripture-ref-parser "Gen 1:1" --mode strict
# Or use the shortcut flags:
scripture-ref-parser "Gen 1:1" --strict
scripture-ref-parser "Exodis 1:1" --loose

# With pretty output
scripture-ref-parser "Gen 1:1" --pretty

# Get all fuzzy candidates
scripture-ref-parser "E 1:1" --all-candidates

# Help

Use the `--help` flag to display a comprehensive, example-driven help message describing available modes and flags. The help output includes short, copyable examples and explains the differences between `loose` (fuzzy) and `strict` matching.

Note: `--loose` and `--strict` are provided as shorthand flags and are mutually exclusive. They are equivalent to `--mode loose` and `--mode strict`, respectively.

```bash
scripture-ref-parser --help
# Displays usage, options (including `--mode`, `--all-candidates`, `--pretty`),
# and examples such as:
#   scripture-ref-parser "Gen 1:1-3; 1 Ne. 3:7" --pretty
#   scripture-ref-parser "E 1:1" --all-candidates --pretty
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
uv run pytest

# Format code
uvx ruff format

# Lint
uvx ruff check --fix

# Type check
uvx ty check

# Edit package itself
uv pip install -e .
```

## License

MIT
