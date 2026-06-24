# Schema Drift Probe

A small proof asset for outreach around structured-output reliability.

The goal is simple: test whether an LLM response still satisfies the schema a developer thought they were enforcing after it passes through a provider, wrapper, gateway, or parser.

This is intentionally narrow. It does not claim provider benchmarks yet. It gives us a runnable test shape, sample failures, and a clean artifact to send when asking teams whether this is the right layer to measure.

## What It Tests

The current cases cover:

- Extra keys that should be rejected under `additionalProperties: false`
- Missing required fields
- Enum drift
- Type drift, including strings where numbers are expected
- Nested array/object shape drift
- Tool-call argument shape drift

## Run It

From this directory:

```bash
python3 schema_drift_probe.py \
  --cases cases.json \
  --fixtures fixtures/sample_responses.json \
  --out reports/sample-report.md
```

The script has no third-party dependencies.

Or use:

```bash
make sample
```

## Read The Report

After running:

```bash
open reports/sample-report.md
```

The fixture names are not real providers. They represent common layers:

- `strict_fixture`: schema-valid responses
- `loose_wrapper_fixture`: responses that look usable but violate the schema
- `repair_parser_fixture`: responses after a hypothetical repair layer

## Why This Exists

Most structured-output examples stop at "the response parsed." In practice, teams need to know whether output still satisfies the exact schema contract they planned to rely on.

The outreach question this supports:

> Do teams already test schema behavior per provider/wrapper/model before production traffic, or is this still mostly handled after failures appear?

## Next Step

Replace the sample fixtures with real response logs from:

- LiteLLM
- Pydantic AI
- BAML
- LangChain/LangSmith
- Vercel AI SDK

Then compare results by provider, wrapper, and model.

Use `fixtures/real_run_template.json` as the shape for real logs.

For CI or automated checks, use:

```bash
python3 schema_drift_probe.py \
  --cases cases.json \
  --fixtures fixtures/real_run_template.json \
  --out reports/real-run.md \
  --fail-on-violations
```
