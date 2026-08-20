# Compatibility policy

## Versioning

- Contracts follow SemVer.
- Minor versions must remain backward compatible.
- Major versions may introduce breaking schema changes.

## Consumer responsibilities

- `speq-cli` is the primary consumer and must pin supported schema versions.
- `speq-github-runner` and `speq-vscode-extension` consume contracts through CLI output and should not introduce diverging runtime behavior.
- No consumer may keep a private, unverified copy of a schema. A vendored copy is a mirror of a pinned
  revision, checked in that consumer's CI. See [schema ownership](schema-ownership.md).
