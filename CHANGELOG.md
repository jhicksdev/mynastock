# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-27

### Added

- M0 scaffold: portable kernel primitives (`concat`, `is_digits`, `parse_cents`,
  `format_cents`, `blend`, `stock_status`, `suggested_qty`).
- Python/JS parity harness: `tests/js/parity.test.mjs` mirrors the Python suites.
- Portability gates: target declaration, forbidden-construct scan, and a portable-import
  checker.
- `myna run` entry points (`main.myna`, `cli.myna`) and version metadata.
- ADR-0001 documenting the portable-zone rules and the myna 0.4.x evidence behind them.

- M1 ledger: append-only `receive`, `issue`, `adjust`, and two-leg `transfer` movements.
- Per-location moving weighted average costing with integer cents and validated bounds.
- Materialized `stock_levels` updated in the same transaction as the ledger, with
  optimistic version checks on both repositories.
- Idempotent posting through an `operations` table: canonical request fingerprint,
  stored response, replay, and conflict detection.
- Memory and SQLite repository implementations behind one contract test suite.
- Stock, reorder, and valuation reports.
- 500-movement seeded fuzz test asserting ledger-to-balance reconciliation and transfer
  conservation.
- `tools/assemble.py`: single-file JS assembly plus a service-level Node parity scenario.
- ADR-0002 (ledger and costing) and ADR-0003 (JS assembly).

- M2 HTTP pipeline: portable `Request`/`Response`, table-driven router with path
  parameters and 405/`Allow`, query parsing, RFC 9457 problem responses, keyset
  pagination, and PATCH merge guarded by `If-Match`.
- `POST /movements` transport: required `Idempotency-Key`, replay `200` plus
  `Idempotent-Replay`, and a `replayed` flag in the body.
- Stdlib `ThreadingHTTPServer` adapter with a single repository lock, request logging,
  and a transport-free handler layer.
- CLI (`serve`, `seed`, `--selftest`, `version`) and in-memory end-to-end selftest.
- Zero-install `mynastock.pyz` built with `myna bundle --zipapp` and verified under
  `python -I` in CI.
- Seed catalogue with low-stock, transfer, and valuation cases.
- 26 new tests (68 total) covering router, query, JSON, pagination, handlers, and the same
  API suite against both memory and SQLite; Node parity now exercises the full HTTP
  pipeline.
- ADR-0004 (HTTP contract) and `docs/api.md`.
- `check_collisions.py`: rejects locals that shadow module-level names, a JS-only scoping
  bug found by the parity suite.

- M3 browser demo assembled from the real kernel: `LocalRepo` on `localStorage`, hash
  routing, six views, movement/product forms, one-click reorder receipts, and a seeded
  catalogue.
- `tools/assemble.py --extra` and `tools/web.txt` for the web manifest; duplicate-name
  protection and HTML-safe assembly.
- Static site: landing page, demo shell, generated source viewer (Myna/Python/JS plus
  token stats), `404.html`, and an asset audit.
- `pages.yml` deploys `site/` through GitHub Actions; Pages is enabled for the repo.
- `epoch_ms_to_iso` in the portable kernel, cross-checked against Python `datetime`.
- `demo-smoke`: boots the bundle under a DOM stub, renders every route, posts a receipt,
  and verifies persistence.
- ADR-0005 and `docs/demo.md` with the manual QA checklist.

- M4 async ASGI adapter: an exported `~@asgi_app` callable, `asyncio.to_thread`
  dispatch, body/header/query translation, and integration tests.
- Generated OpenAPI 3.1 from the route table, a CLI `openapi` command, and a drift gate
  that fails when `docs/api/openapi.json` is stale.
- MkDocs documentation site: architecture, quickstart, API, testing, compliance, roadmap,
  and the ADR set, deployed under `/docs/` and linked from every surface.
- Release workflow: on `v*`, build the zipapp, write `SHA256SUMS`, and attach the artifact
  and OpenAPI schema to the GitHub release.
- Six new tests (76 total) covering ASGI and the generated schema.

### Changed

- Pinned `myna-lang==0.4.2`. Generated Python and JavaScript are byte-identical to the
  0.4.1 output for this codebase; the release only changes decompiler diagnostics.

### Fixed

- Verified the build against the pinned `myna-lang==0.4.1` (the previous local toolchain
  was 0.4.0): renamed `p` parameters that 0.4.1 rewrites to the print alias in JS, and
  moved the JS target gate to the assembled artifact because 0.4.1 rejects per-file
  relative imports.
- `make test-js` now passes explicit test files; Node 22 does not accept a directory for
  `--test`.
