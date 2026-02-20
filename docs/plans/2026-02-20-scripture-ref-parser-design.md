## Plan: Scripture Reference Parser Design

TL;DR

- Purpose: Produce a modular, testable pipeline that converts freeform scripture reference text into OSIS ranges for supported canons (KJV, Book of Mormon, D&C, PGP).
- Approach: 4-stage pipeline (tokenize → normalize → parse → resolve) with small, well-typed interfaces between stages, a canonical data layer for versification, and a thin public API + CLI.

Steps

- Architecture
  - Stages:
    - Tokenize: produce candidate tokens (book candidates, numeric tokens, separators) while preserving punctuation and separators (`; , — –`).
    - Normalize: map book-name tokens to canonical book keys using `canon_index.json` and per-work canon files; supports `loose` (fuzzy) and `strict` modes.
    - Parse: convert normalized tokens into structured ranges and cross-book constructs (start/end tuples).
    - Resolve: expand chapter-only references using `num_verses` and emit OSIS `start`/`end` identifiers; validate bounds.
  - Orchestration: public `api.parse_references(text, mode='loose', canon_books=None)` will run the stages in sequence and return structured OSIS ranges (and candidate options when requested).
  - CLI: `scripture-ref-parser` exposes the API with flags `--mode` (`loose|strict`), `--all-candidates`, and `--canon`.

- Pipeline interfaces (typed)
  - Token: { type: "BOOK"|"NUM"|"SEP"|"PUNC", text: str, span: (int,int) }
  - NormalizedBook: { key: str|null, candidates?: [{ key, score }], mode: "loose"|"strict" }
  - ParsedRef: { book_key: str|null, start: (chap:int, verse:int|null), end: (chap:int, verse:int|null), raw: str, errors?: [] }
  - ResolvedRange: { start: "Gen.1.1"|null, end: "Gen.1.5"|null, fuzzy_ratio?: int, not_found?: str }

- Data model
  - Canon registry: `data/canon_index.json` — list of works and mapping to canon/*.json files.
  - Per-work JSON: book entries with `osis_abbr`, `names`, `abbrs`, `num_chaps`, `num_verses` mapping chapter → verse count.
  - Keep raw JSON stable; load once and cache per-process; expose a loader that returns typed structures for validation.

- Error handling
  - Normalize stage:
    - strict: unknown book → return NotFound for that token; stop parsing that candidate and attach `not_found`.
    - loose: unknown map → return best fuzzy candidate with `fuzzy_ratio`; attach `candidates` when `--all-candidates`.
  - Parse stage:
    - Out-of-range numbers → attach validation error for that parsed ref but continue parsing subsequent refs.
  - Resolve stage:
    - If expansion fails (missing canon data) → return `start: null, end: null` with `not_found` and structured error.
  - API: return list of results, each item either a resolved range or an error object; do not raise on per-reference errors. For fatal internal errors raise typed exceptions.

- Testing strategy
  - TDD for each stage: unit tests for tokenizer, normalizer (including fuzzy match edge cases), parser, and resolver (versification edge cases).
  - Integration tests for full pipeline with representative strings (KJV forms, Book of Mormon forms, typo/fuzzy cases, cross-book ranges, multi-sep lists).
  - Use small fixture canon JSON subsets for unit tests to keep tests hermetic.
  - Commands: `uvx pytest` to run tests.

Verification

- Unit test coverage per stage; CI runs `uvx pytest`, `uvx ruff check --fix`, `uvx ruff format`, `uvx ty check`.
- Manual spot-checks: sample CLI runs with `--mode strict/loose` and `--all-candidates` to confirm JSON output shape.

Decisions

- Use fuzzy matching (rapidfuzz) only in `loose` mode; `strict` mode returns explicit not-found errors.
- Keep public API stable and small: expose only `parse_references(text, mode='loose', canon_books=None, all_candidates=False)`.
- Represent OSIS as `{start, end}` strings rather than custom objects for simpler downstream consumption.
- Keep canon data read-only in canon and never modify at runtime.
