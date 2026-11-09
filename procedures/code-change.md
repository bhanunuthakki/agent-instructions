---
name: code-change
description: Implement, fix, refactor, prototype, or review code using Poteto’s engineering playbooks, repository tests, and conventions. Use for features, bug fixes (/tdd), refactors, throwaway prototypes, ambitious multi-part work (/figure-it-out), architectural sketches (/architect), blast-radius proof (/blast-radius), adversarial review (/interrogate), comment hygiene (/no-comments), performance/hillclimbing (/benchmark-checklist), or PR/stack shipping.
---

# Code Change

Implement the authorized outcome by applying Poteto’s engineering playbooks and principles (`pstack`) to the repository’s actual surfaces, tests, and conventions. Approved intent and domain contracts define required behavior; preserve unrelated public behavior and replace an inadequate design from first principles (`redesign-from-first-principles`) when local patches cannot achieve a clean shape.

## Core triggers and non-negotiables

1. **Ground first (`/how` / `/why`):** Before a nontrivial change or architectural choice, inspect the affected interface, nearby tests, repository commands, and current diff. For unfamiliar subsystems or historical constraints, run [code-archaeology](code-archaeology.md) (`/how` for mechanics, `/why` for lineage and `Preserve / Change / Avoid / Risk` constraints).
2. **Settle empirical forks by running code (`never-block-on-the-human`):** Before asking the user a "which approach" or "what should this do" question, check whether the answer is an observable technical fact (behavior, timing, layout, output, or test separation). If so, run a quick probe or throwaway prototype in `scratch/` and let the result decide. Ask the user only for genuine product/preference decisions or irreversible/external boundaries under the global collaboration contract.
3. **Model the domain first (`model-the-domain`):** Name the data shape before writing logic. Encode domain state in a discriminated union, state machine, declarative table/registry, or typed model rather than scattered booleans, string heuristics, or repeated shape assumptions across files.
4. **Sketch before crossing boundaries (`/architect`):** When new or changed logic crosses a module or function boundary or locks in a non-trivial data shape, sketch the types and signatures first via [code-change.REVIEW.md](code-change.REVIEW.md).
5. **Throughput checkpoint:** For nontrivial multi-step work, record four items (keeping inapplicable items as `n/a: <reason>`):
   - *Blocking first steps* (gates and shared primitives that must land before fan-out);
   - *Independent workstreams* (disjoint files, services, or layers that can run in parallel);
   - *Shared mutable state* (default to splitting targets per `separate-before-serializing-shared-state`; serialize only for true invariants);
   - *Smallest safe decomposition* (if one serial worker is best, state why).

## Playbooks by coding task

### Feature
1. Ground with `/how` over the affected subsystem and run `/architect` if crossing module/function boundaries.
2. Choose the organizing data structure (`model-the-domain`) and write the throughput checkpoint. When the implementation admits multiple valid shapes, use [agent-operations.ARENA.md](agent-operations.ARENA.md) (`/arena`) to compare candidates and graft the best mechanisms.
3. Port shared-primitive improvements to all consumers. Build, verify, and commit in small verifiable units (`sequence-verifiable-units`) rather than batching checks at the end.
4. Verify user-observable behavior on the real surface (`prove-it-works`; "inconclusive" or wrong-surface is not a pass). If the design is contested, run `/interrogate` ([code-change.REVIEW.md](code-change.REVIEW.md)) before shipping.

### Bug fix (`/tdd`)
Every shipped line must trace to runtime evidence (`fix-root-causes`). A guard is a fix only when the state it handles is legitimate; revert "might help" belt-and-suspenders that evidence refutes.
1. **Reproduce first** on the matching surface. Synthesize the trigger, tighten conditions, or instrument until it fires; ask the user to reproduce only with a specific reason the local surface cannot reach the target.
2. **Binary-search the root cause:** Seed hypotheses with `/how` and `/why`, instrument/log runtime state to split the problem space in half on each pass, and confirm the surviving mechanism before writing the fix. If two fixes sharing a premise fail the same gate, write that premise down and test it directly (`attack-the-premise`).
3. **Write the failing test first (`/tdd`):** When a cheap local unit, component, or integration test path exists, write the focused test asserting intended behavior and confirm it fails for the expected reason before editing production code. Skip creating a brand-new test harness only when setup would be brittle, mock-heavy, or disproportionate—use the closest executable reproduction check instead.
4. **Fix and verify on the same surface:** Apply the minimal root-cause fix and confirm both the regression test and original reproduction pass. When commits are in scope and a local test exists, commit the failing test before the fix commit (`sequence-verifiable-units`); always report the failing-before and passing-after evidence.

