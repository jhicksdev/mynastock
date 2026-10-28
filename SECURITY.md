# Security Policy

## Supported versions

MynaStock 1.x is supported. Only the latest release and `main` receive fixes.

## Reporting a vulnerability

Do not open a public issue. Use GitHub's private vulnerability reporting on the
repository, or contact the maintainer through the profile linked on the repository page.
Include a minimal reproduction, affected version, and impact. Expect an initial response
within a few days.

## Threat model (v1)

MynaStock is designed for a **single tenant on a trusted network**. It deliberately does
not ship authentication, authorization, TLS termination, or rate limiting. Do not expose
it directly to the internet; put it behind an authenticating reverse proxy.

What the project does enforce:

- All SQL uses bound parameters; no string-concatenated queries.
- No file uploads, no user-supplied file paths, no template evaluation of request data.
- Request bodies are validated against explicit limits (quantity and cost bounds) before
  entering the ledger.
- The runtime artifact has **no third-party Python dependencies**; the attack surface is
  the Python standard library plus the application itself.
- The browser demo stores data only in the visitor's `localStorage`; it makes no network
  requests and has no backend.

Out of scope for v1: multi-tenant isolation, audit-grade identity, secrets management.
Those are roadmap items, not assumptions.
