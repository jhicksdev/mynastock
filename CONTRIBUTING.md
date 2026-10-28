# Contributing

## Prerequisites

- `myna-lang==0.4.2` (`pip install myna-lang==0.4.2`)
- Python 3.12+
- Node 22+ (for the JavaScript parity and demo smoke suites)
- GNU Make
- `uv` or installed `ruff` / `mkdocs-material` (the Makefile defaults to `uvx` for both)

## Everyday commands

```bash
make check        # 76 tests, parity, demo, docs, site, zipapp smoke
make lint         # target declarations, forbidden constructs, imports, name collisions
make test-py      # compile to build/py and run unittest
make lint-py      # ruff over the generated Python (syntax and undefined names only)
make openapi-check # docs/api/openapi.json matches the route table
make test-js      # assemble the portable modules, compile to ES, run node --test
make selftest     # the full request pipeline, in memory
make serve        # SQLite at build/mynastock.db on 127.0.0.1:8080
make serve-asgi   # async ASGI via uvicorn on 127.0.0.1:8081
make zipapp-smoke # python -I build/mynastock.pyz --selftest
make demo         # assemble + compile the browser bundle
make demo-smoke   # boot the bundle against a DOM stub and exercise every route
make docs         # strict MkDocs build under build/docs
make site         # landing, demo, docs, source viewer, asset audit
make clean
```

The browser demo adds `tools/web.txt` to the portable manifest. Imports must start at
column 0: the assembler strips them by that rule, and HTML inside template strings usually
starts with `<` after indentation. JavaScript-only modules are skipped by `build-py`.

`make test-js` runs `tools/assemble.py`, which concatenates the modules in
`tools/portable.txt` into one JS-compilable file. Add a new portable module to the end of
that list, after its dependencies. Do not add it in the middle of a group.

Tests are written in Myna but compiled first. Run one file directly with:

```bash
myna compile tests/test_money.myna -o build/py/tests/test_money.py
PYTHONPATH=build/py python3 build/py/tests/test_money.py
```

## The two rules that matter

1. **Portable means portable.** Any module listed in `tools/portable.txt` must obey the
   rules in [`docs/adr/0001-portable-core.md`](docs/adr/0001-portable-core.md): no
   imports, no exceptions, no `new`, no string comprehensions, integer cents.
2. **Every behavior change needs evidence on both targets.** Add the case to the relevant
   Python suite *and* to `tests/js/parity.test.mjs`. A change that only passes in Python
   is not done. The ledger suite, the repository contract suite, and the 500-movement
   reconciliation fuzz test are the baseline.

Three pitfalls that cost real debugging time, now covered by tests:

- `d$?k` uses the **literal** key `"k"`. Dynamic keys go through `lookup(d, k)`.
- Never name a variable or parameter `p`: myna 0.4.1 and 0.4.2 rewrite it to the print
  alias in JS (`__myna_print`) while Python keeps the local binding.
- A local variable must not share a name with a module-level function or class. JS emits
  an unscoped assignment and overwrites the outer binding; `check_collisions.py` blocks it.
- Do not use Python keywords (`from`, `class`, `import`) as identifiers, and do not shadow
  auto-imported module names (`json`, `datetime`, `sys`).
- A subclass `@init` must call `..init()` before touching `self`; the JS target needs
  `super()` first.
- Myna does not check call arity. Extra positional arguments are silently ignored, so a
  shifted argument list can only be caught by tests.
- Parse failures are the one exception boundary (`http/json.myna`). Adding another
  requires an entry in `tools/exceptional.txt` and a parity test.

If a language limitation forces a workaround, document it in the ADR or a comment, and
link the upstream issue. Do not widen the portable zone silently.

## Architecture decisions

Anything that changes a boundary — a new dependency, a new adapter, a data-model change,
a deviation from the blueprint — needs an ADR in `docs/adr/`. Use the existing format:
Status, Date, Context, Decision, Consequences, Alternatives.

## Commits and releases

Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). The changelog is
curated at release time; do not edit it per commit. Version numbers live in
`src/mynastock/version.myna`.

## Code style

- Myna: four spaces, one statement per line, braces on the same line, `+@` on public
  functions.
- Keep functions small enough that their portability is obvious.
- Prefer explicit `Result`/`Err` returns over clever control flow in the kernel.

## Code of conduct

Be direct, be kind, assume good intent. A formal Contributor Covenant will be added when
the repository is made public.
