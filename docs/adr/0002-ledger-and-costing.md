# ADR-0002: Append-only ledger with per-location moving average

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

Inventory systems fail in predictable ways: balances drift from history, concurrent
postings overwrite each other, retries create duplicate stock, and valuation disagrees
with the ledger. All four are testable, and all four are cheap to prevent if the data
model makes them impossible rather than merely unlikely.

The repository also has to run in two places: a Python server and a browser demo. The
rules therefore live in the portable kernel as pure functions, and the storage layer only
applies a plan atomically.

## Decision

**Movements are the source of truth.** Every change is an immutable row:
`receive`, `issue`, `adjust`, `transfer_out`, `transfer_in`. There are no updates and no
deletes; corrections are compensating movements. `stock_levels` is a materialized fold of
the ledger, written in the same transaction.

**Costing is per-location moving weighted average.**

```
new_avg = (on_hand*avg + qty*cost) // (on_hand + qty)
```

`//` is floored on both targets, so the result is deterministic. Outbound movements
snapshot the current average in `unit_cost_cents` without changing it. Transfers move cost
from source to destination and blend into the destination average. Valuation is
`sum(on_hand * avg_cost_cents)`, exact in integer cents.

**Quantities are whole units; money is integer cents.** Bounds are `qty <= 1_000_000` and
`cost <= 100_000_000`, keeping every product under `10^14`, well inside the JavaScript
safe-integer range.

**Transfers are one operation with two legs.** Both legs share `operation_id` and
`transfer_id`, and must sum to zero. A partial transfer is impossible because both levels
and both legs are written by one `apply` call.

**Idempotency lives on an `operations` row, not on movements.** A transfer has two legs,
so a key on `movements` would collide with itself. `operations` stores:

- `idempotency_key` (unique),
- `request_fingerprint` — a length-prefixed concatenation of the canonical request fields,
  not a hash: no portable hashing primitive exists, and length prefixes remove ambiguity,
- `response_json` — the serialized result, replayed verbatim.

Same key and fingerprint returns the stored response; same key and a different fingerprint
returns `movement.idempotency_conflict`.

**Concurrency is optimistic.** Each planned `StockLevel` carries its next `version`. The
repository applies the whole plan only if every stored level is still at `version - 1`;
otherwise it returns `version.conflict` and writes nothing. SQLite enforces this in the
upsert's `WHERE stock_levels.version = excluded.version - 1`; the memory repository
pre-validates every level before writing.

**Codes are canonical uppercase.** `is_code` accepts `A-Z`, `0-9`, `-`, `_` (1-40 chars).
Rejecting lowercase avoids case-folding, which has no portable Myna shorthand and differs
between Python and JavaScript.

## Consequences

- `test_reconcile_fuzz` folds 500 seeded random movements and asserts the result equals
  the materialized balances. It is the backstop for every storage change.
- Rounding down understates valuation by at most one cent per inbound movement. It never
  drifts upward and never accumulates silently.
- A concurrent planner must retry on `version.conflict`. There is no lock held across the
  service layer, which keeps the kernel pure and the browser viable.
- Negative stock is rejected; there is no override flag in v1.
- FIFO, landed cost, multi-currency, reservations, and purchase orders are out of scope
  and documented as such.

## Alternatives considered

- **Mutable balances only:** rejected; reconciliation would be unprovable.
- **FIFO layers:** more realistic, but several times the rule surface for a portfolio
  project. Deferred.
- **Global average per product:** simpler, but transfers would silently change product
  valuation and hide location-level error.
- **Hash the request with a checksum:** rejected; no portable `ord` or bitwise operators,
  and a weak hash adds risk without benefit. Length-prefixed fields are exact.
- **Pessimistic locking:** rejected; the memory and browser adapters would need to fake a
  lock, and the failure mode (retry) is easy to explain.

## Links

- `src/mynastock/core.myna` — `plan_receive`, `plan_issue`, `plan_adjust`, `plan_transfer`
- `src/mynastock/app/service.myna` — posting, idempotency, reports
- `docs/adr/0001-portable-core.md`
