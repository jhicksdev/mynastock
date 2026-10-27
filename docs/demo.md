# Browser demo

**Live:** <https://jhicksdev.github.io/mynastock/demo/>

The demo is not a mock. `tools/assemble.py --extra tools/web.txt` concatenates the
portable kernel with a browser entry point, `myna compile -t js` emits one ES module, and
the UI calls the same `dispatch(Request) -> Response` pipeline as the HTTP server.

Differences from the server are confined to adapters:

| Concern | Server | Browser |
|---|---|---|
| Storage | SQLite | `localStorage`, one JSON document |
| Clock | `datetime.now(UTC)` | `Date.now()` through `epoch_ms_to_iso` |
| IDs | UUIDv4 | `crypto.randomUUID()` |
| Transport | stdlib `http.server` | hash routes calling `dispatch` directly |

## Data

- Key: `mynastock:v1`. Clearing it restores the seeded catalogue.
- Seed: 8 products, 3 locations, receipts, one transfer, low-stock and out-of-stock cases.
- Every write goes through the portable handlers, so validation, idempotency, averages,
  and transfer legs behave exactly as on the server.
- The demo does not make network requests.

## Routes

| Hash | View |
|---|---|
| `#/` | KPIs, valuation bars, recent movements |
| `#/stock` | filters, stock table, movement form |
| `#/movements` | newest-first ledger |
| `#/products` | product list and create form |
| `#/reorder` | suggested quantities with a one-click receipt |
| `#/behind` | architecture notes, reset, source viewer link |

## Build and test

```bash
make demo        # assemble + compile build/demo.mjs, copy site/demo/*
make demo-smoke  # boot the bundle against a DOM stub, render every route, post a receipt
make site        # landing + demo + source viewer + asset audit
python3 -m http.server -d site   # inspect at http://localhost:8000
```

`demo-smoke` catches bundle-level failures (missing exports, boot errors, broken routes,
persistence). It does not test layout.

## Manual QA checklist

Run before a release:

- [ ] Fresh visit seeds the catalogue and shows three KPI cards with non-zero values.
- [ ] `#/stock` search filters by SKU and name; "Low only" narrows to low/out rows.
- [ ] Receiving 5 units updates on-hand, average cost, and the overview KPIs.
- [ ] Issuing more than available shows the `stock.insufficient` detail in a toast.
- [ ] Transferring writes two movements; the source and destination both change.
- [ ] An adjustment without a reason is rejected; a signed delta works.
- [ ] `#/reorder` "Receive N" posts a receipt and the row disappears when above the point.
- [ ] Creating a product with a lowercase SKU is rejected with a readable message.
- [ ] Reload preserves state; "Reset demo data" clears it and reseeds.
- [ ] Layout holds at 360 px; tables scroll; no horizontal page overflow.
- [ ] Dark mode via `prefers-color-scheme` is legible.
- [ ] Keyboard: tab reaches nav, filters, forms; focus ring is visible.
- [ ] Source viewer links resolve and show Myna, Python, and JS where available.

## Known limits

- State is per browser profile; there is no sync or backend.
- Search and query values are not percent-decoded (ASCII SKUs, codes, and dates only).
- `localStorage` caps the document size; the seed is deliberately small.
- There is no authentication, and the demo is not a deployment template.
