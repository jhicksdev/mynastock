# ADR-0003: Build-time assembly for the JavaScript target

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

Before 0.4.1, Myna compiled relative imports for the JavaScript target into
extensionless specifiers:

```js
import { add } from "./core";   // no .js
```

Browsers fetch that specifier literally, and Node ESM rejects it. `myna run -t js` also
copies the entry file to a temporary directory, so siblings can never resolve. Myna's own
decision record (D-002) places JavaScript bundling after 1.0.

The project nevertheless needs one artifact that runs in a browser and one that Node can
import for parity tests, both sourced from the same portable modules.

## Decision

`tools/assemble.py` concatenates the modules listed in `tools/portable.txt`, in order:

1. strip module-level `@target(...)` headers and relative imports,
2. emit a single `@target(js)` header with provenance,
3. scan top-level declarations and refuse duplicate names across modules,
4. write `build/js/portable.myna`, which `myna compile -t js` turns into one ES module.

The allowlist order is the dependency order. Modules are small and the list is short, so
an explicit topological order is clearer than a resolver. The assembler is a development
tool, not part of the runtime.

Node imports the resulting module directly. The same parity cases run against Python and
JavaScript, including a full service scenario (catalogue, receive, transfer, replay,
reports, insufficient stock).

## Consequences

- Adding a portable module means appending it to `tools/portable.txt` after its
  dependencies. `check_imports.py` validates the edges; the assembler validates names.
- All portable modules share one namespace in the JS artifact. Prefixing or renaming is
  required if two modules ever want the same top-level name.
- The browser demo compiles the same assembled file; there is no second implementation.
- The tool is debt by design. When upstream JS bundling lands, delete `assemble.py`,
  point `myna compile -t js` at the real entry, and keep the parity suite unchanged.

## Alternatives considered

- **Reimplement the domain in JavaScript for the demo:** rejected; guaranteed drift and a
  weaker claim.
- **Rewrite specifiers to `.js` after compilation:** rejected; fragile, and still leaves
  `myna run -t js` unable to resolve the graph.
- **Depend on a generic JS bundler (esbuild/rollup):** rejected; drags Node tooling into a
  Python-centric build and undermines the zero-dependency story.
- **Vendor a hand-written bundle:** rejected; it would drift from source.

## Links

- Myna `DECISIONS.md` D-002 (JavaScript is a bounded second target)
- `tools/assemble.py`, `tools/portable.txt`, `tests/js/parity.test.mjs`
