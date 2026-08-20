# Compatibility policy

## Versioning

- Contracts follow SemVer.
- Minor versions must remain backward compatible.
- Major versions may introduce breaking schema changes.

## Published schemas

| Artifact | Schema | Since |
| --- | --- | --- |
| `manifest.yaml` | `schemas/manifest/v1.json` | v1.0.0 |
| test spec | `schemas/test/v1.json` | v1.0.0 |
| `summary.json` | `schemas/results/v1.json` | v1.0.0 |
| `environments/*.yaml` | `schemas/environment/v1.json` | v1.1.0 |
| `suites/**/init.yaml` | `schemas/suite/v1.json` | v1.1.0 |
| `modules/*.yaml` | `schemas/module/v1.json` | v1.1.0 |
| `fixtures/*.yaml` | `schemas/fixture/v1.json` | v1.1.0 |
| shared definitions | `schemas/common/v1.json` | v1.1.0 |

`common/v1.json` describes no artifact of its own. It holds the definitions — steps, assertions,
conditions, imports, generator blocks — that are the same construct in more than one artifact, so they are
written once and referenced. See [schemas/README.md](../schemas/README.md) for how those references
resolve.

## Consumer responsibilities

- `speq-cli` is the primary consumer and must pin supported schema versions.
- `speq-github-runner` and `speq-vscode-extension` consume contracts through CLI output and should not introduce diverging runtime behavior.
- No consumer may keep a private, unverified copy of a schema. A vendored copy is a mirror of a pinned
  revision, checked in that consumer's CI. See [schema ownership](schema-ownership.md).
