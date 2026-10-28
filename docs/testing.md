# Testing

Every behaviour has a test, and every cross-target claim has an executable proof.

| Suite | What it covers |
|---|---|
| `test_money` | integer cents, parsing, formatting, blending, status helpers |
| `test_ledger` | receive, issue, adjust, transfer, bounds, conservation, fingerprints |
| `test_time` | `epoch_ms_to_iso` against known timestamps and Python `datetime` |
| `test_service` | catalogue, idempotent replay/conflict, reports, versioning |
| `test_repo_contract` | one suite against memory **and** SQLite |
| `test_http` | router, query parsing, safe JSON, pagination, presenters |
| `test_http` (API classes) | the same HTTP suite against memory and SQLite |
| `test_stdlib_server` | real sockets: health, create, movement, replay, problem responses |
| `test_asgi` | async ASGI callable: body parsing, headers, query, errors |
| `test_openapi` | every route documented, security headers, document shape |
| `test_reconcile_fuzz` | 500 seeded movements folded back to balances |
| `tests/js/parity.test.mjs` | kernel, service, and HTTP pipeline under Node |
| `tests/js/demo-smoke.mjs` | browser bundle boots, routes, writes, persists |

## Why the parity suite matters

Myna compiles to Python and JavaScript, but the targets are not identical. The parity
suite has already caught:

- a local variable named like a module-level function overwriting it in JS;
- a parameter named `p` compiling to the print alias;
- an assembler rule that deleted HTML lines inside template strings.

Each is now covered by a gate (`check_collisions.py`), a naming rule, or a regression test.

## Gates

`make check` runs, in order:

1. `lint` — target declarations, forbidden constructs, imports, name collisions.
2. `test-py` — compile and run 76 tests.
3. `lint-py` — ruff over generated Python (syntax and undefined names).
4. `openapi-check` — `docs/openapi.json` matches the route table.
5. `test-js` — Node parity over the assembled ES module.
6. `demo` / `demo-smoke` — compile the web bundle and exercise every route.
7. `site` — landing, docs, source viewer, asset audit.
8. `selftest` — the pipeline in memory without a socket.
9. `zipapp-smoke` — the bundled artifact under `python -I`.

CI runs the same commands on Python 3.12 and 3.13, myna-lang 0.4.2, ruff, Node 22, and
deploys the site through GitHub Pages.

## Not covered

- Browser layout and interaction are a manual checklist in [the demo guide](demo.md).
- SQLite contention across processes and load testing are out of scope for v1.
