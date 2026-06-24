# Schema Drift Probe Report

Generated: 2026-06-24 23:31:55 UTC

## Summary

| Source | Passed | Failed | Total |
| --- | ---: | ---: | ---: |
| loose_wrapper_fixture | 0 | 5 | 5 |
| repair_parser_fixture | 4 | 1 | 5 |
| strict_fixture | 5 | 0 | 5 |

## Case Results

### strict_fixture / ticket_triage: PASS

Checks enum adherence, required fields, number type, and rejection of extra keys.

No schema violations found.

### strict_fixture / invoice_line_items: PASS

Checks nested arrays and object field types.

No schema violations found.

### strict_fixture / calendar_event: PASS

Checks strict object shape for event extraction.

No schema violations found.

### strict_fixture / tool_arguments: PASS

Checks whether tool call arguments stay strict when routed through wrappers.

No schema violations found.

### strict_fixture / safety_label: PASS

Checks nullable fields and controlled labels.

No schema violations found.

### loose_wrapper_fixture / ticket_triage: FAIL

Checks enum adherence, required fields, number type, and rejection of extra keys.

- $: unexpected key 'summary'
- $.category: value 'technical_bug' not in enum ['billing', 'bug', 'feature_request', 'account']
- $.priority: value 'urgent' not in enum ['low', 'medium', 'high']
- $.confidence: expected number, got string

### loose_wrapper_fixture / invoice_line_items: FAIL

Checks nested arrays and object field types.

- $.items[0]: unexpected key 'currency'
- $.items[0].quantity: expected integer, got string

### loose_wrapper_fixture / calendar_event: FAIL

Checks strict object shape for event extraction.

- $: missing required key 'date'
- $: unexpected key 'relative_date'
- $.duration_minutes: expected integer, got string

### loose_wrapper_fixture / tool_arguments: FAIL

Checks whether tool call arguments stay strict when routed through wrappers.

- $: unexpected key 'rationale'
- $.arguments: unexpected key 'include_orders'

### loose_wrapper_fixture / safety_label: FAIL

Checks nullable fields and controlled labels.

- $.label: value 'needs_review' not in enum ['allow', 'block', 'review']
- $.needs_human_review: expected boolean, got string

### repair_parser_fixture / ticket_triage: PASS

Checks enum adherence, required fields, number type, and rejection of extra keys.

No schema violations found.

### repair_parser_fixture / invoice_line_items: PASS

Checks nested arrays and object field types.

No schema violations found.

### repair_parser_fixture / calendar_event: FAIL

Checks strict object shape for event extraction.

- $: unexpected key 'timezone'

### repair_parser_fixture / tool_arguments: PASS

Checks whether tool call arguments stay strict when routed through wrappers.

No schema violations found.

### repair_parser_fixture / safety_label: PASS

Checks nullable fields and controlled labels.

No schema violations found.
