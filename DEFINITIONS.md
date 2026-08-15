# Shared Definitions

**Scope:** global
**Owner:** agent-system root
**Inherits:** none

**Lifecycle basis:** Seeded agent-system vocabulary ratified by the owner on 2026-08-13. These terms did not use the ordinary cross-project promotion path; any downstream override request forces scope review.

These terms have one meaning across projects. A descendant may add vocabulary but may not
override any term here. An override request is evidence that the term is too broad for this
scope: use a qualified local term or narrow/demote the global definition.

## Judge

**Definition.** An independent reviewer registered for a named purpose and versioned rubric that applies that rubric to evidence and returns a typed verdict. A judge may block only through a deterministic Gate. Registration proves identity and contract; calibration is a separate empirical status required before active enforcement.

## Judge Receipt

**Definition.** The typed terminal record for one sealed task attempt: repository and work anchor, routing inputs, required evidence and Judge seats, deterministic verdict, owner action, sampling state, outcome, and audit. A receipt is valid evidence only when it matches a prior append-only issuance event.

## Sealed Root Episode

**Definition.** The immutable statistical identity issued and appended before a task's sampling rank is revealed. Retries receive new attempt identities but inherit the root; a root that ever enters a Mandatory Control Review never enters an Ordinary Audit Sample.
**Not to be confused with.** A Critic, which is advisory, or a Grader, which scores one trial.

## Critic

**Definition.** An advisory reviewer that identifies weaknesses, alternatives, or questions without independently changing a Gate.
**Not to be confused with.** A Judge, whose typed verdict may be consumed by a Gate.

## Evaluation Suite

**Definition.** A repeatable set of representative trials, grading rules, and aggregation logic used to measure a system or treatment.
**Not to be confused with.** Verification of one observable state or a Judge's review of one task.

## Grader

**Definition.** Deterministic code or a governed model that scores one evaluation trial against a declared answer key or rubric.
**Not to be confused with.** The Evaluation that aggregates trials or the Judge that issues a task verdict.

## Verification

**Definition.** Deterministic confirmation of an observable claim, such as a test result, file hash, database invariant, citation date, or deployed revision.
**Not to be confused with.** Judgment where no complete deterministic oracle exists.

## Judge Verdict

**Definition.** A typed conclusion of `PASS`, `BLOCK`, `HOLD`, or `ABSTAIN` produced from declared evidence and a versioned rubric.
**Not to be confused with.** Authorization. A verdict never grants permission for an external, destructive, or owner-gated action.

## Gate

**Definition.** Deterministic policy that translates verification evidence and typed verdicts into an allowed or blocked state transition.
**Not to be confused with.** A model's prose recommendation.

## Calibration

**Definition.** Measurement of a grader, judge, or router against known cases, independent human review, or later outcomes, including false-pass and false-block rates.
**Not to be confused with.** Self-reported Confidence.

## Judge Confidence

**Definition.** A bounded claim about uncertainty attached to a specific output. Confidence is diagnostic data, not proof of correctness or Calibration.

## Review Tier

**Definition.** The minimum rigor required for a task, selected from J0 through J3 by deterministic impact and uncertainty signals. It is not a model-size label.

## J0

**Definition.** Deterministic verification sufficient to prove the relevant contract, with no model judgment required.

## J1

**Definition.** J0 evidence plus one registered, purpose-specific Judge for bounded, reversible work whose complete quality is not deterministic. Active enforcement additionally requires that Judge purpose to be calibrated.

## J2

**Definition.** Material but reversible work whose complete quality is not deterministic. J2 adds one purpose-specific specialist Judge; a second independent Judge is required for conflicting evidence, prior regression, a material first-judge finding, or explicit owner request. Different model families are optional.

## J3

**Definition.** Review of an actual irreversible or externally consequential action: high-impact production or security mutation, publication, legal or capital action, or unresolved J2 disagreement. Passing authorization requires the configured specialist review and explicit owner approval; BLOCK, HOLD, and ABSTAIN remain recordable without approval.

## Mandatory Control Review

**Definition.** A census review required by a named risk event such as J3, disagreement, override, or policy change. It is a control, not a random sample, and is excluded from ordinary failure-prevalence estimates.

## Ordinary Audit Sample

**Definition.** An unbiased, without-replacement selection of sealed task episodes used to estimate routing or execution failure within one declared task stratum.

## Tolerable Error Rate

**Definition.** The owner-ratified maximum material failure prevalence for a declared task stratum. It is a policy choice, not a property inferred from an arbitrary sampling percentage.

## Statistical Sample Target

**Definition.** The number of independent Ordinary Audit Sample episodes derived from a Tolerable Error Rate and confidence objective. A Sampling Fraction is an operational consequence of this target and available volume, not its statistical justification.

## Task Population Frame

**Definition.** An independently enumerable set of substantive coding or research work units, including units with no Judge Receipt. It is required to measure whether judging was invoked at all; a ledger of recorded receipts can measure execution correctness but cannot prove coverage of omitted work.

## Review-Tier Promotion

**Definition.** An owner-ratified, reversible move to a more demanding Review Tier after a ledger-derived audited miss or owner overturn. The system may recommend but never silently apply it. Low Judge calibration instead suspends that Judge purpose; a new blast radius is routed as new task risk.

## Review-Tier Demotion

**Definition.** An owner-ratified, reversible move to a less demanding Review Tier only after the declared per-stratum Statistical Sample Targets are met without undercutting the router's risk floor. The system may recommend but never silently apply it.

## Definition-Scope Promotion

**Definition.** A reviewed move of a ratified definition from its owning project or subtree to a broader scope after repeated identical meaning across real uses.

## Definition-Scope Demotion

**Definition.** A reviewed move of a definition to its true narrower owning scope. A downstream override request is evidence for this move, but the change holds until that owner is identified.

## Reconstructability

**Definition.** The guarantee that an entire system or project subsystem, including its state, schemas, data transformations, domain semantics, prompts, evaluation suites, and verification entrypoints, can be deterministically audited, rebuilt, and operated from locally owned, version-controlled repository assets alone without reliance on unversioned external harness state.

## Exit-Ready Design

**Definition.** The architectural discipline of keeping core business logic, data models, schemas, prompts, evaluation datasets, and verification suites runtime-neutral and locally owned, while treating runtime skills, hosted CI, subscription wrappers, provider SDKs/CLIs, model IDs, grounding connectors, and realtime formats as replaceable boundary adapters.
**Not to be confused with.** Universal portability, which claims unconstrained zero-effort migration across arbitrary environments without adapter boundaries.

# Registered cross-project collisions

The unqualified terms `Decision`, `conviction`, and `drift` have different existing project
meanings. Cross-project work must qualify them with their owning domain; they are not global
definitions.

