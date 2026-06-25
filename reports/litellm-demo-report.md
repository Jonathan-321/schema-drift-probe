# LiteLLM Provider-Change Regression Demo

Generated: 2026-06-24 00:00:00 UTC

Scenario: LiteLLM provider-change regression demo
Baseline route: `openai_primary`

This is an offline fixture, not a live provider benchmark. It shows the shape
of a pre-ship check a team could run before changing LiteLLM routing,
fallback, or model selection rules.

## Route Summary

| Source | Route | Schema | Latency | Cost | Regression flags |
| --- | --- | ---: | ---: | ---: | --- |
| openai_primary | primary: openai/gpt-4.1 | 5/5 | 820 ms | $0.0184 | none |
| anthropic_fallback | fallback: anthropic/claude-sonnet | 2/5 | 1250 ms | $0.0191 | 3 new schema failure(s); latency +52.4%; tool-call signature changed |
| cheap_route | cost-optimized: gemini-flash | 4/5 | 640 ms | $0.0042 | 1 new schema failure(s) |

## Tool-Call Signatures

| Source | Signature |
| --- | --- |
| openai_primary | `refund_order(customer_id:string, order_id:string)` |
| anthropic_fallback | `create_ticket(customer_id:string, summary:string)` |
| cheap_route | `refund_order(customer_id:string, order_id:string)` |

## Output-Contract Failures

### anthropic_fallback / ticket_triage
- $.priority: value 'urgent' not in enum ['low', 'medium', 'high']

### anthropic_fallback / invoice_line_items
- $.items[0].quantity: expected integer, got string

### anthropic_fallback / tool_arguments
- $.arguments: unexpected key 'summary'

### cheap_route / ticket_triage
- $: unexpected key 'notes'

## Read

A provider fallback can be correct at the HTTP layer and still regress a
workflow: slower route, higher cost, different tool call, or valid-looking
JSON that fails the exact downstream contract. This demo makes those changes
visible before production traffic moves.
