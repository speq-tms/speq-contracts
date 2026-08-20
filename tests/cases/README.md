# Conformance cases

Documents that a schema in `schemas/` must accept or reject, as plain data. No runner lives here yet —
wiring these into CI is [speq-tms/speq-docs#13](https://github.com/speq-tms/speq-docs/issues/13).

| File | Schema |
| --- | --- |
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

- `speq-cli` ignores unknown keys everywhere, so a misspelled or misplaced key is silently dropped —
  a `module:` wrapper produces a module with no actions, top-level suite hooks are simply never run.
  The schemas are closed so an editor says so.
- `validate_module_content` checks only the shape of `returns` expressions, never the steps of an
  action, so `speq validate` passes a module whose action cannot run
  ([#23](https://github.com/speq-tms/speq-docs/issues/23)).
- An environment's `headers` key is not applied as headers at all
  ([#21](https://github.com/speq-tms/speq-docs/issues/21)); the schema states the convention the key is
  named for.

`environment/v1.json` is the one open schema, because every key other than `baseUrl` becomes a variable
of that name and there is no fixed key set to close over.

`parity: run-only` marks a case no `speq validate` pass covers — environment files are read at run time,
and a fixture is loaded only when a step's `bodyFromFixture.ref` points at it.
