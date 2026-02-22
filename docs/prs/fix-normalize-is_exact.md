Title: fix/normalize-is_exact
=============================

Summary
-------

Fix the `normalize_book` behavior in strict mode so that when a book name is
not found the returned `NormalizedBook` uses `is_exact=False` (previously it
incorrectly returned `is_exact=True` with `key=None`).

Files changed
-------------

- src/scripture_ref_parser/normalize/normalize.py (adjusted strict-mode return)

Suggested git commands to create branch and commit
--------------------------------------------------

```bash
git checkout -b fix/normalize-is_exact
git add src/scripture_ref_parser/normalize/normalize.py
git commit -m "fix(normalize): set is_exact=False for not-found strict matches"
git push --set-upstream origin fix/normalize-is_exact
```

Notes
-----

This is a small behavioral correctness fix; adjust callers if they relied on
the previous misleading `is_exact` value.