### Refactoring
You own the contract: structure changes, behavior does not. If cleanup reveals a bug or missing feature, split it out and ship the structural change first against the pinned contract.
1. **Pin the behavior contract first:** Run `/how`, then write or run a characterization test, snapshot, or equivalence harness that captures current behavior. Typecheck and lint alone are not a behavior pin.
2. **Subtract before you add (`subtract-before-you-add`):** Delete dead code, collapse single-caller wrappers, drop redundant validators, and remove orphan references before introducing the new shape (`laziness-protocol`).
3. **Migrate callers and delete legacy APIs in one wave (`migrate-callers-then-delete-legacy-apis`):** Move in small steps that keep the pin green. When reshaping an internal API, migrate every caller and delete the old API in the same change—no compatibility shims or parallel old/new paths unless an external consumer and exit trigger require one. Spot-check renames across strings, docs, and config.
4. **Prove equivalence and lower reader load (`minimize-reader-load`):** Verify unchanged behavior on the real artifact. If the diff does not measurably reduce reader load (fewer layers, less hidden state, smaller mutable scope), revert it.

### Prototype
When resolving an open design question or an empirical behavioral/timing fork:
1. Invert the normal verification bar: optimize for speed of learning in an isolated `scratch/` directory, separate from production source.
2. When comparing alternatives (`exhaust-the-design-space`), put 2–3 labeled variants behind one switcher.
3. Observe or screenshot each variant on the matching surface, present the evidence and recommendation, and state plainly that the prototype is throwaway before routing the chosen direction to **Feature**.

### Ambitious or unmapped multi-part work (`/figure-it-out`)
When a large migration or multi-part change matches no single narrow playbook:
1. **Frame:** State the falsifiable done predicate (`prove-it-works`), quantified scope, and rigor level before writing code.
2. **Sequence riskiest-unknown-first (`foundational-thinking`):** Build and capture the baseline verification harness before feature edits (`build-the-lever`, so checks read `old value vs new value`).
3. **Run the hypothesis loop:** Execute each unit as an experiment (`VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`—never hide a negative or treat inconclusive as pass) and log every step in a scratch `decision.tsv` ([agent-operations.ARENA.md](agent-operations.ARENA.md), `/show-me-your-work`).
4. **Encode lessons in structure (`/correct`):** For non-trivial repetitive work, build a script, codemod, or verifier (`build-the-lever`). Fix recurring mistake classes structurally (architecture → types → self-explanatory lint/CI check → behavior test) before adding prose rules.

## Architecture, types, and verification discipline

