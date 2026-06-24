# Outreach Angle

Use this only after reviewing the draft and making sure the artifact link is available.

## Core Claim

I built a small schema-drift probe to understand where structured outputs stop matching the contract developers think they are enforcing.

Repo:

```text
https://github.com/Jonathan-321/schema-drift-probe
```

## Short Email Template

```text
Hi [Name],

I made a tiny schema-drift probe while looking at structured output failures across providers and wrappers.

The narrow thing I am trying to understand is whether teams usually test schema behavior before routing production traffic, or whether this is mostly handled after failures show up.

Repo: https://github.com/Jonathan-321/schema-drift-probe

Is this the right layer to think about, or would you frame it differently?

Best,
Jonathan
```

## Boundary/BAML Variant

```text
Hi Boundary team,

I made a tiny schema-drift probe after reading through BAML's structured-output docs.

The question I am trying to sharpen is whether BAML users usually test cross-provider schema drift before they ship, or whether parser repair is the main layer where this gets handled.

Repo: https://github.com/Jonathan-321/schema-drift-probe

If this is something Aaron or Vaibhav thinks about, I would value a quick pointer to the right mental model.

Best,
Jonathan
```

## LiteLLM Variant

```text
Hi Ishaan and Krrish,

I made a tiny schema-drift probe while looking at structured outputs through OpenAI-compatible gateways.

The question is whether LiteLLM users should test JSON schema behavior per provider/model before routing production traffic, or whether there is a better pattern you usually recommend.

Repo: https://github.com/Jonathan-321/schema-drift-probe

Am I thinking about this at the right layer?

Best,
Jonathan
```

## Pydantic AI Variant

```text
Hi Pydantic team,

I made a tiny schema-drift probe while looking at how agent frameworks handle structured outputs across providers.

One narrow question: when a provider returns output that is close to the schema but not valid, do you think of that mostly as a provider issue, or something Pydantic AI should help users test and measure?

Repo: https://github.com/Jonathan-321/schema-drift-probe

Best,
Jonathan
```

## Better Follow-Up Hook

Do not write "just following up" on these. Use a new finding:

```text
One extra note since my last email: the failures that seem easiest to miss are not parse failures. They are schema-contract failures where the app still receives JSON, but enum, extra-key, or nested-type guarantees are gone.
```
