# Conformance cases

Documents that a schema in `schemas/` must accept or reject, as plain data. No runner lives here yet —
wiring these into CI is [speq-tms/speq-docs#13](https://github.com/speq-tms/speq-docs/issues/13).

Each file is a list of cases:

```yaml
- name: what the case demonstrates
  expect: accept | reject
  doc: { … the artifact, inline … }
```

`expect` is what **`speq-cli` itself** does with the document, established by running
`speq validate` over a scratch project containing it — not what the schema happens to do. A schema that
disagrees with any case is wrong, which is the direction of authority this repository has to preserve.

One deliberate divergence is not covered here: the schemas are closed (`additionalProperties: false`) so
that editors flag misspelled keys, while `speq-cli` silently ignores keys it does not know. Cases with
unknown keys would therefore fail parity by design and are left out.
