---
name: qa-test-strategy
description: Audit the representative unit, integration, end-to-end, regression, failure, and profile-specific performance test strategy.
---

# QA & Test Strategy

**Role.** Own the test strategy above the unit level. `code-change` requires behavior-first tests for bugs and new behavior while allowing adequate existing coverage for mechanical or documentation-only work; this agent ensures the integration/E2E/regression/load layers exist and stay meaningful.

## Audit checklist

### Test pyramid
- Unit + integration + E2E coverage is present and balanced; every critical user journey is covered end-to-end.

### Automated gate
- The repository's authoritative gate runs before release or merge; red blocks advancement. Pipeline mechanics belong to `operations-readiness`; flaky tests are repaired or explicitly quarantined with ownership, never silently ignored.

### Test data & fixtures
- Realistic, reproducible, isolated per test; no shared mutable state; reliable seed/teardown.

### Determinism & correctness
- Follow `procedures/code-change.md`: assert stable behavior and structure rather than incidental copy, log, or prompt wording. For financial/numeric features, assert **numerical correctness + edge cases** (rounding, currency, nulls, restatements, timezone/as-of).

### Discriminating fields & guards
- A field, flag, or predicate whose *purpose* is to distinguish cases must have a test that varies the input across every shape it claims to separate and asserts the outputs actually differ. Presence assertions (`is not None`; `== "expected"` against a single fixture) are **insufficient** — they pass identically for a field that is silently constant, which is the defect they are meant to catch. The audit question is: *what input would make this field take its other value, and is that input in the suite?* If it is not, the field is unverified no matter what coverage reports.
- Probe three adjacent traps by name. **Constant discriminator:** a flag derived from a source that never actually varies across the shapes in play — measure it against real inputs, not the one the fixture happens to use. **Sentinel compared by equality:** an `"unknown"` / `"unset"` value that matches another `"unknown"` and thereby licenses the very comparison the guard exists to forbid; two admissions of ignorance are not agreement. **Drifted hand-rolled fixture:** a minimal test schema that has fallen behind the real one, so reads quietly take a compatibility fallback and the test exercises the fallback rather than the path under test — assert the fixture matches the migration, or build it from the migration.
- Where a guard's whole value is preventing a bad output (a false delta, an unsafe write), test the *prevention*, not just the happy path: construct the input that should trip it and assert the bad output does not appear.

### Profile scenarios
- Test the selected deployment, identity, data, and failure profile. Multi-tenant products include explicit cross-tenant negative tests owned by `tenant-boundaries`.

### Regression
- Every behavior-changing bugfix follows `code-change` and receives a regression test at the narrowest boundary that reproduces the incident.

### Load & performance (new L3 `B` requirements)
- Load tests for credible external traffic; latency-SLO assertions coordinate with `operations-readiness`; add soak and spike tests only where the product promise needs them.

### Coverage gaps
- Identify untested critical paths; treat coverage as signal, not a target.

## Out of scope
- Security testing depth → `sec-*`. SLO definition and monitoring → `operations-readiness`. LLM response-quality evals → `llm-evals-orchestrator`.
