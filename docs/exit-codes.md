# speq exit codes (v1)

Stable exit code contract for CLI commands:

- `0` success.
- `1` test failures (runtime assertions failed).
- `2` validation/configuration error (invalid schema/layout/arguments).
- `3` internal/runtime error (unexpected exception).

## Usage notes

- `validate` returns `0` on valid input and `2` on contract violations.
- `run` returns `1` when tests execute but at least one test fails.
- Any unhandled exception path should return `3`.
