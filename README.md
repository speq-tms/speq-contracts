# speq-contracts

Versioned schemas and compatibility contracts for the `speq` ecosystem.

## Scope

This repository is the source of truth for:

- manifest schema;
- test YAML schema;
- run JSON result schema;
- exit code contract and compatibility notes.

These are the only schemas. Components may vendor a mirror of a pinned revision, but never a private
copy that nothing verifies — see [docs/schema-ownership.md](docs/schema-ownership.md).

## Planned structure

```text
schemas/
  manifest/
  test/
  results/
docs/
```

## Versioning

- Schema changes follow SemVer.
- Breaking schema changes require migration notes.

## Status

Bootstrap complete. Ready for v1 contract freeze.
