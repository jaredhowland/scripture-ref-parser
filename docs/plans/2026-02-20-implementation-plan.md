# [Scripture Reference Parser] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a modular 4-stage scripture reference parser that outputs OSIS ranges and supports `loose` fuzzy matching and `strict` matching.

**Architecture:** A pipeline of four stages—tokenize, normalize, parse, resolve—each with small, typed interfaces. Provide a thin public API and CLI wrapper. Tests drive development (TDD).

**Tech Stack:** Python >=3.12, `uv`-managed commands, `pytest` (via `uvx pytest`), `ruff` (format/check), `ty` for type checking, `rapidfuzz` for fuzzy matching, `click` for CLI.

---
I'm using the writing-plans skill to create the implementation plan.

### Task grouping and workflow notes

- Work in the repository root worktree. Use `uvx` for Python commands.
- Follow TDD: write a failing unit test, run it, implement minimal code, run tests, commit. Each plan step is short (~2–5 minutes).
- File paths below reference the existing repo layout: parse-scripture-refs and tests.

---

### Task 1: Project scaffolding & test harness

**Files:**

- Modify: none
- Create: `tests/unit/test_smoke_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_smoke_pipeline.py
def test_pipeline_imports():
    import parse_scripture_refs
    assert hasattr(parse_scripture_refs.api, "parse_references")
```

**Step 2: Run test (verify fails if module path differs)**
Run: `uvx pytest tests/unit/test_smoke_pipeline.py -q`
Expected: FAIL (module import may fail until package exports exist)

**Step 3: Minimal implementation / adjustments**

- (If import path differs, adjust: add top-level `src/parse-scripture-refs/api/__init__.py` exports as necessary in later tasks.)

**Step 4: Run tests**
Run: `uvx pytest tests/unit/test_smoke_pipeline.py -q`
Expected: PASS once API exists (this is a gate test for later tasks)

**Step 5: Commit**

```bash
git add tests/unit/test_smoke_pipeline.py
git commit -m "test: add smoke test for pipeline imports"
```

---

### Task 2: Tokenizer unit tests

**Files:**

- Create: `tests/unit/test_tokenizer.py`
- Create: `src/parse-scripture-refs/tokenize/tokenizer.py` (implementation placeholder)

**Step 1: Write failing test**

```python
# tests/unit/test_tokenizer.py
from parse_scripture_refs.tokenize.tokenizer import tokenize

def test_simple_tokenize():
    tokens = tokenize("Gen 1:1-3; Exod. 2")
    assert any(t['type']=="BOOK" and "gen" in t['text'].lower() for t in tokens)
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_tokenizer.py::test_simple_tokenize -q`
Expected: FAIL (tokenize not implemented)

**Step 3: Implement minimal tokenizer**

- Create `src/parse-scripture-refs/tokenize/tokenizer.py` with a simple `tokenize(text)` that yields a list of token dicts (BOOK, NUM, SEP).
  - Minimal: split on whitespace and punctuation returning simple tokens to satisfy the test.

**Step 4: Run test**
Run: `uvx pytest tests/unit/test_tokenizer.py::test_simple_tokenize -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/tokenize/tokenizer.py tests/unit/test_tokenizer.py
git commit -m "feat(tokenize): add basic tokenizer and unit test"
```

---

### Task 3: Normalizer unit tests (strict + loose)

**Files:**

- Create: `tests/unit/test_normalize.py`
- Create: `src/parse-scripture-refs/normalize/normalize.py`

**Step 1: Write failing test**

```python
# tests/unit/test_normalize.py
from parse_scripture_refs.normalize.normalize import normalize_book

def test_normalize_strict_known():
    result = normalize_book("Genesis", mode="strict")
    assert result.key == "Genesis" or result.key == "Gen"
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_normalize.py::test_normalize_strict_known -q`
Expected: FAIL

**Step 3: Implement minimal normalize_book**

- Load canon_index.json and map a small subset; return a small NormalizedBook object.

**Step 4: Run test**
Run: `uvx pytest tests/unit/test_normalize.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/normalize/normalize.py tests/unit/test_normalize.py
git commit -m "feat(normalize): add book normalizer and tests (strict)"
```

---

### Task 4: Fuzzy matching (loose) tests

**Files:**

- Modify: `tests/unit/test_normalize.py` (add test)
- Create: `src/parse-scripture-refs/normalize/_fuzzy.py` (helper for fuzzy)

**Step 1: Write failing test**

```python
def test_normalize_loose_fuzzy():
    result = normalize_book("Exodis", mode="loose")
    assert result.candidates and any(c['key']=="Exod" for c in result.candidates)
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_normalize.py::test_normalize_loose_fuzzy -q`
Expected: FAIL

**Step 3: Implement minimal fuzzy lookup using rapidfuzz**

- Add dependency note in plan; implementation will call `rapidfuzz.fuzz.ratio`.

**Step 4: Run test**
Run: `uvx pytest tests/unit/test_normalize.py::test_normalize_loose_fuzzy -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/normalize/_fuzzy.py src/parse-scripture-refs/normalize/normalize.py tests/unit/test_normalize.py
git commit -m "feat(normalize): add loose fuzzy matching"
```

---

### Task 5: Parser tests (chapter/verse ranges)

**Files:**

- Create: `tests/unit/test_parser.py`
- Create: `src/parse-scripture-refs/parse/parser.py`

**Step 1: Write failing test**

