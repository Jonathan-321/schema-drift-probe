# Outreach Execution Plan

## Goal

Land a reply, call, or small collaboration by showing a concrete schema-drift probe instead of sending abstract cold emails.

The near-term offer is not "hire me." It is:

> I found a narrow reliability question around structured outputs and built a tiny probe. Is this the right layer to measure?

## Positioning

Use the artifact as proof that the outreach is serious:

- It is narrow enough to understand in under two minutes.
- It runs locally with no dependencies.
- It does not overclaim provider benchmarks.
- It gives teams something specific to correct, extend, or react to.

## Sequence

### Phase 1: Proof Asset

Status: done.

- Build a runnable schema-drift probe.
- Include sample cases and fixture failures.
- Generate a sample report.

### Phase 2: Make It Linkable

Status: next.

Best option: GitHub repo.

Suggested repo name:

```text
schema-drift-probe
```

Before sending the next batch, publish the folder to GitHub or another shareable page. Engineers are more likely to click a small repo than a long memo.

### Phase 3: First Batch

Status: drafted, not sent.

Targets:

- Boundary/BAML
- LiteLLM
- Pydantic AI

Action:

- Revise drafts to include the repo link after it is published.
- Send or schedule them one business morning.

### Phase 4: Second Batch

Status: research next.

Targets:

- LangChain/LangSmith
- Vercel AI SDK
- Instructor
- Outlines
- Portkey
- Helicone

Action:

- Find one specific docs page, GitHub issue, or product surface for each.
- Send one short question tied to that surface.

### Phase 5: Permissionless Help

Status: after the first replies or after one week.

Do not just follow up with "bumping this."

Better follow-up:

```text
One extra note since my last email: the failures that seem easiest to miss are not parse failures. They are schema-contract failures where the app still receives JSON, but enum, extra-key, or nested-type guarantees are gone.
```

Even better:

- Open a small GitHub issue against docs or examples.
- Add a test case or short PR if appropriate.
- Then email: "I opened this because I was testing X. Is this the right framing?"

## Success Metrics

Good outcome:

- Reply correcting the framing.
- Reply pointing to another person.
- Call with DevRel/product/engineering.
- Invitation to open an issue or PR.

Strong outcome:

- They ask for the probe or test cases.
- They share internal context.
- They suggest a collaboration, internship path, or intro.

## Guardrails

- Do not claim real provider results until we run real provider calls or logs.
- Do not send the sample fixture report as if it is a benchmark.
- Do not attach a long Notion memo in the first touch.
- Do not ask for a job in the first message.
- Keep the first email to one question.
