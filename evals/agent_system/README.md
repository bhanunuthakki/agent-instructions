# Agent-system evaluations

`procedure_routing_cases.jsonl` checks whether a request selects the smallest owning procedure.

`interaction_outcome_cases.jsonl` defines response-level contracts for altitude, scope, handoff, closure, and project semantics. Each case names the exact global, project, and procedure context assembled for its candidate. Run isolated candidate calls followed by a model-blind independent judge call with:

```bash
python3 snippets/interaction_outcome_eval.py
```

Each run creates a new timestamped attempt directory under `.tmp/interaction_outcome_eval/` and
refuses to reuse it. `started.json` records corpus, instruction, and evaluation-contract hashes before any model call. A successful run adds
`result.json`; a transport, interruption, or schema failure adds `error.json` with its stage, case,
error type, and accumulated usage. Successful receipts record instruction hashes, corpus hash,
candidate and judge identities, measured usage, responses, verdicts, and deterministic scores.
Judge-only criteria are withheld from candidate prompts, and the judge is told that all quoted
payload fields are untrusted data. Every verdict includes a concise evidence-grounded rationale so
criterion omissions, prohibited behavior, and dimension scores below 4 can be independently audited.
Candidate responses and raw judge outputs are retained even when a later stage fails. A judge output
that fails deterministic schema validation receives at most one format-only repair call: the malformed
output, parser error, repair output, and both usages remain in the receipt; the first schema-valid
verdict is accepted, and a second invalid output ends the attempt. A valid unfavorable verdict is never
retried.

The corpus deliberately pairs conservative boundary cases with positive counterfactuals where action,
handoff, completion, mutation, or broader scope is correct. It also samples high-risk project
boundaries for Angel Memos, Blog Engine, Resume, Wealthplan, Reading Companion, and maintenance.
Each response is judged independently to avoid cross-case anchoring.

The live threshold is calibrated to an A− floor rather than zero-variance perfection. Each attempt
requires at least 20/22 whole cases passing, 0.95 required-outcome recall, 1.0 avoidance accuracy, no response over 250 words,
every quality-dimension average at least 4.0/5, no case dimension below 3/5, and no scope/authority or
completion-truth score below 4/5. Quality dimensions are first-screen altitude, scope/authority,
actionability, technical precision, completion truth, and context economy.

Release confidence requires two consecutive attempts with identical corpus, instruction,
evaluation-contract, and candidate/judge model identities. Both must meet the per-attempt floor; their
combined required-outcome recall must be at least 0.97; every criterion and every case must pass in at
least one attempt. The checker rejects a selected pair when another completed same-identity attempt
falls between them, so an unfavorable run cannot be skipped. Run the deterministic pair check with:

```bash
python3 snippets/interaction_outcome_eval.py --qualify-pair FIRST_RESULT SECOND_RESULT
```

Two perfect 22/22 attempts remain an A+ signal, not the A− floor. Until the pair check passes this
suite is shadow evidence, not a production model qualification. Do not rerun an unchanged revision
merely to select a favorable stochastic result. A failed current-revision attempt remains evidence
until the relevant instruction/case/contract is corrected or a documented transport/model error
invalidates the attempt. Unit tests inject a fake transport and remain deterministic and offline.
