#!/usr/bin/env python3
"""Fail when the published schemas and reality disagree.

Three checks, because a schema can be wrong in three different directions:

  examples  every artifact in speq-examples validates against its schema.
            Catches a schema that has fallen behind the CLI and started
            rejecting valid input -- the #7 bug.

  cases     every conformance case in tests/cases/ is accepted or rejected
            exactly as it says. Catches a schema that passes the first check
            by being permissive.

  summary   a summary.json from a real run validates against results/v1.json.
            Catches the runtime emitting a field no contract describes -- the
            #6 bug, which survived a whole release.

The examples check runs twice, under both ways a consumer can resolve the
cross-file $refs: with each file preloaded under its declared $id, and with
$id ignored and references resolved against the file's location on disk.
Both must work or the relative reference strings are wrong for someone.

Usage:
    check-conformance.py --schemas <dir> --examples <dir> [--cases <dir>]
                         [--summary <summary.json>]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    import yaml
    import jsonschema
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError as exc:  # pragma: no cover
    sys.exit(f"missing dependency: {exc}. Install with: pip install jsonschema pyyaml referencing")

SCHEMA_NAMES = ["common", "manifest", "environment", "test", "suite", "module", "fixture", "results"]

# Which schema each artifact is validated against, by where it sits in a project.
CASE_FILES = {
    "manifest": "manifest-v1.yaml",
    "test": "test-v1.yaml",
    "suite": "suite-v1.yaml",
    "module": "module-v1.yaml",
    "fixture": "fixture-v1.yaml",
    "environment": "environment-v1.yaml",
}


class Failure(Exception):
    pass


def load_schemas(schemas_dir: pathlib.Path, by_path: bool) -> tuple[Registry, dict]:
    """Build a registry of every schema, keyed the way a consumer would key it."""
    registry = Registry()
    docs = {}
    for name in SCHEMA_NAMES:
        path = schemas_dir / name / "v1.json"
        if not path.is_file():
            raise Failure(f"missing schema: {path}")
        doc = json.loads(path.read_text())
        if by_path:
            # A consumer that ignores $id resolves relative references against
            # wherever the file came from. Restating $id as the file URI models that.
            doc["$id"] = path.resolve().as_uri()
        elif "$id" not in doc:
            raise Failure(f"{path} declares no $id")
        docs[name] = doc
        registry = registry.with_resource(
            doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012)
        )
    return registry, docs


def validators(schemas_dir: pathlib.Path, by_path: bool = False) -> dict:
    registry, docs = load_schemas(schemas_dir, by_path)
    out = {}
    for name, doc in docs.items():
        jsonschema.Draft202012Validator.check_schema(doc)
        out[name] = jsonschema.Draft202012Validator(doc, registry=registry)
    return out


def errors_for(validator, document) -> list[str]:
    found = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    return [f"{'.'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in found]


def artifacts(examples: pathlib.Path):
    """Yield (schema name, path) for every .speq artifact in the examples tree."""
    projects = []
    for entry in sorted(examples.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "manifest.yaml").is_file():
            projects.append(entry)
        elif (entry / ".speq" / "manifest.yaml").is_file():
            projects.append(entry / ".speq")
    if not projects:
        raise Failure(f"no .speq projects found under {examples}")

    for root in projects:
        yield "manifest", root / "manifest.yaml"
        for kind, subdir in (("environment", "environments"), ("fixture", "fixtures"), ("module", "modules")):
            if (root / subdir).is_dir():
                for path in sorted((root / subdir).rglob("*.y*ml")):
                    yield kind, path
        if (root / "suites").is_dir():
            for path in sorted((root / "suites").rglob("*.y*ml")):
                yield ("suite" if path.stem == "init" else "test"), path


def check_examples(schemas: pathlib.Path, examples: pathlib.Path) -> list[str]:
    problems = []
    counted = 0
    for by_path in (False, True):
        mode = "by-path" if by_path else "by-id"
        vs = validators(schemas, by_path)
        counted = 0
        for kind, path in artifacts(examples):
            document = yaml.safe_load(path.read_text())
            counted += 1
            for message in errors_for(vs[kind], document):
                problems.append(f"[{mode}] {path.relative_to(examples)} ({kind}): {message}")
        print(f"  {mode}: {counted} artifacts checked")
    if counted == 0:
        problems.append("no artifacts were checked at all")
    return problems


def check_cases(schemas: pathlib.Path, cases: pathlib.Path) -> list[str]:
    problems = []
    vs = validators(schemas)
    total = 0
    for kind, filename in CASE_FILES.items():
        path = cases / filename
        if not path.is_file():
            problems.append(f"missing case file: {path}")
            continue
        for case in yaml.safe_load(path.read_text()):
            total += 1
            found = errors_for(vs[kind], case["doc"])
            actual = "reject" if found else "accept"
            if actual != case["expect"]:
                detail = f" ({found[0]})" if found else ""
                problems.append(
                    f"{filename}: '{case['name']}' expected {case['expect']}, schema said {actual}{detail}"
                )
    print(f"  {total} conformance cases checked")
    if total == 0:
        problems.append("no conformance cases were checked at all")
    return problems


def check_summary(schemas: pathlib.Path, summary: pathlib.Path) -> list[str]:
    if not summary.is_file():
        return [f"summary not found: {summary}"]
    document = json.loads(summary.read_text())
    problems = [f"{summary.name}: {m}" for m in errors_for(validators(schemas)["results"], document)]
    print(f"  {summary} validated against results/v1.json")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas", required=True, type=pathlib.Path)
    parser.add_argument("--examples", required=True, type=pathlib.Path)
    parser.add_argument("--cases", type=pathlib.Path)
    parser.add_argument("--summary", type=pathlib.Path)
    args = parser.parse_args()

    cases = args.cases or args.schemas.parent / "tests" / "cases"

    problems: list[str] = []
    try:
        print("examples:")
        problems += check_examples(args.schemas, args.examples)
        print("cases:")
        problems += check_cases(args.schemas, cases)
        if args.summary:
            print("summary:")
            problems += check_summary(args.schemas, args.summary)
        else:
            print("summary: skipped (no --summary given)")
    except Failure as exc:
        problems.append(str(exc))

    if problems:
        print(f"\nFAILED: {len(problems)} problem(s)\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            "\nThe published contracts and reality disagree. Either the schema is wrong,\n"
            "or something changed that the schema has to describe. Do not relax the schema\n"
            "to make this pass without checking speq-cli's source first.",
            file=sys.stderr,
        )
        return 1

    print("\nOK: contracts, examples and conformance cases agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
