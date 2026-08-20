# speq-contracts

Versioned JSON Schemas and compatibility contracts for the SPEQ ecosystem.

## Responsibilities
- Publish a schema for every `.speq` artifact type and for the CLI's machine-readable output.
- Keep those schemas in exact agreement with what `speq-cli` accepts and produces.
- Record compatibility decisions in `docs/compatibility.md`.

## Invariants
- **The schema follows the parser, not the other way round.** Before changing a schema, verify against
  `speq-cli/src/parser/mod.rs`, `src/manifest/mod.rs`, `src/generator/mod.rs`, and `src/cli/run.rs`.
- Schemas use `additionalProperties: false`, so an omitted field is not a gap — it is a rejection of valid input.
- When the DSL changes, `speq-cli`, `speq-contracts`, and `speq-vscode-extension` are updated in the same
  release candidate.
- The shared step definition is defined once and referenced; never copied between schemas.

## How we work

Full process: `speq-docs/docs/delivery/release-flow.md`. Read it before starting delivery work. Summary:

- **Issues live in [`speq-tms/speq-docs`](https://github.com/speq-tms/speq-docs/issues)**, not here. Work for
  this repository carries the `area/contracts` label.
- **Milestone title == RC branch name.** Milestone `v1.1.0` means branch `v1.1.0` in this repository.
  `backlog` is not a release and has no branch.
- **Find the current RC** — GitHub state is authoritative, not any checked-in file:

  ```bash
  gh api repos/speq-tms/speq-docs/milestones \
    --jq '.[] | select(.state=="open" and .title != "backlog") | .title'
  git ls-remote --heads origin 'v*'
  ```

- **Branch from the RC, never from `main`:** `git switch -c chore/contracts-<name> origin/<RC>`.
- **PR base is the RC**, never `main`. One final PR takes the RC into `main`.
- `Closes #N` does **not** work across repositories. Write `Part of speq-tms/speq-docs#N` in the PR, then close
  the issue manually after merge:
  `gh issue close N --repo speq-tms/speq-docs --comment "Landed in <PR url>."`
- Tick the checkbox in the epic issue when a child issue lands.

## Current state

Known open work is tracked under epic
[speq-tms/speq-docs#5](https://github.com/speq-tms/speq-docs/issues/5): the published test schema currently
rejects valid v1.0.0 specs, four artifact types have no schema at all, and the ATDD/coverage schema work was
never merged off `chore/contracts-atdd-and-coverage-schema`.
