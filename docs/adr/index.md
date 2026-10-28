# Architecture decisions

Each decision records context, the choice, its consequences, and the alternatives that
were rejected.

| ADR | Decision |
|---|---|
| [0001](0001-portable-core.md) | One portable kernel with explicit laws and executable proof |
| [0002](0002-ledger-and-costing.md) | Append-only ledger, per-location moving average |
| [0003](0003-js-assembly.md) | Build-time assembly for the JavaScript target |
| [0004](0004-http-contract.md) | Portable HTTP contract with thin adapters |
| [0005](0005-browser-demo.md) | Browser demo from the same kernel |

The process is in [CONTRIBUTING](https://github.com/jhicksdev/mynastock/blob/main/CONTRIBUTING.md):
a change to a boundary, dependency, data model, or language workaround needs an ADR.