```python
# tests/unit/test_parser.py
from parse_scripture_refs.parse.parser import parse_tokens
def test_parse_chapter_verse_range():
    tokens = [{'type':'BOOK','text':'Gen'},{'type':'NUM','text':'1:1-3'}]
    parsed = parse_tokens(tokens)
    assert parsed[0]['start'] == (1,1) and parsed[0]['end'] == (1,3)
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_parser.py::test_parse_chapter_verse_range -q`
Expected: FAIL

**Step 3: Implement minimal parser to extract simple ranges**

- Implement `parse_tokens` to handle `chap:verse-verse` syntax.

**Step 4: Run test**
Run: `uvx pytest tests/unit/test_parser.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/parse/parser.py tests/unit/test_parser.py
git commit -m "feat(parse): add parser for simple chapter:verse ranges"
```

---

### Task 6: Resolver tests (expand chapter-only, validate bounds)

**Files:**

- Create: `tests/unit/test_resolver.py`
- Create: `src/parse-scripture-refs/resolve/resolver.py`

**Step 1: Write failing test**

```python
# tests/unit/test_resolver.py
from parse_scripture_refs.resolve.resolver import resolve_parsed
def test_resolve_chapter_only():
    parsed = {'book_key':'Gen','start':(1,None),'end':(1,None)}
    resolved = resolve_parsed([parsed])
    assert resolved[0]['start'] == "Gen.1.1" and resolved[0]['end'] == "Gen.1.31"
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_resolver.py::test_resolve_chapter_only -q`
Expected: FAIL

**Step 3: Implement minimal resolver using `num_verses` from `data/canon/*.json`**

- Load `OldTestament.json` and map `num_verses["1"] == 31` for test.

**Step 4: Run test**
Run: `uvx pytest tests/unit/test_resolver.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/resolve/resolver.py tests/unit/test_resolver.py
git commit -m "feat(resolve): add resolver to expand chapter-only refs"
```

---

### Task 7: Full pipeline integration test

**Files:**

- Create: `tests/integration/test_full_pipeline.py`
- Modify: `src/parse-scripture-refs/api/__init__.py` (create API orchestration)

**Step 1: Write failing integration test**

```python
# tests/integration/test_full_pipeline.py
from parse_scripture_refs.api import parse_references
def test_integration_basic():
    out = parse_references("Gen 1:1-2; Exod 1:1", mode="loose")
    assert isinstance(out, list) and out[0]['start'].startswith("Gen.")
```

**Step 2: Run test**
Run: `uvx pytest tests/integration/test_full_pipeline.py -q`
Expected: FAIL

**Step 3: Implement API orchestration**

- Implement `api.__init__.py` that calls tokenizer → normalizer → parser → resolver and returns results.

**Step 4: Run tests (integration + unit)**
Run: `uvx pytest tests/unit tests/integration -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/api/__init__.py tests/integration/test_full_pipeline.py
git commit -m "feat(api): add pipeline orchestration and integration test"
```

---

### Task 8: CLI wrapper

**Files:**

- Create: `src/parse-scripture-refs/cli/cli.py`
- Create: `tests/integration/test_cli.py`

**Step 1: Write failing test**

```python
# tests/integration/test_cli.py
import subprocess, json
out = subprocess.check_output(["uvx", "--", "scripture-ref-parser", "Gen 1:1-2", "--mode", "loose"])
data = json.loads(out)
assert data[0]['start'].startswith("Gen.")
```

**Step 2: Run test**
Run: `uvx pytest tests/integration/test_cli.py -q`
Expected: FAIL

**Step 3: Implement CLI with Click to call `parse_references` and emit JSON**

- Entry point name: `scripture-ref-parser`

**Step 4: Run test**
Run: `uvx pytest tests/integration/test_cli.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/cli/cli.py tests/integration/test_cli.py
git commit -m "feat(cli): add CLI wrapper and tests"
```

---

### Task 9: Edge cases, error objects, and --all-candidates

**Files:**

- Modify: `src/parse-scripture-refs/normalize/normalize.py`
- Modify: `src/parse-scripture-refs/api/__init__.py`
- Create: `tests/unit/test_all_candidates.py`

**Step 1: Write failing test**

```python
# tests/unit/test_all_candidates.py
from parse_scripture_refs.api import parse_references
out = parse_references("E 1.2-3", mode="loose", all_candidates=True)
assert 'options' in out[-1] or out[-1].get('fuzzy_ratio') is not None
```

**Step 2: Run test**
Run: `uvx pytest tests/unit/test_all_candidates.py -q`
Expected: FAIL

**Step 3: Implement candidate option branch in API to include `options` when requested**

**Step 4: Run tests**
Run: `uvx pytest tests/unit -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parse-scripture-refs/api/__init__.py src/parse-scripture-refs/normalize/normalize.py tests/unit/test_all_candidates.py
git commit -m "feat(api): support --all-candidates and options in output"
```

---

### Task 10: CI / lint / format / type checks (plans only)

**Files:**

- Create: `docs/plans/ci-checklist.md` (optional)
- No code changes required in this plan step.

**Step 1: Document commands to run locally**
Commands:

```bash
uvx ruff format
uvx ruff check --fix
uvx ty check
uvx pytest
```

Expected: All commands succeed locally; CI will mirror these checks.

---

After you review and approve, I can:

- refine tasks or split them finer, or
- prepare to hand off to execution (subagent-driven) to implement step-by-step.
