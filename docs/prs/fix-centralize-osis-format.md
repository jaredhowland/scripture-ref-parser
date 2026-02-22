Title: fix/centralize-osis-format
=================================

Summary
-------

Centralize OSIS formatting and chapter-expansion logic by introducing
`resolve_ref_with_book` in `src/scripture_ref_parser/resolve/resolver.py` and
updating the public API to reuse it (removed duplicate logic in
`src/scripture_ref_parser/api/__init__.py`).

Files changed
-------------

- src/scripture_ref_parser/resolve/resolver.py  (added helper `resolve_ref_with_book`)
- src/scripture_ref_parser/api/__init__.py      (removed duplicated formatting/resolution)

Suggested git commands to create branch and commit
--------------------------------------------------

```bash
git checkout -b fix/centralize-osis-format
git add src/scripture_ref_parser/resolve/resolver.py src/scripture_ref_parser/api/__init__.py
git commit -m "refactor(resolve,api): centralize OSIS formatting and add resolve_ref_with_book helper"
git push --set-upstream origin fix/centralize-osis-format
```

Notes
-----

No behavioral changes intended; functionality is preserved but duplication
removed. Run `uv run pytest` to verify.
