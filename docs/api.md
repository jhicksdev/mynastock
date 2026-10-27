# HTTP API (v1)

Base path: `/api/v1`. JSON in, JSON out. Errors are
`application/problem+json` with a stable `code`.

## Conventions

- Money is integer cents. Quantities are positive whole units.
- SKUs and location codes are uppercase `A-Z`, `0-9`, `-`, `_` (1-40 chars).
- Timestamps are ISO-8601 UTC strings.
- Lists return `{ "items": [...], "next_cursor": "..." | null }`. `limit` defaults to 50
  and is capped at 200. Treat `cursor` as opaque.
- `POST /movements` requires `Idempotency-Key`. Replaying the same body returns `200`
  with `Idempotent-Replay: true`; the same key with a different body returns `409`.
- `PATCH /products/{id}` is a partial merge and requires `If-Match: "N"` where `N` is the
  current `version`.

## Endpoints

### `GET /health`

```json
{"status": "ok", "name": "MynaStock", "version": "0.1.0"}
```

### `GET /products`

Query: `q`, `active=true|false`, `limit`, `cursor`.

```json
{"items": [{"id": "...", "sku": "WID-001", "name": "Widget", "uom": "ea",
            "unit_cost_cents": 250, "reorder_point": 5, "reorder_qty": 20,
            "active": true, "version": 1}],
 "next_cursor": null}
```

### `POST /products`

```json
{"sku": "WID-001", "name": "Widget", "unit_cost_cents": 250,
 "reorder_point": 5, "reorder_qty": 20, "uom": "ea"}
```

`201` with the product. Duplicate SKU → `409 product.duplicate_sku`.

### `PATCH /products/{id}`

Headers: `If-Match: "1"`. Send only the fields to change.

```json
{"name": "Widget v2", "reorder_point": 10}
```

Returns `200` with the merged product and incremented `version`. A stale `If-Match`
returns `409 version.conflict`.

### `GET` / `POST /locations`

```json
{"code": "WH1", "name": "Main warehouse", "kind": "warehouse"}
```

`kind` is one of `warehouse`, `bin`, `transit`.

### `POST /movements`

Headers: `Idempotency-Key`.

```json
{"type": "receive", "sku": "WID-001", "location": "WH1",
 "qty": 10, "unit_cost_cents": 250, "reference": "PO-1042"}
```

| Type | Fields | Effect |
|---|---|---|
| `receive` | `location`, `qty`, optional `unit_cost_cents` | increases stock, blends average cost |
| `issue` | `location`, `qty` | decreases stock, rejects negative balances |
| `adjust` | `location`, signed `qty`, `reason` | corrects stock; positive adjustments accept cost |
| `transfer` | `location`, `to_location`, `qty` | two linked legs, sum to zero |

Response `201` includes the operation, its movements, and the resulting levels. A replay
returns `200` with the stored response and `Idempotent-Replay: true`.

### `GET /stock`

Query: `q`, `location`, `below_reorder=true`, `limit`, `cursor`.

```json
{"items": [{"sku": "WID-001", "product": "Widget", "location": "WH1",
            "on_hand": 10, "avg_cost_cents": 250, "value_cents": 2500,
            "reorder_point": 5, "status": "ok"}],
 "next_cursor": null}
```

`status` is `ok`, `low`, or `out`.

### `GET /movements`

Query: `sku`, `location`, `type`, `from`, `to`, `limit`, `cursor`. Newest first. Items
include `qty_delta`, the cost snapshot, `transfer_id`, `reason`, `actor`, `occurred_at`.

### `GET /reports/reorder`

```json
{"items": [{"sku": "LMP-007", "product": "Lamp", "location": "WH1",
            "on_hand": 1, "reorder_point": 2, "suggested_qty": 5}]}
```

### `GET /reports/valuation?group_by=location`

```json
{"group_by": "location", "total_cents": 41300,
 "items": [{"key": "WH1", "qty": 120, "value_cents": 41300}]}
```

## Error codes

| Code | Status | Meaning |
|---|---|---|
| `validation.failed` | 400 | missing or mistyped field |
| `sku.invalid`, `code.invalid`, `name.invalid`, `uom.invalid`, `kind.invalid` | 400 | field format |
| `qty.invalid`, `qty.too_large`, `cost.invalid`, `cost.too_large` | 400 | bounds |
| `idempotency.required` | 400 | missing `Idempotency-Key` |
| `group.invalid` | 400 | bad `group_by` |
| `transfer.same_location` | 400 | source equals destination |
| `adjust.reason_required` | 400 | adjustment without a reason |
| `route.not_found` | 404 | unknown path |
| `product.unknown`, `location.unknown` | 404 | unknown reference |
| `method.not_allowed` | 405 | known path, wrong method; includes `Allow` |
| `product.duplicate_sku`, `location.duplicate_code` | 409 | uniqueness |
| `stock.insufficient` | 409 | would go negative |
| `version.conflict` | 409 | stale `If-Match` or concurrent plan |
| `movement.idempotency_conflict` | 409 | key reused with another body |
| `product.inactive` | 409 | movement against an archived product |
| `internal.error`, `repo.error` | 500 | server fault |

Problem bodies:

```json
{"type": "about:blank", "title": "Conflict", "status": 409,
 "detail": "Not enough stock at this location", "code": "stock.insufficient",
 "field": "qty", "meta": {"available": 4}}
```
