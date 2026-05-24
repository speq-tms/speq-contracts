# speq-contracts

Shared contract definitions for SPEQ DSL and outputs.

## Responsibilities
- Maintain schema compatibility and versioning.
- Provide source-of-truth structure for validation and tooling.

## Main paths
- `schemas/manifest/v1.json`
- `schemas/test/v1.json`
- `schemas/results/v1.json`

## Invariants
- Contract changes require synchronized updates in `speq-cli` and `speq-vscode-extension`.
- Prefer additive changes for backward compatibility in active versions.
