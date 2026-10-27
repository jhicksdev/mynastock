# ADR-0001: A single import-free portable kernel

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

Myna compiles to Python 3.12 (normative semantics) and to a bounded JavaScript target.
The project needs one domain implementation that runs on a Python server *and* in a
browser demo; reimplementing the ledger in JavaScript would guarantee drift.

Before choosing a boundary, the JavaScript target was probed directly on myna 0.4.1.
The failures are not theoretical:

- `$E<Exception` emits `class E extends Exception`, and JS has no `Exception` binding.
- `!^ValueError("x")` emits `throw ValueError('x')`, also undefined.
- `!!e:ValueError` compiles to a bare `catch (e)` with no type check, so a typed handler
  swallows every error.
- `[c | c <- s]` emits `s.filter(...)`; strings have no `.filter`.
- `?? v { 0 => "none" }` (expression arm) silently returns `None` in both targets; only
  block arms with an explicit return work.
- `@int("4x")` raises in Python and returns `NaN` in JS.
- `new Date()` is not supported by the grammar.
- Relative imports compile to extensionless specifiers (`./core`) and cannot be bundled
  for JS, so the browser artifact must be a single file.

## Decision

Shared code lives in a **portable zone** governed by explicit laws, and portability is
proven by execution rather than assertion.

The laws:

1. No imports (`<`) in shared modules.
2. No exception syntax (`!{`, `!!`, `!^`, `!&`, `!?`) in shared modules. Failures are
   values: `$$Err(code, message, field, meta)` and `$$Result(ok, value, error)`.
3. No host libraries (no `datetime`, `json`, `sqlite3`, `abc`, `uuid`). Builtins `@J`,
   `@j`, `@int`, `@str` are allowed; time, IDs, and storage are injected.
4. Money is integer cents; quantities are whole units. Values stay under `2^53`.
5. Parse, don't coerce: validate with `is_digits` before `@int`.
6. No comprehensions over strings; iterate with `% i <- ..#s` and index.
7. `??` arms are blocks with explicit `^` returns.
8. Single inheritance only; no class or method decorators.
9. Public functions use `+@`, which yields `__all__` in Python and `export` in JS.
10. No `new`, no string `join`/`replace` (their semantics differ across targets).

Enforcement:

- `tools/portable.txt` is the allowlist of shared modules.
- `tools/check_targets.sh` requires `@target(py, js)` and a successful JS generation.
- `tools/check_portable.sh` rejects imports, exception syntax, and `new`.
- `tests/js/parity.test.mjs` executes the same cases as the Python suite.

## Consequences

- Adapters (SQLite, HTTP, `localStorage`) own every host concern and are `@target(py)` or
  `@target(js)`.
- The kernel has no `try`, so error paths are explicit and visible in signatures.
- Some Python idioms are unavailable (comprehensions over strings, exceptions, dataclass
  inheritance), which costs a little verbosity and buys identical behavior.
- Any new portable primitive must ship with a parity case; the allowlist grows only when
  a test proves it.
- The browser artifact is assembled at build time because JS relative imports do not
  resolve in 0.4.1. That tool is deleted when upstream bundling lands.

## Alternatives considered

- **Python-only kernel with a separate JS demo:** rejected; duplicated ledger logic would
  drift and undermine the project's main claim.
- **Full Python semantics on JS via a runtime shim:** rejected; Myna already rejects or
  miscompiles several constructs, and a hand-written shim would be larger than the kernel.
- **Target-gated modules for everything:** rejected for the domain layer; too much
  duplication for code that is intrinsically portable.

## Links

- Myna specification: <https://github.com/jhicksdev/myna/blob/main/SPEC.md>
- Target contract: `DECISIONS.md` D-001 and D-002 in the Myna repository
- Upstream gaps: `docs/upstream/` (added in M0.5)
