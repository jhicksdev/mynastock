# MynaStock

**Inventory that speaks your language.**

[![CI](https://github.com/jhicksdev/mynastock/actions/workflows/ci.yml/badge.svg)](https://github.com/jhicksdev/mynastock/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Myna](https://img.shields.io/badge/myna--lang-0.4.1-informational)](https://pypi.org/project/myna-lang/)

MynaStock is an inventory management system written in [Myna](https://github.com/jhicksdev/myna), an ultra-dense language that transpiles 1:1 to Python 3.12 and to a portable subset of JavaScript. One import-free kernel is intended to power a zero-dependency HTTP server, an ASGI deployment, and a static browser demo compiled from the same source.

> **Status: M1 (ledger).** Catalogue, append-only movements with per-location moving
> average, idempotent posting, memory + SQLite repositories, and cross-target parity are
> implemented. The HTTP API, browser demo, and documentation site land in M2-M4.

## Quickstart

Requirements: `myna-lang==0.4.1`, Python 3.12+, Node 22+, and `uv` (only for the default `uvx ruff` runner; `RUFF=ruff` works too).

```bash
git clone https://github.com/jhicksdev/mynastock.git
cd mynastock

make check                                      # gates, Python tests, JS parity
myna run src/mynastock/main.myna                # banner
myna run src/mynastock/cli.myna version         # CLI
```

`make check` runs three things:

| Target | What it proves |
|---|---|
| `lint` | every listed portable module declares `@target(py, js)`, generates for JS, imports only other portable modules, and contains no exceptions or `new` |
| `test-py` | the kernel behaves correctly under CPython |
| `lint-py` | the generated Python has no syntax or undefined-name errors |
| `test-js` | the same cases pass under Node against the compiled ES module |

`lint-py` uses `uvx ruff` by default; install ruff yourself and pass `RUFF=ruff` if you prefer.

## How it is built

```
adapters (Starlette | stdlib http | localStorage)     @target(py) / @target(js)
        ↓ portable Request/Response
http (router, handlers, presenters)                   @target(py, js)
        ↓
app (use cases, idempotency)                          @target(py, js)
        ↓
core (money, ledger rules, invariants)                @target(py, js), no imports
        ↓
memory repo | SQLite repo | localStorage repo
```

The rule is simple: shared code imports nothing and raises nothing, so it survives both backends. Anything that needs the host — sockets, SQL, storage, clocks, IDs — lives in an adapter.

### Portable-zone rules

1. No imports; no exceptions (`!{`, `!!`, `!^`, `!&`, `!?`); no `new`.
2. Money is integer cents; quantities are whole units.
3. Validate strings with `is_digits` before `@int`.
4. No comprehensions over strings; use `% i <- ..#s` and indexing.
5. `??` arms are blocks with an explicit `^` return.
6. `+@` marks the public surface, so JavaScript gets a real `export`.

See [`docs/adr/0001-portable-core.md`](docs/adr/0001-portable-core.md) for the evidence behind each rule.

## What works now

- **Catalogue** — uppercase SKUs and location codes, explicit validation, optimistic
  `version` updates.
- **Ledger** — `receive`, `issue`, `adjust`, `transfer`; append-only movements; balances
  materialized in the same transaction; per-location moving weighted average.
- **Idempotency** — an `operations` row stores the canonical request fingerprint and the
  serialized response. Replay returns the original result; a changed payload is rejected.
- **Repositories** — in-memory (tests, browser) and SQLite (stdlib) behind one contract,
  with optimistic `version` checks so concurrent planners cannot double-post.
- **Reports** — stock rows, reorder suggestions, valuation by product or location.

## Repository layout

```
src/mynastock/
  core.myna           portable kernel: entities, validation, ledger rules, Result
  ports.myna          repository contract
  app/service.myna    use cases, idempotency, reports
  adapters/           memory.myna, sqlite.myna
  db/migrations.myna  schema as Myna constants (survives the .pyz bundle)
  main.myna, cli.myna entry points
tests/                unittest sources (compiled to build/py) + Node parity suite
tools/                portability gates, import checker, JS assembler
docs/adr/             architecture decision records
build/                generated Python and JavaScript (gitignored)
```

Tests are compiled before they run, so they import the installed-shaped package (`mynastock.core`) rather than relative paths. That keeps `unittest discover` and the future `.pyz` artifact honest.

## Roadmap

- **M0** — scaffold, portability gates, parity harness. Done.
- **M1** — ledger, moving average, idempotency, memory + SQLite repositories. Done.
- **M2** — portable router, stdlib HTTP adapter, `mynastock.pyz` with zero installed dependencies.
- **M3** — browser demo assembled from the same kernel, GitHub Pages, source viewer.
- **M4** — Starlette adapter, generated OpenAPI, documentation site, v1.0.0.

Out of scope for v1: authentication, purchase orders, reservations, FIFO costing, multi-currency. Those are documented as intentional boundaries rather than missing features.

## Contributing

Development setup, gates, and the portable-zone checklist are in [`CONTRIBUTING.md`](CONTRIBUTING.md). Security reports: [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE).
