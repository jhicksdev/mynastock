# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- M0 scaffold: portable kernel primitives (`concat`, `is_digits`, `parse_cents`,
  `format_cents`, `blend`, `stock_status`, `suggested_qty`).
- Python/JS parity harness: `tests/js/parity.test.mjs` mirrors the Python suites.
- Portability gates: target declaration, forbidden-construct scan, and a portable-import
  checker.
- `myna run` entry points (`main.myna`, `cli.myna`) and version metadata.
- ADR-0001 documenting the portable-zone rules and the myna 0.4.1 evidence behind them.

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
