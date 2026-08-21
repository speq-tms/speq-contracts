# Schemas

One schema per `.speq` artifact type, plus `common/` for the definitions more than one of them needs.

| Artifact | Schema |
| --- | --- |
| `manifest.yaml` | `manifest/v1.json` |
| `environments/*.yaml` | `environment/v1.json` |
| test spec under `suites/` | `test/v1.json` |
| `suites/**/init.yaml` | `suite/v1.json` |
| `modules/*.yaml` | `module/v1.json` |
| `fixtures/*.yaml` | `fixture/v1.json` |
| `summary.json` from a run | `results/v1.json` |
| — shared definitions — | `common/v1.json` |

## `${VAR}` placeholders

Any string value in any of these artifacts may hold `${VAR}`, resolved from the OS environment as the file
is loaded. `${VAR:-default}` supplies a fallback; `$${VAR}` is a literal. A placeholder with neither a
variable nor a default is a load-time error, not an empty string.

This is invisible to the schemas by design. Substitution happens *before* a document is deserialised, so
what a schema sees is the resolved value — a placeholder is never validated against the field's type, and
no schema needs a pattern permitting the syntax. The rule to preserve is the inverse one: a field must not
be narrowed with `pattern`, `enum` or `format` in a way that a resolved value could fail while the
placeholder text would have passed, because the schema is what an editor checks before resolution is
possible.

## Resolving the cross-file references

A step is the same construct in a test spec, a suite hook and a module action, so it is defined once in
`common/v1.json` and referenced from the other three. Those references are written **relative**
(`../common/v1.json#/$defs/step`), which resolves correctly under either way a consumer loads the set:

- **Preload by `$id`.** Register each file under the `$id` it declares. Relative references resolve
  against the referring file's `$id`, landing on `https://speq.dev/schemas/common/v1.json`.
- **Resolve by location.** Ignore `$id` and let references resolve against wherever the file was
  retrieved from — a local directory, or a raw URL over this repository.

Both are exercised on every artifact in `speq-examples` before a change to these files is merged.

What does **not** work is fetching one file alone and expecting its references to dereference over the
network: `speq.dev` does not currently resolve, so the `$id` values are identifiers, not addresses. Take
the directory as a unit. Making the `$id` host serve these files is tracked as
[speq-tms/speq-docs#22](https://github.com/speq-tms/speq-docs/issues/22).

## Open and closed

Every schema here is closed (`additionalProperties: false`) so an editor flags a misspelled key, with one
deliberate exception: `environment/v1.json`. The CLI turns every environment key other than `baseUrl` into
a variable of that name, so an environment file has no fixed key set and the schema must stay open.

Note that `speq-cli` itself ignores unknown keys everywhere. A document these schemas reject for an
unknown key would still run — the strictness is an editing aid, not a claim about the runtime.
