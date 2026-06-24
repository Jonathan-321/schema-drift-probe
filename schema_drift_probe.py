#!/usr/bin/env python3
"""Run strict schema checks against fixture responses.

This is deliberately dependency-free so it can be sent around or dropped into a
small repo without setup friction. It implements the JSON Schema subset used by
the local cases file, not the full JSON Schema spec.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CaseResult:
    source: str
    case_id: str
    passed: bool
    errors: list[str]


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: str) -> bool:
    actual = json_type(value)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        if not any(type_matches(value, item) for item in expected_type):
            errors.append(
                f"{path}: expected one of {expected_type}, got {json_type(value)}"
            )
            return errors
    elif isinstance(expected_type, str):
        if not type_matches(value, expected_type):
            errors.append(f"{path}: expected {expected_type}, got {json_type(value)}")
            return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum {schema['enum']!r}")

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errors.append(f"{path}: value {value!r} below minimum {schema['minimum']!r}")

    if "maximum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value > schema["maximum"]:
            errors.append(f"{path}: value {value!r} above maximum {schema['maximum']!r}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        if additional is False:
            extra_keys = sorted(set(value) - set(properties))
            for key in extra_keys:
                errors.append(f"{path}: unexpected key {key!r}")

        for key, subschema in properties.items():
            if key in value:
                errors.extend(validate(value[key], subschema, f"{path}.{key}"))

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors.extend(validate(item, schema["items"], f"{path}[{index}]"))

    return errors


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_probe(cases: list[dict[str, Any]], fixtures: dict[str, Any]) -> list[CaseResult]:
    by_id = {case["id"]: case for case in cases}
    results: list[CaseResult] = []

    for run in fixtures.get("runs", []):
        source = run["source"]
        responses = run.get("responses", {})

        for case_id, case in by_id.items():
            if case_id not in responses:
                results.append(
                    CaseResult(
                        source=source,
                        case_id=case_id,
                        passed=False,
                        errors=[f"missing response for case {case_id!r}"],
                    )
                )
                continue

            errors = validate(responses[case_id], case["schema"])
            results.append(
                CaseResult(
                    source=source,
                    case_id=case_id,
                    passed=not errors,
                    errors=errors,
                )
            )

    return results


def summarize(results: list[CaseResult]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for result in results:
        bucket = summary.setdefault(result.source, {"passed": 0, "failed": 0, "total": 0})
        bucket["total"] += 1
        if result.passed:
            bucket["passed"] += 1
        else:
            bucket["failed"] += 1
    return summary


def render_markdown(
    results: list[CaseResult],
    cases: list[dict[str, Any]],
    generated_at: str | None = None,
) -> str:
    case_lookup = {case["id"]: case for case in cases}
    summary = summarize(results)
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Schema Drift Probe Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        "| Source | Passed | Failed | Total |",
        "| --- | ---: | ---: | ---: |",
    ]

    for source, counts in sorted(summary.items()):
        lines.append(
            f"| {source} | {counts['passed']} | {counts['failed']} | {counts['total']} |"
        )

    lines.extend(["", "## Case Results", ""])

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        why = case_lookup[result.case_id].get("why", "")
        lines.extend(
            [
                f"### {result.source} / {result.case_id}: {status}",
                "",
                why,
                "",
            ]
        )
        if result.errors:
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")
        else:
            lines.append("No schema violations found.")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_json(results: list[CaseResult]) -> str:
    payload = {
        "summary": summarize(results),
        "results": [
            {
                "source": result.source,
                "case_id": result.case_id,
                "passed": result.passed,
                "errors": result.errors,
            }
            for result in results
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run schema drift checks.")
    parser.add_argument("--cases", default="cases.json", type=Path)
    parser.add_argument("--fixtures", default="fixtures/sample_responses.json", type=Path)
    parser.add_argument("--out", default="reports/sample-report.md", type=Path)
    parser.add_argument(
        "--generated-at",
        help="Override the markdown report timestamp, useful for reproducible samples.",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with code 1 when any case fails schema validation.",
    )
    args = parser.parse_args()

    cases = load_json(args.cases)
    fixtures = load_json(args.fixtures)
    results = run_probe(cases, fixtures)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.suffix.lower() == ".json":
        output = render_json(results)
    else:
        output = render_markdown(results, cases, args.generated_at)

    args.out.write_text(output, encoding="utf-8")

    summary = summarize(results)
    for source, counts in sorted(summary.items()):
        print(
            f"{source}: {counts['passed']} passed, "
            f"{counts['failed']} failed, {counts['total']} total"
        )
    print(f"wrote {args.out}")
    if args.fail_on_violations and any(counts["failed"] for counts in summary.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
