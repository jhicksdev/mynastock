# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- M0 scaffold: portable kernel primitives (`concat`, `is_digits`, `parse_cents`,
  `format_cents`, `blend`, `stock_status`, `suggested_qty`).
- Python/JS parity harness: `tests/js/parity.test.mjs` mirrors `tests/test_money.myna`.
- Portability gates: `@target(py, js)` declaration check and a forbidden-construct scan.
- `myna run` entry points (`main.myna`, `cli.myna`) and version metadata.
- ADR-0001 documenting the portable-zone rules and the myna 0.4.1 evidence behind them.
