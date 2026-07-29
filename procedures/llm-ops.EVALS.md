# LLM eval and routing reference

Use this reference for new evals, judges, prompt comparisons, or cheaper-model routing.

## Match the eval to the purpose

- Golden set: deterministic extraction, classification, or schema tasks with known outputs. Include adversarial and prompt-injection cases where inputs are untrusted.
- Rubric judge: prose or judgment tasks. Score versioned facets into a validated schema; do not compare exact wording.
- Outcome calibration: predictions or recommendations that reality can grade later. Keep this separate from immediate response-quality scoring.

Key evals by `(purpose, prompt_version, schema_version, model, reasoning)` so each treatment is attributable. Preserve representative production shapes, including empty, long-context, malformed, and degraded-path cases.

## Brand-blind pairwise comparison

Present outputs as Response A and Response B without provider, model, prompt-version, cost, or incumbent labels. Run both slot orders and require position-consistent results. The verdict schema contains `winner: A|B|tie`, confidence or margin, facet scores, and rationale tied to the rubric.

A model or prompt candidate that errors, times out, or violates the output contract loses that case.

## Conservative downgrade

Default thresholds are starting policy, not universal truth:

- below 4 cases: `INSUFFICIENT_DATA`; use at least 10 for high-stakes purposes;
- `SWITCH_DOWN` only when every judge has the candidate at parity or better on at least 80% of cases and cross-judge agreement is at least 60%;
- `KEEP_INCUMBENT` when any judge gives the incumbent a majority;
- otherwise `HOLD`.

Write a switch as reversible data, not a code edit. Continue sampling and automatically clear the override when later evidence falls below the gate. Token and cost improvements count only after the quality contract passes.

## Govern the judge

The judge is its own purpose with a model choice, schema, prompt version, ledger rows, and budget. Unparseable judgments fail closed. Periodically compare a sample with human review and record agreement. Escalate the judge only for purposes where the cheaper tier fails that calibration.

## Prompt migration

Start with the current prompt and effective reasoning. Test one change group at a time:

1. target model with the existing prompt and preserved reasoning;
2. the same model one reasoning level lower when supported;
3. removal of repeated instructions, irrelevant examples, or unused tools;
4. the smallest targeted instruction needed for a measured regression;
5. optional features as a separate treatment.

Compare task success, schema validity, evidence completeness, tool behavior, latency, tokens, cost, retries, and fallback rate.
