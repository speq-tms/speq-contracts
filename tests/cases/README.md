# Conformance cases

Documents that a schema in `schemas/` must accept or reject, as plain data. No runner lives here yet —
wiring these into CI is [speq-tms/speq-docs#13](https://github.com/speq-tms/speq-docs/issues/13).

| File | Schema |
| --- | --- |
| `manifest-v1.yaml` | `schemas/manifest/v1.json` |
| `test-v1.yaml` | `schemas/test/v1.json` |
| `suite-v1.yaml` | `schemas/suite/v1.json` |
| `module-v1.yaml` | `schemas/module/v1.json` |
| `fixture-v1.yaml` | `schemas/fixture/v1.json` |
| `environment-v1.yaml` | `schemas/environment/v1.json` |

Each file is a list of cases:

```yaml
- name: what the case demonstrates
  expect: accept | reject
  parity: cli | schema-only | run-only     # optional, default cli
  why: >-                                   # required whenever parity is not cli
    …
  doc: { … the artifact, inline … }
```

## `expect` follows the CLI, not the schema

For the default `parity: cli`, `expect` records what **`speq-cli` itself** does with the document,
established by running `speq validate` over a scratch project containing it. A schema that disagrees with
such a case is wrong — that is the direction of authority this repository has to preserve.

## Where the schema is deliberately stricter

`parity: schema-only` marks a case the CLI accepts and the schema rejects. Every one of them is a
document that parses and then misbehaves later, so the strictness is the point:

- `speq-cli` ignores unknown keys in most places, so a misspelled or misplaced key is silently
  dropped — top-level suite hooks are simply never run. The schemas are closed so an editor says so.
  Module files are the exception: `speq validate` now reports an unknown top-level key itself, so the
  `module:` wrapper case is ordinary `parity: cli`.
- `coverage.failBelow` is any `f64` to the parser, so a threshold above 100 simply makes a gate that
  never passes. The schema bounds it to 0..100.
`environment/v1.json` is the one open schema, because every key other than `baseUrl` and `headers`
becomes a variable of that name and there is no fixed key set to close over.

`parity: cli-only` is the inverse: the CLI rejects the document and the schema accepts it, because
JSON Schema cannot express the constraint at all. Comparing two sibling numbers — `http.connectTimeoutMs`
against `http.timeoutMs` — is the only such case today. `expect` records what the *schema* does, so these
read `accept`; the `why` names the CLI rule the schema cannot mirror.

`parity: run-only` marks a case no `speq validate` pass covers — the manifest and the environment files
are read at every command's start rather than by `validate`, and a fixture is loaded only when a step's
`bodyFromFixture.ref` points at it.
