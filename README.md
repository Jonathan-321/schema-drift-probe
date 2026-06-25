# AI Workflow Regression Probe

A small, dependency-free demo for catching LLM workflow regressions before a
team changes model routes, fallbacks, providers, or wrappers.

The point is not "does the API return 200?" The point is whether the workflow a
developer depends on still behaves the same:

- output contracts still pass
- tool-call signatures stay compatible
- latency does not jump unexpectedly
- cost does not change silently

The repo started as a schema-drift probe. The stronger version treats schema
drift as one signal inside a broader model/provider-change regression check.

## 30-Second Demo

Run the LiteLLM-style route-change fixture:

```bash
make litellm-demo
```

It renders:

```text
reports/litellm-demo-report.md
```

Current fixture result:

| Route | Result |
| --- | --- |
| `openai_primary` | 5/5 schema checks, no regression flags |
| `anthropic_fallback` | 3 new schema failures, latency +52.4%, tool-call signature changed |
| `cheap_route` | 1 new schema failure, lower cost |

The important read: a fallback route can be correct at the HTTP layer and still
break the downstream workflow by changing tool arguments, output shape, latency,
or cost.

## Why This Exists

Teams using LiteLLM, model gateways, eval platforms, and agent frameworks often
change routes for good reasons: cost, latency, availability, model upgrades, or
fallback reliability.

Those changes can pass basic smoke tests while still breaking production
assumptions. Examples:

- a tool call changes from `refund_order(...)` to `create_ticket(...)`
- a field that was an integer becomes a string
- an enum gains an unsupported value
- a "cheaper" route saves money but changes output shape
- a fallback route works but makes the workflow slower or more expensive

This repo makes that failure mode concrete with small offline fixtures.

## Run It

From this directory:

```bash
make litellm-demo
```

For the original schema-only sample:

```bash
make sample
```

No third-party packages are required.

## What Gets Checked

The schema probe covers:

- extra keys rejected under `additionalProperties: false`
- missing required fields
- enum drift
- type drift
- nested array/object drift
- tool-call argument drift

The LiteLLM-style demo adds route-level checks:

- schema pass/fail counts per route
- latency deltas against the baseline route
- cost deltas against the baseline route
- tool-call signature changes

## What This Is Not

This is not a live provider benchmark.

The fixture names are intentionally offline examples, not claims about real
OpenAI, Anthropic, Google, or other provider behavior. The useful artifact is
the shape of the check: what a team could log and compare before moving traffic
to a new model route.

## Files

| File | Purpose |
| --- | --- |
| `litellm_regression_demo.py` | Renders the provider-change regression report |
| `schema_drift_probe.py` | Validates fixture outputs against JSON schemas |
| `fixtures/litellm_route_runs.json` | Offline route-change fixture |
| `reports/litellm-demo-report.md` | Human-readable demo output |
| `cases.json` | Contract cases used by both demos |

## Next Improvements

The next useful version would replace the offline fixture with real logs from a
wrapper or gateway:

- LiteLLM route logs
- LangSmith / LangGraph traces
- Pydantic AI structured outputs
- BAML structured-output runs
- Vercel AI SDK tool calls

Use `fixtures/real_run_template.json` as the starting shape for real logs.

For CI-style usage:

```bash
python3 schema_drift_probe.py \
  --cases cases.json \
  --fixtures fixtures/real_run_template.json \
  --out reports/real-run.md \
  --fail-on-violations
```
