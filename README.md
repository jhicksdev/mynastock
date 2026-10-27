# MynaStock

**Inventory that speaks your language.**

[![CI](https://github.com/jhicksdev/mynastock/actions/workflows/ci.yml/badge.svg)](https://github.com/jhicksdev/mynastock/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Myna](https://img.shields.io/badge/myna--lang-0.4.2-informational)](https://pypi.org/project/myna-lang/)

MynaStock is an inventory management system written in [Myna](https://github.com/jhicksdev/myna), an ultra-dense language that transpiles 1:1 to Python 3.12 and to a portable subset of JavaScript. One portable kernel powers a zero-dependency HTTP server today, with an ASGI deployment and a static browser demo compiled from the same source on the roadmap.

> **Status: M3 (demo).** The catalogue, ledger, idempotent posting, repositories,
> portable HTTP pipeline, stdlib server, zero-install `.pyz`, and the browser demo are
> implemented. **Live demo:** <https://jhicksdev.github.io/mynastock/demo/>.
> The ASGI adapter, generated OpenAPI, and documentation site land in M4.

## Quickstart

Requirements: `myna-lang==0.4.2`, Python 3.12+, Node 22+, and `uv` (only for the default `uvx ruff` runner; `RUFF=ruff` works too).

```bash
git clone https://github.com/jhicksdev/mynastock.git
cd mynastock

make check                          # gates, 68 tests, JS parity, demo, site, zipapp
make serve                          # SQLite at build/mynastock.db, http://127.0.0.1:8080
make selftest                       # the whole pipeline, in memory, no socket
make site                           # landing page + browser demo + source viewer

curl -s localhost:8080/api/v1/health
python3 -I build/mynastock.pyz --selftest   # zero installed dependencies
```

The static demo is built from the same kernel as the server:

```bash
make demo                           # assemble + compile build/demo.mjs
make site                           # writes site/ (open with: python3 -m http.server -d site)
```

Seed a demo catalogue, then explore:

```bash
myna run src/mynastock/cli.myna seed --db build/mynastock.db
curl -s 'localhost:8080/api/v1/stock?below_reorder=true'
```

`make check` runs:

| Target | What it proves |
|---|---|
| `lint` | target declarations, portable-import edges, forbidden constructs, no local/global name collisions |
| `test-py` | 68 tests: kernel, ledger, repositories, router, handlers, stdlib API |
| `lint-py` | generated Python has no syntax or undefined-name errors |
| `test-js` | the same scenarios under Node against the assembled ES module |
| `demo-smoke` | the browser bundle boots, renders every route, and writes through the pipeline |
| `site` | the landing page, demo, and source viewer build; every local asset resolves |
| `selftest` | the full request pipeline runs in memory |
| `zipapp-smoke` | `python -I build/mynastock.pyz --selftest` with no installed packages |

`lint-py` uses `uvx ruff` by default; install ruff yourself and pass `RUFF=ruff` if you prefer.

## API

Base path `/api/v1`. Lists are keyset-paginated (`limit`, `cursor`, `next_cursor`). Errors
are `application/problem+json` with a stable `code`.

| Method | Path | Notes |
|---|---|---|
| `GET` | `/health` | version and status |
| `GET`/`POST` | `/products` | `q`, `active`, pagination |
| `PATCH` | `/products/{id}` | partial merge; requires `If-Match: "N"` |
| `GET`/`POST` | `/locations` | |
| `POST` | `/movements` | `receive`, `issue`, `adjust`, `transfer`; requires `Idempotency-Key` |
| `GET` | `/stock` | `q`, `location`, `below_reorder` |
| `GET` | `/movements` | `sku`, `location`, `type`, `from`, `to`; newest first |
| `GET` | `/reports/reorder` | suggested quantities |
| `GET` | `/reports/valuation` | `group_by=product\|location` |

```bash
curl -s -X POST localhost:8080/api/v1/movements \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-1' \
  -d '{"type":"receive","sku":"WID-001","location":"WH1","qty":10,"unit_cost_cents":250}'
```

The same key and body replays the original response with `Idempotent-Replay: true`; the
same key with a different body is a `409`. See [`docs/api.md`](docs/api.md).

## How it is built

```
adapters (stdlib http | Starlette M3 | localStorage M3)   @target(py) / @target(js)
        ↓ portable Request/Response
http (router, handlers, presenters, pagination)           @target(py, js)
        ↓
app (use cases, idempotency, reports)                     @target(py, js)
        ↓
core (money, ledger rules, invariants)                    @target(py, js)
        ↓
memory repo | SQLite repo | localStorage repo
```

The same `dispatch(Request) -> Response` pipeline runs under the stdlib server, the future
ASGI adapter, and the browser demo. The kernel imports only other portable modules; host
concerns (sockets, SQL, storage, clocks, IDs) live in adapters.

### Portable-zone rules

1. Import only other modules on the portable allowlist, and only relatively.
2. No exceptions in domain code; failures are `Result`/`Err`. The single exception is
   `http/json.myna` (parse failures), allowlisted and parity-tested.
3. No host libraries; time, IDs, and storage are injected.
4. Money is integer cents; quantities are whole units.
5. Validate strings with `is_digits` before `@int`.
6. `??` arms are blocks with an explicit `^` return.
7. Avoid Python keywords, auto-imported module names, and locals that shadow a
   module-level name; all three break the generated target.
8. `+@` marks the public surface, so JavaScript gets a real `export`.

See [`docs/adr/0001-portable-core.md`](docs/adr/0001-portable-core.md) for the verified
evidence behind each rule.

## What works now

- **Catalogue** — uppercase SKUs and location codes, explicit validation, optimistic
  `version` updates with `If-Match`.
- **Ledger** — `receive`, `issue`, `adjust`, `transfer`; append-only movements; balances
  materialized in the same transaction; per-location moving weighted average.
- **Idempotency** — an `operations` row stores the canonical request fingerprint and the
  serialized response. Replay returns the original result with a header; a changed
  payload is rejected.
- **Repositories** — in-memory (tests, browser) and SQLite (stdlib) behind one contract,
  with optimistic version checks so concurrent planners cannot double-post.
- **HTTP** — portable router and handlers, RFC 9457 problem responses, keyset pagination,
  PATCH merge semantics.
- **Delivery** — `myna bundle --zipapp` produces a 22 KB `mynastock.pyz` that runs on a
  clean Python with no third-party packages.
- **Browser demo** — the same kernel and `dispatch` pipeline compiled to one ES module,
  with a `localStorage` repository, seeded catalogue, hash routing, and a source viewer.
  No backend, no framework, no CDN.

## Repository layout

```
src/mynastock/
  core.myna            portable kernel: entities, validation, ledger rules, Result
  ports.myna           repository contract
  app/service.myna     use cases, idempotency, reports
  http/                request/response, router, handlers, presenters, pagination, JSON
  adapters/            memory.myna, sqlite.myna, stdlib_server.myna
  db/                  migrations.myna, seed.myna
  cli.myna, main.myna  entry points (zipapp is bundled from cli.myna)
  selftest.myna        in-memory end-to-end check
  web/                 browser repository, DOM helpers, views, entry point
web/                   static shells and styles for the landing page and demo
tests/                 unittest sources (compiled to build/py) + Node parity suite
tools/                 portability gates, import/collision checks, JS assembler, site build
docs/                  API contract and ADRs
site/                  generated Pages artifact (gitignored)
build/                 generated Python, JavaScript, SQLite, and the .pyz (gitignored)
```

Tests are compiled before they run, so they import the installed-shaped package
(`mynastock.core`) rather than relative paths. That keeps `unittest discover` and the
`.pyz` artifact honest.

## Roadmap

- **M0** — scaffold, portability gates, parity harness. Done.
- **M1** — ledger, moving average, idempotency, memory + SQLite repositories. Done.
- **M2** — portable HTTP pipeline, stdlib adapter, CLI, zero-install `.pyz`. Done.
- **M3** — browser demo assembled from the same kernel, GitHub Pages, source viewer. Done.
- **M4** — ASGI adapter with async routes, generated OpenAPI, documentation site, v1.0.0.

Out of scope for v1: authentication, purchase orders, reservations, FIFO costing,
multi-currency. Those are documented as intentional boundaries rather than missing
features.

## Contributing

Development setup, gates, and the portable-zone checklist are in
[`CONTRIBUTING.md`](CONTRIBUTING.md). Security reports: [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE).
