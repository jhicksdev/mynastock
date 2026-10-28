# Architecture

```
adapters   stdlib http | ASGI | localStorage        @target(py) / @target(js)
             ↓ portable Request/Response
http       router · handlers · presenters · pagination
             ↓
app        use cases · idempotency · reports
             ↓
core       money · ledger rules · invariants
             ↓
ports      repository contract
             ↓
storage    memory | SQLite | localStorage
```

The dependency direction is strict: adapters depend on the HTTP layer, which depends on
the service, which depends on the kernel. Nothing points the other way.

## The portable zone

Shared code imports only allowlisted modules and never raises domain errors. Failures are
`Result`/`Err` values. Host concerns — sockets, SQL, storage, clocks, IDs — live in
adapters.

The single audited exception boundary is `http/json.myna`: `@j` throws on malformed JSON
and there is no non-throwing spelling. It is allowlisted in `tools/exceptional.txt` and
covered by parity tests.

Portability is enforced by execution, not assertion:

- `tools/check_targets.sh` validates the assembled JS artifact.
- `tools/check_imports.py` rejects absolute or non-portable imports.
- `tools/check_collisions.py` rejects locals that would clobber module-level JS bindings.
- `tools/assemble.py` merges the portable modules into one JS-compilable file.
- `tests/js/parity.test.mjs` runs the same scenarios under Node.

See [ADR-0001](adr/0001-portable-core.md) for the myna version evidence behind each rule.

## Domain model

| Entity | Purpose |
|---|---|
| `Product` | SKU, name, UOM, unit cost, reorder policy, version |
| `Location` | warehouse, bin, or transit code |
| `Movement` | immutable ledger row with signed quantity and cost snapshot |
| `StockLevel` | materialized `(product, location)` balance and average cost |
| `Operation` | idempotency key, request fingerprint, stored response |

Balances are a fold of the ledger, updated in the same transaction. Transfers write two
legs that share an operation and a transfer ID and sum to zero.

Costing is per-location moving weighted average, floored integer cents:

```
new_avg = (on_hand*avg + qty*cost) // (on_hand + qty)
```

Outbound movements snapshot the current average. Valuation is exact integer arithmetic.
See [ADR-0002](adr/0002-ledger-and-costing.md).

## HTTP

`dispatch(Request) -> Response` is transport-free. The stdlib and ASGI adapters translate
sockets into the same values; the browser builds `Request` objects directly from UI
events. Errors become RFC 9457 problem documents, with `Err.code` mapped to a status in
the presenter. See [ADR-0004](adr/0004-http-contract.md) and the [API](api.md).

## Browser demo

`LocalRepo` extends the in-memory repository and persists one JSON document after each
successful `apply`, so the browser gets the same atomic write as SQLite. The bundle is
assembled from the same source graph; only adapters differ. See
[ADR-0005](adr/0005-browser-demo.md) and [the demo guide](demo.md).

## Deployment shapes

| Shape | Command | Dependencies |
|---|---|---|
| stdlib server | `make serve` | Python standard library |
| zero-install zipapp | `make zipapp` | Python 3.12+ |
| ASGI | `make serve-asgi` | `uvicorn` |
| static demo | `make site` | a static file server |

All four serve the same behaviour.
