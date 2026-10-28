# Quickstart

Requirements: `myna-lang==0.4.2`, Python 3.12+, Node 22+, and `uv` for the default
lint/docs runners (`ruff` and `mkdocs` can be installed directly instead).

```bash
git clone https://github.com/jhicksdev/mynastock.git
cd mynastock
make check
```

`make check` runs the portability gates, 76 Python tests, generated-Python lint, OpenAPI
drift, JS parity, the demo smoke test, the strict docs build, the site audit, the in-memory
selftest, and the zero-install zipapp smoke test.

## Server

```bash
make serve                                  # http://127.0.0.1:8080, build/mynastock.db
myna run src/mynastock/cli.myna seed --db build/mynastock.db
curl -s localhost:8080/api/v1/health
curl -s 'localhost:8080/api/v1/stock?below_reorder=true'
```

Create a movement:

```bash
curl -s -X POST localhost:8080/api/v1/movements \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-1' \
  -d '{"type":"receive","sku":"WID-001","location":"WH1","qty":10,"unit_cost_cents":250}'
```

## Async ASGI

```bash
pip install uvicorn
make serve-asgi                             # http://127.0.0.1:8081
```

The ASGI callable is `mynastock.adapters.asgi_server:asgi_app`; database path comes from
`MYNASTOCK_DB`.

## Zero-install artifact

```bash
make zipapp
python3 -I build/mynastock.pyz --selftest
python3 -I build/mynastock.pyz serve --db inventory.db
```

The zipapp embeds every Myna module and needs only Python 3.12+.

## Static demo

```bash
make demo        # build/demo.mjs, site/demo/app.js
make demo-smoke  # boot, route, write, persist
make site        # landing + demo + source viewer + docs
python3 -m http.server -d site
```

## CLI

```bash
myna run src/mynastock/cli.myna version
myna run src/mynastock/cli.myna serve --db inventory.db --port 9000
myna run src/mynastock/cli.myna seed
myna run src/mynastock/cli.myna openapi
myna run src/mynastock/cli.myna --selftest
```
