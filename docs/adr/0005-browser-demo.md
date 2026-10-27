# ADR-0005: Browser demo from the same kernel

**Status:** Accepted
**Date:** 2026-10-27
**Supersedes:** none

## Context

The portfolio claim is that one kernel runs on a Python server and in a browser. A demo
that reimplements the ledger would undermine it. The JavaScript target is constrained:
myna 0.4.2 rejects relative imports and cannot bundle, so a multi-file program must be
assembled into one file before compilation.

The demo also has to be static: no backend, no build service, no CDN. GitHub Pages serves
files; hash routing avoids deep-link 404s.

## Decision

**One source graph, two manifests.**

- `tools/portable.txt` is the shared kernel, in dependency order.
- `tools/web.txt` adds the browser adapter, DOM helpers, views, and entry point.
- `tools/assemble.py --extra tools/web.txt` concatenates them, strips headers and
  imports at column 0, rejects duplicate top-level names, and emits one `@target(js)`
  file. `myna compile -t js` produces the bundle.
- The demo calls `dispatch(Request)` for reads and writes. Routes, validation, errors,
  idempotency, and averages are identical to the server.
- `LocalRepo` extends the in-memory repository and overrides its mutators to persist the
  whole document after a successful `apply`. One `setItem` mirrors the server's one
  transaction.
- Rendering is plain DOM through `innerHTML` with an explicit `esc()` for every
  user-controlled value. No framework, no virtual DOM, no runtime dependency.
- The site is generated: `tools/build_site.py` copies static shells, compiles curated
  files for the source viewer, and `tools/audit_site.py` fails on missing assets or
  oversized artifacts. `pages.yml` uploads `site/` as a Pages artifact.
- `tests/js/demo-smoke.mjs` boots the bundle against a small DOM stub, renders every
  route, and posts a receipt through the pipeline. Layout remains a manual checklist in
  `docs/demo.md`.

## Consequences

- The demo bundle is ~100 KB and loads without a backend or third-party script.
- The browser and server share every domain rule; only storage, clock, IDs, and transport
  differ.
- Domain changes automatically flow to the demo, and the Node parity suite catches
  target-specific regressions.
- The assembler is a temporary tool. It must be deleted when upstream JS bundling lands.
- No SSR, no hydration, no client-side framework. Interactivity is event delegation and
  full re-renders, which is appropriate at demo scale.
- No browser automation in CI. The smoke test covers execution, not pixels; the manual
  checklist is the contract for layout.

## Alternatives considered

- **Reimplement the demo in JavaScript:** rejected; guaranteed drift.
- **React or another framework:** rejected; adds a build toolchain and runtime to a
  project whose point is zero dependencies.
- **Server-hosted demo:** rejected; visitors should not need a backend, and Pages cannot
  run Python.
- **Hand-written static HTML only:** rejected; the demo must exercise real writes.
- **Store raw dataclasses in `localStorage`:** rejected; hydrate plain JSON into the
  same entity types so repository behavior is unchanged.

## Links

- `docs/demo.md` — routes, limits, manual QA
- `docs/adr/0003-js-assembly.md` — why the assembler exists
- `src/mynastock/web/` — browser adapter and UI
