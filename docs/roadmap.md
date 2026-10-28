# Roadmap

MynaStock 1.0.0 shipped with the kernel, both server transports, the static demo,
generated OpenAPI, and documentation verified together.

## Done

- **M0** — scaffold, portability gates, Python/JS parity harness.
- **M1** — append-only ledger, moving average, idempotency, memory + SQLite.
- **M2** — portable HTTP pipeline, stdlib adapter, CLI, zero-install `.pyz`.
- **M3** — browser demo, `localStorage`, GitHub Pages, source viewer.
- **M4** — async ASGI adapter, generated OpenAPI, documentation site, v1.0.0.

## Deferred

These are intentional boundaries, not forgotten work:

- Authentication, RBAC, and multi-tenancy.
- Purchase orders, reservations/allocation, FIFO or landed cost.
- Multi-currency and localized formatting.
- PyPI packaging (`pipx install mynastock`); the zipapp is the supported artifact.
- Browser automation in CI (the demo has a smoke test and a manual checklist).
- Removing `tools/assemble.py` when Myna ships JavaScript bundling.
- Per-request SQLite connections for high-concurrency ASGI deployments.

## Versioning

SemVer. The language pin is part of the compatibility surface: a myna minor upgrade is a
project minor until the parity and pin suites are green again.
