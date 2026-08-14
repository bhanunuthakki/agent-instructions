---
name: judging
description: Route substantive coding and research work through J0-J3 evidence tiers, typed judge receipts, risk controls, and statistically derived audit samples. Use for judge, critic, evaluation, review rigor, substantive code or research validation, or high-impact decisions.
---

# Evidence-Governed Judging

Use the global meanings in `DEFINITIONS.md`. Review tiers describe rigor, not model size. Every
task begins with deterministic evidence; judgment adds coverage only where the oracle is incomplete.
Infrastructure, schema, evidence, provider, or budget failure produces `HOLD` or `ABSTAIN`.

Policy `1.1.0` is shadow-only for ordinary statistical enforcement until the owner ratifies a
Tolerable Error Rate and confidence target for each coding/research stratum. Judge purposes are
registered but remain calibration-shadowed. Historical receipts remain bound to their immutable
policy snapshots.

## Issue before judging

`route` is a read-only preview and does not create a sealed episode. Governed work uses the exclusive
`begin` writer, which appends the issuance before revealing the sampling identity:

```powershell
python C:\Users\Bhanu\.gemini\snippets\judge_governance.py begin `
  --task-id <display-id> --task-class coding|research --signals <signals> `
  --repository-id <repo> --work-anchor <commit-pr-or-work-unit>
```

Use `--retry-of <prior-receipt.json>` for a retry. A retry keeps repository, work anchor, policy,
task class, and root episode identity. One exclusive local writer owns issuance and completion.
Every issuance must reach a terminal receipt, and one repository/work anchor may have only one live
root; abandoned or competing roots fail the ledger gate.

- **J0:** deterministic proof is complete and no unresolved risk signal remains.
- **J1:** bounded, reversible work whose semantic quality needs one purpose-specific Judge.
- **J2:** material but reversible uncertainty. One specialist Judge is standard. Conflicting
  evidence, prior regression, an explicit owner request, or a material first-judge finding requires
  an independent second Judge. Different model families are optional.
- **J3:** an actual irreversible or externally consequential action: high-impact production or
  security mutation, publication, legal or capital action, owner request, or unresolved J2
  disagreement. Passing authorization requires the configured specialist review and explicit owner
  approval. BLOCK, HOLD, and ABSTAIN do not require approval.

J2 routing counts independent risk groups, not raw flags: evidence uncertainty, scope/state,
novelty, observed failure, and economics. Conflicting evidence, a missing oracle, and prior
regression, and an owner request for a second Judge are direct J2 signals; otherwise two distinct
groups are required. Correlated flags in one group count once. `deterministic_complete` cannot
coexist with unresolved risk.

The root agent owns synthesis. Never leak the intended answer into a judge brief. Judges return
typed evidence and findings; deterministic policy computes the final gate.

## Receipt and failure contract

Policy 1.1 receipts receive a centrally generated `episode_id`. Retries use a new attempt ID but
inherit the sealed `root_episode_id`; display-task renaming cannot change the sampling unit. Record
the derived routing profile, recommended and actual tier, typed deterministic proof, Judge
identities/purposes/registry versions/rubrics/evidence, verdict, disagreement, owner action, policy
change, failure code, sampling state, outcome, and audit. A registered purpose and rubric are
required; active enforcement additionally rejects purposes without calibrated status.
Evidence references are typed but not yet verifier-backed, so policy 1.1 cannot enter active mode.

```powershell
python C:\Users\Bhanu\.gemini\snippets\judge_governance.py complete <receipt.json>
```

`complete` validates the terminal receipt, verifies every sealed field against the issuance ledger,
and appends it idempotently. A later observed result uses append-only `record-outcome` keyed to the
sealed root; it never rewrites the terminal receipt. `validate` checks the typed receipt alone and
therefore does not prove issuance.

`PENDING` cannot validate as final. A blocker cannot be averaged away. A J3 PASS without positive
owner approval is `HOLD`; a J3 BLOCK remains BLOCK. A Judge Verdict never authorizes an external
side effect.

## Adaptation boundary

Promotion and demotion evidence is derived only from the append-only ledger. Callers cannot supply
receipt totals, strata, miss counts, or independence claims. The system reports a recommendation
and evidence; automatic policy changes are forbidden. A completed audit finding or owner overturn
recommends a one-tier promotion review. Zero failures across the full Statistical Sample Target in
both coding and research recommends a one-tier demotion review. Owner ratification is required,
and no demotion may undercut the current router floor. Evidence from another tier or a Mandatory
Control Review cannot satisfy an ordinary demotion target.

```powershell
python C:\Users\Bhanu\.gemini\snippets\judge_governance.py review-policy `
  governance\judge_ledger.jsonl --current-tier J1 --signals <signals>
```

Read [judging.EVALS.md](judging.EVALS.md) for sampling, audit-schema, and calibration rules, and
[judging.REFERENCE.md](judging.REFERENCE.md) for primary-source provenance. Use `llm-ops` when a
persistent application LLM call, prompt, model, or budget changes.
