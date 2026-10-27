# ADR-0001: A single portable kernel

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

Myna compiles to Python 3.12 (normative semantics) and to a bounded JavaScript target.
The project needs one domain implementation that runs on a Python server *and* in a
browser demo; reimplementing the ledger in JavaScript would guarantee drift.

Before choosing a boundary, the JavaScript target was probed directly on myna 0.4.2
(the pinned release). Version 0.4.1 had already fixed several 0.4.0 problems: it defines
JS exception classes, emits `instanceof` checks for typed handlers, iterates strings in
comprehensions, and rejects relative imports instead of emitting broken specifiers.
0.4.2 is a diagnostics patch and leaves code generation unchanged. The constraints that
remain, and that the kernel is designed around, are:

- `?? v { 0 => "none" }` (expression arm) silently evaluates to `None`; only block arms
  with an explicit return work.
- `@int("4x")` raises in Python and returns `NaN` in JS.
- `new Date()` is not supported by the grammar.
- A parameter or variable named `p` is rewritten to the print alias in JS
  (`__myna_print`), while Python keeps the local binding.
- Relative imports are rejected for the JS target, so a multi-file portable program must
  be assembled into one file before compilation.

## Decision

Shared code lives in a **portable zone** governed by explicit laws, and portability is
proven by execution rather than assertion.

The laws:

1. Shared modules may import only other modules on the portable allowlist, and only
   relatively. Absolute imports are rejected.
2. No exception syntax (`!{`, `!!`, `!^`, `!&`, `!?`) in shared modules. Failures are
   values: `$$Err(code, message, field, meta)` and `$$Result(ok, value, error)`. 0.4.1+
   can emulate exceptions, but relying on that shim would tie domain flow to a class
   hierarchy the JS backend only approximates; explicit results are identical on both
   hosts and free of transport concerns. One audited boundary exists:
   `http/json.myna` uses a bare try/catch around `@j`, is listed in
   `tools/exceptional.txt`, and has invalid-input parity tests.
3. No host libraries (no `datetime`, `json`, `sqlite3`, `abc`, `uuid`). Builtins `@J`,
   `@j`, `@int`, `@str` are allowed; time, IDs, and storage are injected.
4. Money is integer cents; quantities are whole units. Values stay under `2^53`.
5. Parse, don't coerce: validate with `is_digits` before `@int`.
6. Scan strings with indexed loops (`% i <- ..#s`) so behaviour does not depend on
   iteration emulation.
7. `??` arms are blocks with explicit `^` returns.
8. Single inheritance only; no class or method decorators.
9. Public functions use `+@`, which yields `__all__` in Python and `export` in JS.
10. No `new`, no string `join`/`replace` (their semantics differ across targets).
11. Never use a builtin shorthand alias as an identifier. In 0.4.1 and 0.4.2 a parameter
    named `p` compiles to `__myna_print` in JS (the print alias wins over the local
    binding), while Python emits `p` correctly.

Enforcement:

- `tools/portable.txt` is the allowlist of shared modules, in dependency order.
- `tools/check_targets.sh` requires `@target(py, js)` on every module and validates the
  assembled artifact, because per-file JS compilation rejects relative imports.
- `tools/check_portable.sh` rejects exception syntax and `new`.
- `tools/check_imports.py` rejects absolute imports and imports of non-portable modules.
- `tools/check_collisions.py` rejects locals that shadow a module-level name (see below).
- `tools/exceptional.txt` lists the audited exception boundary.
- `tools/assemble.py` produces the single JS compilable file, refusing duplicate
  top-level names.
- `tests/js/parity.test.mjs` executes the same cases as the Python suites, including a
  full service scenario.

Pitfalls discovered while building M1 (all verified, all now covered by tests):

- `d$?k` treats `k` as a **literal** key, not a variable. Dynamic keys must use
  `lookup(d, k)`, which relies on the portable `in` operator.
- A subclass `@init` must call `..init()` before touching `self`, because the JS target
  emits an ES class and requires `super()` first.
- Return annotations are evaluated when the function is defined. A factory that returns
  a class must be declared after that class.
- Myna does not check call arity; extra positional arguments are silently ignored. Parity
  tests are the only reliable guard against a shifted argument list.
- `@srt(key=...)` is not documented as portable, so report ordering is left to the
  presenters and the UI.
- In 0.4.1+ the JS target rejects relative imports at compile time (0.4.0 emitted broken
  extensionless specifiers instead). The target gate therefore validates the assembled
  artifact, not each source module.
- The local toolchain matters: myna 0.4.0 and 0.4.1+ differ in JS code generation. Always
  verify against the pinned version, which is what CI installs.
- A local variable that matches a module-level name is emitted as an unscoped assignment
  in JS (`reason = ...`), overwriting the function even when it lives in another module.
  Because the assembler merges modules, this crosses boundaries. `check_collisions.py`
  rejects it; Python's scoping hides the bug, so only the JS parity suite catches it.
- Python keywords cannot be identifiers: `from` produced invalid Python. Use `from_time`.
- Do not shadow names that `@J`/`@j` auto-import (`json`, `dataclasses`, `datetime`,
  `sys`). A presenter function named `json` shadowed the module and broke every response.
  `make lint-py` (undefined-name checks) is the safety net for missing imports.

## Consequences

- Adapters (SQLite, HTTP, `localStorage`) own every host concern and are `@target(py)` or
  `@target(js)`.
- The kernel has no `try`, so error paths are explicit and visible in signatures.
- Some Python idioms are unavailable (comprehensions over strings, exceptions, dataclass
  inheritance), which costs a little verbosity and buys identical behavior.
- Any new portable primitive must ship with a parity case; the allowlist grows only when
  a test proves it.
- The browser artifact is assembled at build time because JS relative imports do not
  resolve in 0.4.x. That tool is deleted when upstream bundling lands.

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
