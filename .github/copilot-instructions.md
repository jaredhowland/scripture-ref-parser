# Scripture Ref Parser — Copilot Instructions

## Project Purpose

A modular Python library and CLI that parses scripture references (KJV OT/NT and LDS canon: Book of Mormon, Doctrine & Covenants, Pearl of Great Price) and returns OSIS-based ranges. Pipeline stages (tokenize → normalize → parse → resolve) are intentionally separable and independently testable.

---

## HARD RULES — Always Enforced

### Command Execution

- **ALWAYS** run Python via `uv run …` or `uvx …`
- **ALWAYS** run tests with `uv run pytest` (requires package to be installed)
- **ALWAYS** format with `uvx ruff format`
- **ALWAYS** lint/fix with `uvx ruff check --fix`
- **ALWAYS** type-check with `uvx ty check`
- **NEVER** invoke `python`, `python3`, or `pytest` directly

### File Placement

- Write all temp scripts and debug outputs to `tmp/` (gitignored)
- Write all log files to `logs/` (gitignored)
- **NEVER** commit debug or temp files to the repo

### Test Structure

- Place all tests under `tests/`
- Separate into `tests/unit/` and `tests/integration/`
- Run the full suite with `uv run pytest`

---

## Tech Stack

| Tool | Version / Notes |
|------|----------------|
| Python | `>=3.12` |
| Package manager | `uv` |
| Testing | `pytest` (via `uvx pytest`) |
| Linting/formatting | `ruff` (via `uvx ruff`) |
| Type checking | `ty` (via `uvx ty check`) |
| CLI framework | `click` |
| Fuzzy matching | `rapidfuzz` |

---

## Source Layout

All production code lives under `src/scripture_ref_parser/`:

```
src/scripture_ref_parser/
  tokenize/tokenizer.py    # Stage 1 — tokenize
  normalize/normalize.py   # Stage 2 — normalize
  parse/parser.py          # Stage 3 — parse
  resolve/resolver.py      # Stage 4 — resolve
  api/__init__.py          # Public API orchestration
  cli/cli.py               # CLI entrypoint
  data/
    canon_index.json       # Book registry
    canon/                 # Per-work JSON files
```

---

## Pipeline Stages

### Stage 1 — Tokenize (`tokenize/tokenizer.py`)
- Preserve punctuation and separators: `;`, `,`, `—`, `–`
- Yield candidate reference tokens for downstream stages

### Stage 2 — Normalize (`normalize/normalize.py`)
- Map book names, aliases, abbreviations, and fuzzy matches to canonical keys
- Load book registry from `data/canon_index.json`
- Support two modes — **default is `loose`**:
  - `loose`: fuzzy matching allowed
  - `strict`: exact/known alias match only; unknown books return an error
- Strip spaces, periods, and punctuation; convert to lowercase before matching

### Stage 3 — Parse (`parse/parser.py`)
- Parse chapter:verse ranges into structured `(start, end)` tuples
- Handle: single refs, chapter-only, chapter:verse, ranges, cross-book ranges, comma/semicolon lists

### Stage 4 — Resolve (`resolve/resolver.py`)
- Map parsed tuples to OSIS identifiers (e.g., `Gen.1.1`)
- Expand chapter-only bounds to full verse ranges using `num_verses` from canon JSON files
- Validate all references against canon data

### Public API (`api/__init__.py`)

```python
parse_references(text, mode='loose', all_candidates=False)
```

### CLI (`cli/cli.py`)

- Entrypoint: `scripture-ref-parser` (or `uvx --with-editable . -- scripture-ref-parser`)
- Default mode: `loose`
- Flag `--all-candidates`: return all fuzzy-match candidates instead of only the top match

---

## Output Format (OSIS)

### Loose mode — `"Gen 1:1-4; 1 Ne. 3:12; Exodis 1:2-22"`

```json
[
  { "start": "Gen.1.1",  "end": "Gen.1.4" },
  { "start": "1Ne.3.12", "end": "1Ne.3.12" },
  { "start": "Exod.1.2", "end": "Exod.1.22", "fuzzy_ratio": 83 }
]
```

### Loose + `--all-candidates` — `"Gen 1:1-4; 1 Ne. 3:12; E 1:2-22"`

```json
[
  { "start": "Gen.1.1",  "end": "Gen.1.4" },
  { "start": "1Ne.3.12", "end": "1Ne.3.12" },
  {
    "options": [
      { "start": "Exod.1.2",  "end": "Exod.1.22",  "fuzzy_ratio": 83 },
      { "start": "Ether.1.2", "end": "Ether.1.22", "fuzzy_ratio": 64 }
    ]
  }
]
```

### Strict mode — `"Gen 1:1-4; 1 Ne. 3:12; Exodis 1.2-22"`

```json
[
  { "start": "Gen.1.1",  "end": "Gen.1.4" },
  { "start": "1Ne.3.12", "end": "1Ne.3.12" },
  { "start": null, "end": null, "not_found": "Unknown book 'Exodis'" }
]
```

---

## Data Model

Canon JSON files live in `src/scripture_ref_parser/data/canon/`:

| File | Contents |
|------|----------|
| `OldTestament.json` | KJV OT versification |
| `NewTestament.json` | KJV NT versification |
| `BibleOrgSys.json` | Full Bible versification (derived from BibleOrgSys XML) |
| `BookOfMormon.json` | Book of Mormon |
| `DoctrineAndCovenants.json` | Doctrine & Covenants |
| `PearlOfGreatPrice.json` | Pearl of Great Price |
| `JstAppendix.json` | JST Appendix |

All canon JSON files are normalized. Example book entry:

```json
{
  "Genesis": {
    "osis_abbr": "Gen",
    "names": ["Genesis", "Gen"],
    "abbrs": ["Ge", "Gene"],
    "num_chaps": 50,
    "num_verses": { "1": 31, "2": 25, "...": "..." }
  }
}
```

---

## Extensibility

- **Add a new work:** create `data/canon/<work>.json`, then register it in `data/canon_index.json`
- **Add a new language/locale:** create `normalize/lang/<lang>.py`
