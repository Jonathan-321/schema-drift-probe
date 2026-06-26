SAMPLE_GENERATED_AT := 2026-06-24 00:00:00 UTC

.PHONY: sample sample-json litellm-demo litellm-ci clean

sample:
	python3 schema_drift_probe.py --cases cases.json --fixtures fixtures/sample_responses.json --out reports/sample-report.md --generated-at "$(SAMPLE_GENERATED_AT)"

sample-json:
	python3 schema_drift_probe.py --cases cases.json --fixtures fixtures/sample_responses.json --out reports/sample-report.json

litellm-demo:
	python3 litellm_regression_demo.py --cases cases.json --fixtures fixtures/litellm_route_runs.json --out reports/litellm-demo-report.md --json-out reports/litellm-demo-report.json --generated-at "$(SAMPLE_GENERATED_AT)"

litellm-ci:
	python3 litellm_regression_demo.py --cases cases.json --fixtures fixtures/litellm_route_runs.json --out reports/litellm-demo-report.md --json-out reports/litellm-demo-report.json --generated-at "$(SAMPLE_GENERATED_AT)" --fail-on-regressions

clean:
	rm -rf reports __pycache__
