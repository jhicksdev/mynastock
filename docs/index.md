# MynaStock

**Inventory that speaks your language.**

MynaStock is an inventory management system written in [Myna](https://github.com/jhicksdev/myna),
an ultra-dense language that transpiles 1:1 to Python 3.12 and to a portable subset of
JavaScript. One kernel powers a zero-dependency server, an async ASGI deployment, and a
static browser demo.

[Live demo](https://jhicksdev.github.io/mynastock/demo/){: .md-button }
[Source viewer](https://jhicksdev.github.io/mynastock/source.html){: .md-button }
[GitHub](https://github.com/jhicksdev/mynastock){: .md-button }

## What works

| Area | Status |
|---|---|
| Catalogue | uppercase SKUs, locations, optimistic `If-Match` edits |
| Ledger | `receive`, `issue`, `adjust`, two-leg `transfer`, append-only |
| Costing | per-location moving weighted average, integer cents |
| Idempotency | `operations` table, request fingerprint, replayed response |
| Storage | SQLite (server) and `localStorage` (browser) behind one contract |
| HTTP | portable router/handlers, problem+json, keyset pagination |
| Transports | stdlib `http.server`, async ASGI, browser `dispatch` |
| Delivery | 22 KB zero-install `.pyz`, static Pages site |

## Quick facts

- **76 tests** across the kernel, repositories, API, socket, ASGI, OpenAPI, and fuzz
  reconciliation, plus a Node parity suite and a browser-bundle smoke test.
- **0 runtime dependencies**: the server artifact is the Python standard library.
- **1 portable kernel**: the browser demo compiles the same files as the server.
- **MIT licensed.**

## Start here

- [Quickstart](quickstart.md) — run the server, demo, and tests.
- [Architecture](architecture.md) — why the boundary is where it is.
- [HTTP API](api.md) — the contract and error codes.
- [Myna compliance](compliance.md) — the exact language surface used.
- [Decisions](adr/index.md) — every architectural trade-off, recorded.