- **Boundary and type discipline (`boundary-discipline` / `type-system-discipline`):** Parse untrusted inputs (`unknown` from network, disk, env, IPC, or LLM output) into precise schemas at system boundaries, trust internal types, and keep core business logic pure. Make illegal states unrepresentable and brand distinct primitive IDs/units. When reading or writing TypeScript, read [code-change.TYPESCRIPT.md](code-change.TYPESCRIPT.md).
- **Deep modules and explicit errors:** Prefer cohesive modules whose interface is materially simpler than the decisions they hide. Avoid pass-through layers, namespace-only `Service`/`Manager`/`Helper`/`Utils` classes, and configuration bags without behavior. Fail with clear errors; any deliberate fallback or degradation path must emit a structured event naming the branch and reason, and record provenance on returned values when downstream logic depends on it. Keep imports at module scope unless lazy loading, an optional dependency, or a documented cycle requires otherwise.
- **Idempotency (`make-operations-idempotent`):** Design commands, migrations, retries, and lifecycle steps so repeated execution converges to the same end state.
- **Test behavior, not implementation (`test-behavior-not-implementation`):** Assert user-observable outcomes so tests fail when behavior breaks and keep passing when only internals change. Never weaken or disable a test merely to make it pass; when intended behavior changes or evidence proves an expectation wrong, update the oracle and preserve coverage for nearby invariants. Compare against existing goldens before regenerating.
- **Comment and suppression hygiene (`/no-comments`):** Preserve existing unrelated comments and public API docstrings. In new or modified code, omit narration, section banners, phase-narrating test comments, and commented-out code; add a comment only for a non-obvious *why*, invariant, or external platform/vendor constraint that code and types cannot express. When a diff-scoped comment or lint/type suppression (`@ts-ignore`, `@ts-expect-error`, `eslint-disable`) masks an internal code surprise, reshape, rename, or retype the code so the invariant is self-evident ([code-change.REVIEW.md](code-change.REVIEW.md)).

For `/architect`, `/blast-radius`, `/interrogate`, `/no-comments`, `bugbot-triage`, or code review work, read [code-change.REVIEW.md](code-change.REVIEW.md). For recurring service failures, request performance, runtime/trace forensics, or `/benchmark-checklist` / `hillclimb` loops, read [code-change.OPERATIONS.md](code-change.OPERATIONS.md). For browser or UI work, read [code-change.FRONTEND.md](code-change.FRONTEND.md) and `frontend-quality` (`frontend-quality` owns task reasoning, composition, reduction, and rendered evidence; this procedure owns the engineering loop).

## Network and sensitive surfaces

Keep secrets in headers or typed secret configuration, never query strings or logs. Sanitize exceptions before logging, replace credential-bearing HTTP failures with a safe public exception, and ensure telemetry also redacts retained exception context. Use `procedures/log-redaction.md` for implementation details, and invoke the matching scaffold or `harden` specialist when an affected sensitive boundary presents material risk.

## Commits, PRs, babysitting, and shipping

Use the global completion contract. Combine rendered evidence from `frontend-quality` and deeper owner walkthroughs from `explain-change` when applicable. Pushing, opening, or merging a PR remains governed by the global publication and external-action approval boundary.

- **Commits and PR descriptions (`opening-a-pr`):** Order commits into small, landable, verifiable units (`type(scope): subject`, Conventional Commits, no trailing period; commit body does not restate the subject). Prefer narrow stacked PRs over a single large PR, and run `/unslop` + `/no-comments` over the diff before review. Write a one-minute briefing PR body (under ~40 lines) using `##` headings in order (dropping empty optional sections):
  - `## Why`: 1–3 short sentences on the user goal, problem, and approach.
  - `## What changed`: 1–3 short bullets naming only the symbols/paths that carry the change (both sides of a rename).
  - `## Scope`: 1–3 items on what is covered and what is deliberately left out.
  - `## Tradeoffs`: rejected alternatives a reviewer would ask about (omit if none).
  - `## Blast Radius`: 1–2 sentences on what is touched and why it is safe or risky.
  - `## Verification`: 1–3 bullets with real executed commands/surfaces and outcomes (for perf: `before → after` with units; link bulky arena/swarm artifacts rather than inlining tables).
- **Babysitting PRs (`babysit`):** When asked to get a PR or stack green, declare the mode (`drive`, `background`, `threads-only`, or `check`) and work only the lowest unmerged PR (the merge frontier) in order: conflicts → review threads → CI. Batch fixes into one push wave. Classify CI failures before retrying (at most one fresh build for a flake; check `git merge-base --is-ancestor` for stale base). Triage automated review bots skeptically against the code ([code-change.REVIEW.md](code-change.REVIEW.md)).
- **Shipping stacks (`shipping`):** Green CI and bot approvals are not verdicts. Before landing a stack bottom-up, require an independent non-author verification check (`PASS` / `PASS+NOTES`) on the real surface, compare `git patch-id` at the verified SHA against the current head after any rebase, and land only the contiguous verified run rooted at the bottom.
