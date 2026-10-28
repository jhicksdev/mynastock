# Myna compliance

MynaStock pins **myna-lang 0.4.2**. The language is pre-1.0; generated output can change
between minors. This page records the surface the project relies on and the gaps it works
around.

## Version policy

- `requirements-dev.txt`, CI, and the docs pin `myna-lang==0.4.2`.
- `tests/spec`-style assertions live in the normal suites: time formatting, arithmetic,
  match arms, JSON, and byte/string behaviour.
- Upgrading: run `make check`, regenerate `docs/openapi.json`, rebuild the site, read the
  Myna changelog, and re-run the JS parity suite. 0.5.0 changes the default `@target` to
  Python-only, so every module must keep declaring its targets explicitly.

## Constructs used

| Construct | Where |
|---|---|
| `@target(py, js)` / `@target(py)` / `@target(js)` | portable zone, adapters, browser |
| `$$` dataclasses, `+@` exports | entities, commands, router, responses |
| `??` with block arms | movement dispatch, route dispatch, status reasons |
| comprehensions, `\|>` pipelines | reports, filters, route tables |
| `~@`, `~` | ASGI callable and threaded dispatch |
| `!&`, `!!` | SQLite transactions, adapter errors |
| `d$key`, `d$?key`, `lookup` | JSON and header access |
| `@J` / `@j` | wire format and storage |
| `$=` aliases | not used in v1 |

## Verified gaps and workarounds

| Gap in 0.4.2 | Workaround |
|---|---|
| A parameter named `p` compiles to `__myna_print` in JS | never name an identifier `p` |
| `?? v { 0 => "x" }` expression arms silently yield `None` | always use block arms with `^` |
| `@int("4x")` returns `NaN` in JS | validate with `is_digits` first |
| `new X()` is unsupported | derive values with functions (`Date.now()` + `epoch_ms_to_iso`) |
| Relative imports are rejected for `-t js` | one-file assembly via `tools/assemble.py` |
| A local matching a module-level name emits an unscoped JS assignment | `check_collisions.py` |
| Python keywords are valid-looking identifiers | `from` became `from_time`; ruff catches the rest |
| Auto-imported module names can be shadowed | rename `json` to `json_response` |

Some 0.4.0 gaps were fixed in 0.4.1: JS exception classes, typed catch checks, and string
iteration in comprehensions. MynaStock still returns `Result` values by design rather than
depending on exception flow.

## Upstream issues

The reproducers live outside this repository for now. When a fix lands, remove the
workaround, keep the parity case, and update this page.

## Links

- [Myna specification](https://github.com/jhicksdev/myna/blob/main/SPEC.md)
- [Myna design decisions](https://github.com/jhicksdev/myna/blob/main/DECISIONS.md)
- [ADR-0001](adr/0001-portable-core.md)
