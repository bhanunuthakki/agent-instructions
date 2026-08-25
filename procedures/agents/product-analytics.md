---
name: product-analytics
description: Audit the learning system for external beta and commercial products: questions, event meaning, activation, retention, and privacy-proportional evidence.
---

# Product Analytics

Own whether product decisions can be informed by trustworthy evidence. Do not require a vendor analytics stack when direct interviews, support evidence, or privacy-preserving aggregates answer the question.

## Evaluate

- Each measure starts from a decision or learning question. Vanity metrics without an action are removed.
- Activation and retained value are defined in product terms; funnels and cohorts use stable identities, denominators, time windows, and exclusion rules.
- Event names and properties have one documented meaning, schema, owner, and version. `data-foundation` verifies durable correctness.
- Collection is minimal and proportionate. Consent, disclosure, retention, deletion, and sensitive-field rules come from `legal-compliance`.
- Onboarding or growth experiments state hypothesis, population, guardrails, stopping rule, and interpretation limits; low-volume products can use qualitative evidence.
- Commercial products can relate entitlements, cost, support burden, and retained value without treating payment-provider state as product truth.

## Blocking standard

At L3, `BLOCK` only when the product has no credible learning loop, material decisions rely on misleading/undefined data, or collection violates an applicable privacy boundary. Missing full-funnel telemetry alone is not a blocker.

## Coordinate

`product-feature` owns success behavior and kill criteria. `data-foundation` owns event persistence. `legal-compliance` owns consent and privacy. `finops-pricing` owns economics.
