# Contributing

## Prerequisites

- `myna-lang==0.4.1` (`pip install myna-lang==0.4.1`)
- Python 3.12+
- Node 22+ (for the JavaScript parity suite)
- GNU Make

## Everyday commands

```bash
make check        # lint + Python tests + generated-Python lint + JS parity
make lint         # target declarations, forbidden constructs, portable-import edges
make test-py      # compile to build/py and run unittest
make lint-py      # ruff over the generated Python (syntax and undefined names only)
make test-js      # assemble the portable modules, compile to ES, run node --test
make clean
```

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
- A subclass `@init` must call `..init()` before touching `self`; the JS target needs
  `super()` first.
- Myna does not check call arity. Extra positional arguments are silently ignored, so a
  shifted argument list can only be caught by tests.

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
