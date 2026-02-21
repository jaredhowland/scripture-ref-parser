# Code Review Issues (2026-02-20)

This checklist captures issues discovered during a full code review of the
`parse-scripture-refs` repository and suggested fixes or follow-ups. Each item
includes a suggested issue title, short description, severity, and recommended
fix/PR branch name.

- [ ] **Centralize OSIS formatting & chapter expansion**
  - Issue: Duplicate `_format_osis` and chapter-expansion logic appear in
    `src/scripture_ref_parser/resolve/resolver.py` and
    `src/scripture_ref_parser/api/__init__.py`.
  - Severity: Medium
  - Suggested fix: Move formatting/expansion helpers into `resolve` (or a
    shared `utils`) and update API to reuse them.
  - PR branch: `fix/centralize-osis-format`

- [ ] **Fix normalize `is_exact` for unknown strict matches**
  - Issue: `normalize_book(..., mode='strict')` returns `is_exact=True` when the
    `key` is `None`, which is misleading.
  - Severity: Low
  - Suggested fix: Return `is_exact=False` for not-found, or add a dedicated
    `not_found` flag and adjust callers.
  - PR branch: `fix/normalize-is_exact`

- [ ] **Tokenizer: support Unicode and expanded characters**
  - Issue: Tokenizer uses `[A-Za-z]` which excludes non-ASCII letters and some
    punctuation used in book names/aliases.
  - Severity: Low
  - Suggested fix: Use Unicode-aware classes (e.g., `\w` with re.UNICODE) or
    explicitly include apostrophes/diacritics. Add tests for non-ASCII names.
  - PR branch: `enh/tokenizer-unicode`

- [ ] **Parser numeric-range clarity and edge-case tests**
  - Issue: `_parse_num_token` uses variable names and branches that are hard to
    reason about; possible ambiguity for inputs like `1:1-3`, `1:1-2:3`, `1-3`.
  - Severity: Medium
  - Suggested fix: Refactor into clear helpers, rename variables, and add
    explicit unit tests for edge cases.
  - PR branch: `refactor/parser-num-clarity`

- [ ] **Standardize error payloads across API/resolver**
  - Issue: `not_found` is returned as freeform string in several places. This
    makes programmatic consumption harder.
  - Severity: Low
  - Suggested fix: Standardize to a structured error object, e.g.
    `{reason: 'unknown_book', raw: '...', details: ...}` and update tests.
  - PR branch: `chore/standardize-errors`

- [ ] **Add lightweight logging for observability**
  - Issue: No `logging` calls in pipeline; diagnosing fuzzy-match surprises or
    parsing failures requires ad-hoc debugging.
  - Severity: Low
  - Suggested fix: Add `logging.getLogger(__name__)` and emit DEBUG/INFO logs
    in tokenizer/normalize/parse/resolve. Wire CLI option to increase verbosity.
  - PR branch: `feat/logging-pipeline`

- [ ] **Make fuzzy-match threshold configurable**
  - Issue: `_MIN_FUZZY_SCORE = 60` is hard-coded.
  - Severity: Low
  - Suggested fix: Expose as an optional parameter (API) or config constant
    with a documented default.
  - PR branch: `feat/fuzzy-threshold-config`

- [ ] **Tests: expand coverage for edge cases**
  - Issue: Core flows are covered, but tokenizer/parser edge-cases and
    `all_candidates` interactions need more coverage.
  - Severity: Medium
  - Suggested fix: Add unit tests for tokenizer unicode, parser numeric edge
    cases, normalize `all_candidates` behavior and API error messages.
  - PR branch: `test/edge-cases`

Recommended next steps

- Create individual GitHub issues (one per checklist item) using the titles
  above and assign/triage as needed.
- Implement fixes in small, focused PRs matching suggested branch names.

If you want, I can open the GitHub issues for you (requires repository access),
or I can create initial PR branches and patches here. Which would you prefer?
