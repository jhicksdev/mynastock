# Contributing

## Prerequisites

- `myna-lang==0.4.1` (`pip install myna-lang==0.4.1`)
- Python 3.12+
- Node 22+ (for the JavaScript parity suite)
- GNU Make

## Everyday commands

```bash
make check        # lint + Python tests + generated-Python lint + JS parity
make test-py      # compile to build/py and run unittest
make lint-py      # ruff over the generated Python (syntax and undefined names only)
make test-js      # compile the portable kernel to build/js and run node --test
make clean
```

Tests are written in Myna but compiled first. Run one file directly with:

```bash
myna compile tests/test_money.myna -o build/py/tests/test_money.py
PYTHONPATH=build/py python3 build/py/tests/test_money.py
```

## The two rules that matter

1. **Portable means portable.** Any module listed in `tools/portable.txt` must obey the
   rules in [`docs/adr/0001-portable-core.md`](docs/adr/0001-portable-core.md): no
   imports, no exceptions, no `new`, no string comprehensions, integer cents.
2. **Every behavior change needs evidence on both targets.** Add the case to
   `tests/test_money.myna` *and* to `tests/js/parity.test.mjs`. A change that only
   passes in Python is not done.

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
