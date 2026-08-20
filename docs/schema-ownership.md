# Schema ownership

## The rule

**The schemas published in this repository are the only schemas.** No component
keeps a private opinion of what a `.speq` artifact looks like.

A component may vendor a copy for offline use — a test suite that must not
reach the network, an editor extension that ships schema files inside its
package — but a vendored copy is a *mirror*, never a source. Every mirror must
be machine-verified against the published file, in that component's CI, so that
a divergence fails a build instead of accumulating silently.

## Why the rule exists

Between the v1.0.0 release and this document, four copies of the contract were
in circulation and all four disagreed:

| Copy | State when found |
| --- | --- |
| `speq-contracts` `main` | Oldest. Results schema had no `pending`, no `error`, no `coverage`; the test schema rejected valid v1.0.0 specs |
| `speq-contracts` branch `chore/contracts-atdd-and-coverage-schema` | Carried the ATDD and coverage work, written a release earlier, never merged |
| `speq-cli/tests/fixtures/contracts/results/v1.json` | A private vendored copy, ahead of `main` but behind the stranded branch |
| `speq-vscode-extension/schemas/*.json` | Its own draft-07 `speq-test`, `speq-module`, `speq-suite-init` files, materially more complete than anything published |

The failure was not that copies existed. It was that `speq-cli` validated its
own output against a file `speq-cli` controlled. The contract could rot for an
entire release without a single test going red — and it did: v1.0.0 shipped a
`summary.json` carrying `totals.pending`, `totals.error` and a `coverage` block
that the published results schema did not describe.

A copy nothing checks is not a copy. It is a fork.

## Disposition of each copy

- **`speq-contracts` `main` / the RC.** The source of truth. Everything else
  mirrors it.
- **`chore/contracts-atdd-and-coverage-schema`.** Cherry-picked onto the
  `v1.1.0` RC and deleted. Its widening of the top-level run `status` enum to
  include `pending` was dropped: `speq-cli/src/cli/run.rs` computes that field
  as `if failed == 0 && error_count == 0 { "passed" } else { "failed" }`, so a
  run whose tests are all pending still reports `passed`.
- **`speq-cli/tests/fixtures/contracts/`.** Kept, but demoted to a mirror. The
  revision it tracks is pinned in `tests/fixtures/contracts/CONTRACTS_PIN`, and
  `scripts/sync-contracts.sh --check` runs in `speq-cli` CI and fails on any
  byte-level difference. The results-contract test was widened at the same time
  to exercise every optional field the runtime can emit, so a schema that omits
  one now fails the build.
- **`speq-vscode-extension/schemas/`.** Decision recorded here, implementation
  deliberately out of scope for the v1.1.0 contract work — see below.

## Decision for `speq-vscode-extension`

The extension bundles three schema files and points the YAML language server at
them through `yaml.schemas` (`src/schemaAssociation.ts`). It needs files on disk
at activation time, so it will keep vendoring — under the same mirror rule as
`speq-cli`: a pinned revision, and a CI check that fails on drift.

Two things must be reconciled before that mirror can be turned on, which is why
it is not part of this change:

1. **Draft and `$id` mismatch.** The extension files are draft-07 and claim
   `https://speq.dev/schemas/test.schema.json`, while the published contracts
   are draft 2020-12 under `https://speq.dev/schemas/test/v1.json`. Two
   different documents currently assert authority over the same namespace.
2. **The extension is ahead in content, behind in currency.** Its test schema
   already covers `imports`, `bodyFromFixture`, `action`, `properties`,
   `condition`, `as`, `inline` and `gen` — but it predates the ATDD and coverage
   work, so it has no `status`. It is starting material for the published
   schemas, not a drop-in replacement, and every rule in it has to be re-checked
   against `speq-cli/src/parser/mod.rs` before being published.

The published schemas therefore absorb the extension's coverage first
(`speq-tms/speq-docs#7` and `#8`); the extension then switches to mirroring
them.

## Checklist for a contract change

1. Change the schema here, and merge it here first.
2. Move each mirroring component's pin to the revision containing the change.
3. Re-run that component's sync so the mirror is byte-identical, and commit it
   with the runtime change it describes.

A runtime change that lands before step 1 is the bug this document exists to
prevent.
