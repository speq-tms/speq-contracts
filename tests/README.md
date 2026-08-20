# tests

The gate that keeps the published schemas honest.

| Path | Contains |
| --- | --- |
| `cases/` | Documents each schema must accept or reject, as data. See [cases/README.md](cases/README.md) |
| `../scripts/check-conformance.py` | The runner |

## Running it locally

```bash
pip install jsonschema pyyaml referencing
python3 scripts/check-conformance.py \
  --schemas schemas \
  --examples ../speq-examples \
  --cases tests/cases
```

Add `--summary <path>` to also validate a `summary.json` from a real run against
`schemas/results/v1.json`.

## What it checks, and why each one exists

**Examples.** Every `.speq` artifact in `speq-examples` validates against its schema. This is the check
that would have caught [#7](https://github.com/speq-tms/speq-docs/issues/7): a schema that fell behind the
CLI and started rejecting valid specs.

It runs twice — once with each schema preloaded under its declared `$id`, once with `$id` ignored and
references resolved against the file's location on disk. The cross-file `$ref`s into `common/v1.json` have
to work under both, because consumers do both.

**Cases.** Every conformance case behaves as it says. A schema can pass the examples check by accepting
everything; this is what stops it. Roughly a third of the cases are `reject`.

**Summary.** A `summary.json` produced by an actual run validates against `results/v1.json`. This is the
check that would have caught [#6](https://github.com/speq-tms/speq-docs/issues/6): the runtime emitting
`totals.pending`, `totals.error` and a whole `coverage` block that no published contract described, for an
entire release, with nothing going red.

## Which branch it checks against

The two repositories move together, so the gate has to pair a schema with the examples from the same
point in the release. It resolves that from the RC invariant — milestone title == RC branch name —
trying the pull request's **head** branch first, then its base, then `main`.

Head first matters on exactly one pull request: the final `RC -> main` merge. There the head names the
release candidate under test, and keying off the base would check `v1.1.0` against a `main` that predates
it — which fails, since `main` has not been rolled out yet.

The rollout merges one repository at a time, so between step 1 and step 2 `speq-contracts@main` is ahead
of `speq-examples@main`. The summary check runs whichever example project is actually present rather than
insisting on the newest one, so `main` does not go red inside that window.

## When it fails

Fix the schema, or fix whatever changed. Do not relax the schema to make the gate pass without reading
`speq-cli/src/` first — a permissive contract is how this repository got into the state
[#5](https://github.com/speq-tms/speq-docs/issues/5) had to repair.

If a case is genuinely wrong, change the case and say why in the PR. The cases encode the CLI's behaviour,
established by running `speq validate`, not the schema's.
