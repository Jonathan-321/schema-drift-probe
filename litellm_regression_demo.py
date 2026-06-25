#!/usr/bin/env python3
"""Render a LiteLLM-style provider-change regression report.

This stays offline and dependency-free. The fixture format mirrors the data a
team could log around a LiteLLM route: provider/model metadata, latency, cost,
tool calls, and strict output-contract responses.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schema_drift_probe import CaseResult, load_json, run_probe, summarize


@dataclass
class RouteResult:
    source: str
    route: str
    provider: str
    model: str
    latency_ms: float
    cost_usd: float
    schema_passed: int
    schema_failed: int
    schema_total: int
    tool_signature: str
    regressions: list[str]


def pct_delta(value: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return ((value - baseline) / baseline) * 100


def value_type(value: Any) -> str:
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


def tool_signature(tool_calls: list[dict[str, Any]]) -> str:
    signatures: list[str] = []
    for call in tool_calls:
        name = call.get("name", "<missing>")
        arguments = call.get("arguments", {})
        if isinstance(arguments, dict):
            arg_parts = [
                f"{key}:{value_type(arguments[key])}" for key in sorted(arguments)
            ]
            signatures.append(f"{name}({', '.join(arg_parts)})")
        else:
            signatures.append(f"{name}(<arguments:{value_type(arguments)}>)")
    return "; ".join(signatures) if signatures else "<no tool calls>"


def build_route_results(
    fixture: dict[str, Any],
    probe_results: list[CaseResult],
) -> list[RouteResult]:
    summary = summarize(probe_results)
    runs = fixture.get("runs", [])
    runs_by_source = {run["source"]: run for run in runs}
    baseline_source = fixture["baseline_source"]
    baseline = runs_by_source[baseline_source]
    thresholds = fixture.get("thresholds", {})
    max_latency_delta_pct = thresholds.get("max_latency_delta_pct", 35)
    max_cost_delta_pct = thresholds.get("max_cost_delta_pct", 25)
    baseline_counts = summary[baseline_source]
    baseline_tool_signature = tool_signature(baseline.get("tool_calls", []))

    route_results: list[RouteResult] = []
    for run in runs:
        source = run["source"]
        counts = summary[source]
        regressions: list[str] = []
        latency_delta = pct_delta(run["latency_ms"], baseline["latency_ms"])
        cost_delta = pct_delta(run["cost_usd"], baseline["cost_usd"])
        current_tool_signature = tool_signature(run.get("tool_calls", []))

        if source != baseline_source:
            if counts["failed"] > baseline_counts["failed"]:
                regressions.append(
                    f"{counts['failed'] - baseline_counts['failed']} new schema failure(s)"
                )
            if latency_delta > max_latency_delta_pct:
                regressions.append(f"latency +{latency_delta:.1f}%")
            if cost_delta > max_cost_delta_pct:
                regressions.append(f"cost +{cost_delta:.1f}%")
            if current_tool_signature != baseline_tool_signature:
                regressions.append("tool-call signature changed")

        route_results.append(
            RouteResult(
                source=source,
                route=run.get("route", source),
                provider=run.get("provider", ""),
                model=run.get("model", ""),
                latency_ms=run["latency_ms"],
                cost_usd=run["cost_usd"],
                schema_passed=counts["passed"],
                schema_failed=counts["failed"],
                schema_total=counts["total"],
                tool_signature=current_tool_signature,
                regressions=regressions,
            )
        )
    return route_results


def render_markdown(
    fixture: dict[str, Any],
    route_results: list[RouteResult],
    probe_results: list[CaseResult],
    generated_at: str | None = None,
) -> str:
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# LiteLLM Provider-Change Regression Demo",
        "",
        f"Generated: {generated_at}",
        "",
        f"Scenario: {fixture.get('scenario', 'LiteLLM regression demo')}",
        f"Baseline route: `{fixture['baseline_source']}`",
        "",
        "This is an offline fixture, not a live provider benchmark. It shows the shape",
        "of a pre-ship check a team could run before changing LiteLLM routing,",
        "fallback, or model selection rules.",
        "",
        "## Route Summary",
        "",
        "| Source | Route | Schema | Latency | Cost | Regression flags |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]

    for result in route_results:
        schema = f"{result.schema_passed}/{result.schema_total}"
        flags = "; ".join(result.regressions) if result.regressions else "none"
        lines.append(
            "| "
            f"{result.source} | {result.route} | {schema} | "
            f"{result.latency_ms:.0f} ms | ${result.cost_usd:.4f} | {flags} |"
        )

    lines.extend(
        [
            "",
            "## Tool-Call Signatures",
            "",
            "| Source | Signature |",
            "| --- | --- |",
        ]
    )
    for result in route_results:
        lines.append(f"| {result.source} | `{result.tool_signature}` |")

    failures = [result for result in probe_results if not result.passed]
    lines.extend(["", "## Output-Contract Failures", ""])
    if failures:
        for failure in failures:
            lines.append(f"### {failure.source} / {failure.case_id}")
            lines.extend(f"- {error}" for error in failure.errors)
            lines.append("")
    else:
        lines.append("No output-contract failures found.")
        lines.append("")

    lines.extend(
        [
            "## Read",
            "",
            "A provider fallback can be correct at the HTTP layer and still regress a",
            "workflow: slower route, higher cost, different tool call, or valid-looking",
            "JSON that fails the exact downstream contract. This demo makes those changes",
            "visible before production traffic moves.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a LiteLLM regression demo.")
    parser.add_argument("--cases", default="cases.json", type=Path)
    parser.add_argument(
        "--fixtures", default="fixtures/litellm_route_runs.json", type=Path
    )
    parser.add_argument("--out", default="reports/litellm-demo-report.md", type=Path)
    parser.add_argument(
        "--generated-at",
        help="Override report timestamp, useful for reproducible samples.",
    )
    parser.add_argument(
        "--fail-on-regressions",
        action="store_true",
        help="Exit with code 1 when any non-baseline route has regression flags.",
    )
    args = parser.parse_args()

    cases = load_json(args.cases)
    fixture = load_json(args.fixtures)
    probe_results = run_probe(cases, fixture)
    route_results = build_route_results(fixture, probe_results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    report = render_markdown(fixture, route_results, probe_results, args.generated_at)
    args.out.write_text(report, encoding="utf-8")

    for result in route_results:
        flags = ", ".join(result.regressions) if result.regressions else "none"
        print(
            f"{result.source}: {result.schema_passed}/{result.schema_total} "
            f"schema checks passed; regression flags: {flags}"
        )
    print(f"wrote {args.out}")

    if args.fail_on_regressions and any(result.regressions for result in route_results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
