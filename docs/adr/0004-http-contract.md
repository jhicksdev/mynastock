# ADR-0004: A portable HTTP contract with a thin stdlib adapter

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

The same request pipeline has to run under the zero-dependency stdlib server, an async
ASGI adapter, and the browser demo. Framework-coupled handlers would force a
second implementation, and the demo would drift from the server.

FastAPI is a poor fit for Myna: its request models require bare class annotations, which
are a parse error, and its validation lives in Pydantic rather than in the portable
kernel. Starlette was considered for the ASGI adapter, but a raw ASGI callable needs no
dependency and keeps the contract identical for uvicorn and the test harness.

## Decision

**Transport is an adapter; the contract is portable.**

- `http/request.myna` defines `Request(method, path, query, headers, body)` and
  `Response(status, headers, body)`. Adapters translate into and out of these.
- `http/router.myna` is a table of `Route(method, pattern, handler)` where patterns are
  literal segments plus `{name}` captures. A path match with a different method returns
  `405` with an `Allow` header; no path match returns `404`.
- `http/handlers.myna` owns validation of wire types, builds service commands, and calls
  the same service functions as tests and the CLI.
- `http/presenters.myna` maps `Err.code` to an HTTP status and emits RFC 9457
  `application/problem+json`. The domain never contains a status code.
- Lists carry an ASCII `cursor` (SKU, or `occurred_at|id`). Rows are sorted by cursor and
  paged by strict comparison, which behaves identically in Python and JS. Cursors are
  opaque to clients.
- `POST /movements` requires `Idempotency-Key`. Replay returns `200` with
  `Idempotent-Replay: true`; the service marks `replayed` in the response body.
- `PATCH /products/{id}` is a partial merge and requires `If-Match: "N"`; stale versions
  return `409`.
- The stdlib adapter (`adapters/stdlib_server.myna`) is deliberately small:
  `ThreadingHTTPServer`, one repository, one lock, one UUID source, no authentication.
  It is a single-tenant trusted-network server; TLS and auth belong in a reverse proxy.

Query values are returned raw (no percent-decoding): v1 filters are ASCII SKUs, codes,
booleans, numbers, and ISO timestamps. Values may contain `=`; `&` remains the separator.

JSON parsing is the one place where a host error cannot be avoided. `http/json.myna` wraps
`@j` in a bare try/catch, is listed in `tools/exceptional.txt`, and has a parity test for
invalid input. Everything else uses `Result`.

## Consequences

- `dispatch(Request) -> Response` is tested in memory, under the stdlib server, and in
  the browser. 76 Python tests and the Node parity suite cover the pipeline.
- The stdlib server serializes requests with one lock. That is correct for the current
  SQLite connection and irrelevant at demo scale; a high-concurrency ASGI deployment would
  use a per-request connection or a worker pool.
- No percent-decoding means a search value containing `%` is literal. Acceptable for v1,
  documented, and replaceable inside `query.myna` when a portable decoder exists.
- No auth, rate limiting, TLS, compression, or HTTP/2. Documented in `SECURITY.md`.
- The handler table is the single source for routes; generated OpenAPI reads it
  and a drift gate keeps `docs/api/openapi.json` honest.

## Alternatives considered

- **Starlette-first:** rejected; the raw ASGI callable adds no dependency and the same
  contract is covered by direct tests and uvicorn.
- **FastAPI:** rejected; Pydantic models cannot be expressed (bare annotations) and
  framework validation would split the rules across targets.
- **One endpoint per movement type:** rejected; the transaction and idempotency path are
  identical, and the `??` dispatch is clearer than four near-duplicate handlers.
- **Offset pagination:** rejected; keyset cursors are stable under inserts and compare
  identically on both targets.
- **HTML templating in the server:** rejected; the UI belongs to the static demo.

## Links

- `docs/api.md` — the public contract
- `docs/adr/0001-portable-core.md` — exception boundary and naming rules
- `src/mynastock/http/` — router, handlers, presenters, pagination
