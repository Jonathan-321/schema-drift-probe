.PHONY: sample sample-json clean

sample:
	python3 schema_drift_probe.py --cases cases.json --fixtures fixtures/sample_responses.json --out reports/sample-report.md

sample-json:
	python3 schema_drift_probe.py --cases cases.json --fixtures fixtures/sample_responses.json --out reports/sample-report.json

clean:
	rm -rf reports __pycache__
