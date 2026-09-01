---
description: Audit product maturity with profile-aware, evidence-backed gates. Usage: /harden [l0|l1|l2|l3] [--deep] [--audit <expert>] [--status] [--full]
---

# Hardening

Hardening answers one question: **what is safe and sufficiently complete for this product's next real use?** It does not turn a personal tool into speculative SaaS architecture. Maturity is one axis; deployment, identity, commerce, surface, data, and LLM exposure are separate profile facts.

The orchestrator owns scope, applicability, deduplication, and the final decision. Expert rubrics in `procedures/agents/` own distinct evaluation domains. Audit workers inspect product state and write only the requested report or return structured findings; product mutation requires a separately approved FIX pass.

## Modes

| Invocation | Meaning |
|---|---|
| `/harden` | Assess the next rung using reusable evidence whose fingerprints still match |
| `/harden <rung>` | Assess the named rung |
| `/harden --deep [rung]` | Re-run every applicable gate through the target rung |
| `/harden --audit <expert>` | Run one applicable expert; do not change rung |
| `/harden --status` | Validate state, applicability, evidence freshness, and blockers; no fixes |
| `/harden --full` | Assess through L3; it does not imply multi-tenancy or any other profile |

## Maturity and product profile

- **L0 — decision:** the problem, intended user, value, constraints, and kill criteria justify work.
- **L1 — dependable personal release:** the primary workflow works end to end and durable local state is recoverable.
- **L2 — external beta:** real users or dependent systems can use it safely with bounded operations.
- **L3 — limited commercial release:** the selected distribution and revenue model are supportable, legal, measurable, and reversible.

Record the profile before selecting gates:

| Axis | Allowed values |
|---|---|
| `deployment` | `local`, `distributed-client`, `hosted-single-customer`, `hosted-shared` |
| `identity` | `none`, `single-user`, `multi-user`, `multi-tenant` |
| `commerce` | `personal`, `free`, `paid` |
| `surfaces` | any of `cli`, `api`, `web`, `native` |
| `data` | any of `durable`, `external`, `sensitive` |
| `llm` | `none`, `read-only`, `tool-using` |
| `scheduled_work` | `false`, `true` |

Infer these facts from the repository when evidence is clear. Ask only when a missing fact changes an applicable blocking gate. A paid single-user desktop product can reach L3 without tenancy. A local tool can require operations readiness because it has scheduled jobs or irreplaceable state.

## Active gate matrix

`B` selects blocking requirements introduced or materially tightened at that rung, `A` is advisory, `R` re-verifies the prior blocking contract with the same blocking force, and `—` is not selected by maturity alone. An `R` cell cannot hide newly stricter criteria; use `B` when the target rung adds them. Profile rules below can make a cell `N/A` or elevate a risk-triggered gate.

| Expert | L0 | L1 | L2 | L3 |
|---|:---:|:---:|:---:|:---:|
| idea-evaluator | B | — | — | — |
| product-feature | A | B | R | R |
| architecture-reviewer | A | B | R | R |
| data-foundation | — | B | R | R |
| qa-test-strategy | — | B | R | B |
| ux-design | — | B | R | B |
| frontend-web | — | B | R | B |
| llm-evals-orchestrator | — | B | R | R |
| sec-appsec | — | B | R | R |
| sec-authz | — | B | R | R |
| sec-llm | — | B | R | R |
| api-surface-designer | — | A | B | R |
| legal-compliance | A | A | B | R |
| operations-readiness | — | B | B | R |
| tenant-boundaries | — | — | B | R |
| product-analytics | — | — | A | B |
| docs-support-readiness | — | B | B | R |
| finops-pricing | A | A | A | B |
| payments | — | — | — | B |

### Applicability

- `data-foundation`: durable, external, or sensitive data.
- `ux-design`: a human-facing `web`, `native`, or interactive `cli` surface. A non-interactive library or API is `N/A`.
- `frontend-web`: `web` only. Native and CLI implementation evidence stays with `ux-design` and `qa-test-strategy`.
- `llm-evals-orchestrator` and `sec-llm`: `llm != none`.
- `sec-authz`: `identity != none`, **or** a non-local deployment exposes a `web` or product-owned `api` surface. The latter requires an explicit access-control decision even when the profile currently says `identity: none`; do not silently treat remote mutation or product access as public. A truly local identity-free tool is `N/A`.
- `api-surface-designer`: a product-owned API, webhook, plugin, or MCP surface; consuming a vendor API alone does not qualify.
- `operations-readiness`: durable state, scheduled work, distribution, or hosting. For local products it covers backup, restore, export, upgrades, and scheduler failure rather than cloud ceremony.
- `tenant-boundaries`: `identity == multi-tenant` only.
- `product-analytics`: external beta or commercial release. Direct qualitative learning or privacy-preserving aggregates can satisfy the outcome when event analytics is disproportionate.
- `payments`: `commerce == paid` and the product handles payment, billing, licensing, or entitlement state. It does not require subscriptions.
- `finops-pricing`: advisory for personal/free work; blocking at L3 only when `commerce == paid`.
- `legal-compliance`: risk-triggered by external or sensitive data, external users, distribution, or payment; obligations, not a SaaS checklist, determine scope.
- `docs-support-readiness`: any L1+ product. Personal tools need setup, health, backup, restore, and recovery guidance; external products add user support and incident communication proportional to reach.

Rung-independent mandatory safety findings block advancement regardless of an `A` cell: exposed credentials, likely irreversible data loss without informed confirmation/recovery, known cross-principal data access, unsafe execution of untrusted input, or a legal prohibition on the intended use.

`tool-selector` and `external-integration` are standalone procedures, not maturity gates. Use them when a build/buy choice or a new external capability actually arises.

## Exclusive ownership

Create one primary finding and cross-reference it elsewhere:

- `product-feature`: user-visible behavior, state transitions, non-goals, acceptance, rollout, and kill criteria.
- `architecture-reviewer`: module boundaries, dependency direction, state ownership, and failure shape.
- `data-foundation`: schema, identity/time semantics, migrations, provenance, data quality, retention implementation, backup/export data semantics.
- `qa-test-strategy`: test portfolio, representative scenarios, fixtures, and regression/load execution; CI mechanics belong to operations.
- `ux-design`: task clarity, information architecture, interaction semantics, accessibility, and shared rendered-task judgment.
- `frontend-web`: web implementation, responsiveness, browser states, and rendered performance; reuse UX captures.
- `sec-appsec`: application vulnerabilities, credential material/storage/logging, dependency risk, injection, and abuse ceilings.
- `sec-authz`: identity, sessions, authorization policy, object access, and identity/signing-key lifecycle.
- `tenant-boundaries`: proof that multi-tenant separation holds across storage, cache, jobs, search, files, and compute.
- `sec-llm`: prompt injection, untrusted model output, tool authority, and model-mediated exfiltration.
- `llm-evals-orchestrator`: output quality/contracts, routing evals, and per-call quality/cost/latency/failure evidence.
- `api-surface-designer`: product-owned external contract, compatibility, errors, idempotency, quotas, and webhook contract.
- `legal-compliance`: applicable obligations, rights, consent, disclosure, and retention/deletion requirements.
- `operations-readiness`: build/release mechanics, runtime health, resource telemetry, restore/rollback, incidents, and distribution/update safety.
- `product-analytics`: learning questions, event meaning, activation/retention measures, and experiment interpretation.
- `docs-support-readiness`: setup/recovery/user/API documentation, support intake, escalation, and feedback routing.
- `finops-pricing`: consolidated cost economics, pricing, packaging, and margin.
- `payments`: provider-specific payment lifecycle, reconciliation, refunds/disputes, tax handoff, and entitlement transitions.
- `idea-evaluator`: whether to build at all.

## Evidence and verdicts

Run deterministic checks first. External-practice research is required only for a consequential drift-sensitive seam owned by the selected expert; one scoped research pass may feed several reports. `frontend-quality` owns the shared rendered task/reduction evidence consumed by UX and frontend gates. Browser or renderer evidence is required for material rendered-interface judgments. Do not grade absent harness capability as a product defect.

Each selected gate returns exactly one verdict:

- `PASS`: applicable blocking requirements are evidenced and no finding remains open.
- `BLOCK`: an evidenced product finding prevents the target outcome.
- `ADVISORY`: the advisory review is evidenced and has no unresolved finding in the receipt; proposed future improvements belong in out-of-scope notes, not `open_findings`.
- `HOLD`: required evidence, tool capability, specialist calibration, or valid structured output is unavailable.
- `N/A`: the profile makes the gate irrelevant, with a recorded rationale.

At a `B` or `R` cell, only `PASS` advances. `BLOCK` and `HOLD` stop advancement. At an `A` cell, `ADVISORY` or `PASS` is acceptable; `HOLD` still pauses the overall run because the selected review did not complete, and a mandatory safety finding still blocks. Never silently downgrade a missing worker, malformed report, failed source check, or unavailable renderer into a pass.

`PASS` and `ADVISORY` require an empty `open_findings` list. Any unresolved finding uses `BLOCK` when it prevents the target, otherwise `HOLD` until it is dispositioned or moved to a non-finding future note.

## Run protocol

1. Resolve `target_rung` and the profile JSON. Before spending a worker turn, run `python <harden-package>/runtime/harden_state.py preflight --repo <project> --package-root <harden-package> --runtime <runtime> --profile-json <profile-json> --rung <rung>`. Exit `4` is an evidenced product `BLOCK`, exit `3` is a harness/capability `HOLD`, exit `2` is an operator or package error, and only exit `0` authorizes specialist dispatch. Preflight may run only the exact local subprocesses closed in the applicable mandatory verifier; each command, arguments, timeout, output schema, and exit semantics must match its registered record.
2. Validate any reusable `.harden/state.json` with the same packaged runtime: `python <harden-package>/runtime/harden_state.py validate --repo <project> --package-root <harden-package>`. A malformed or fingerprint-mismatched state is stale evidence, not reusable evidence.
3. Select every matrix row, recording `APPLICABLE` or `N/A` plus one-sentence rationale.
4. Load only selected rubrics. Use `agent-operations` to assign capability roles; model/provider names do not qualify a worker. A blocking specialist must be calibrated for the rubric. Missing capability yields `HOLD`.
5. Audit product files read-only. Commands with possible writes, external effects, test databases, caches, or generated artifacts need an isolated copy or explicit scope. The only ordinary audit write is the named draft report path.
6. Each report records evidence IDs, observed result, reproduction/verification command when safe, severity, owner, confidence, and fix. Severity is: `critical` immediate compromise/loss/prohibition; `high` blocks the target workflow or safety boundary; `medium` material but bounded degradation; `low` improvement; `info` context.
7. Deduplicate by owner, review every `BLOCK`/`HOLD`, apply gate logic, and present approved fix batches. Do not mutate product code until the user authorizes remediation.
8. FIX mode uses an isolated worktree by default. In-place fallback requires explicit approval for that exact repository and change set. Re-run deterministic evidence and the owning gate after a fix.
9. Write state v2 only after reports are complete. Validate it again before claiming advancement.

## State v2

State is a cache index, never proof by itself. `snippets/harden_state.py` is the executable schema and fingerprint authority. A reusable gate receipt is anchored to:

- the exact product worktree excluding hardening reports/state;
- the profile;
- the active matrix contract;
- the selected expert rubric set and shared capability-evaluation registry/receipts.

The state field is `target_rung`: it names the rung being proved, not a previously achieved rung.

Any mismatch invalidates cached `PASS`/`ADVISORY` receipts. A quick run may reuse only a receipt whose four fingerprints match and whose evidence paths still exist with the recorded SHA-256 content hashes. `--deep` ignores reuse. Store unresolved finding IDs, evidence paths plus hashes, capability receipt, applicability rationale, and UTC timestamp. Do not infer omitted fields.

Each capability receipt names one canonical `agent-operations` role, status, identity, purpose, runtime, model identifier, effort, shared evaluation identifier and receipt hash, evaluation and expiry timestamps, exact qualified rubric IDs, and limitations. `PASS`/`ADVISORY` requires an available, unexpired `blocking-specialist` or `frontier-synthesizer` receipt whose ID and hash resolve through `config/harden_capability_registry.json` to a typed receipt under `receipts/`, with its raw outputs and deterministic score under `evidence/<receipt-id>/`. The receipt binds the role/runtime/model/effort and rubrics to a versioned dataset hash, policy hash, rubric hashes, raw-output hash, metric thresholds, measured passing result, and expiry; every duplicated state field must match exactly. The shared registry starts empty until a real evaluation is registered. A project-authored file, provider name, generic worker label, or self-asserted availability is not calibration evidence.

In the public instruction checkout, the registry, receipts, and raw evidence are mutable private
state. They live under `.private-state/config/` and `.private-state/governance/` by default, or
under the absolute `AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT`. The sync generator copies a complete
snapshot into each machine-local hardening package as `config/`, `receipts/`, and `evidence/`;
those generated package files are runtime inputs, not public source artifacts.

Qualification requests include the complete current text of the case's named rubric. Every retained raw case result binds the case ID, full dataset-case hash, blind input hash, rubric ID and hash, rubric-package hash, exact request payload and request hash. The scorer and receipt validator independently reconstruct those bindings and reject missing, duplicate, extra, or mismatched cases before accepting metrics. A receipt cannot qualify a rubric that is absent from the scored raw bindings. Long-context cases must also satisfy the policy's minimum retained character count and structured-section count; a label alone is not coverage.

The v2 verdict vocabulary is `PASS | BLOCK | ADVISORY | HOLD | N/A`; the state and scenario tests reject other values.

## Generative counterparts

- feature contract → `product-feature`
- local-first data baseline → `data-foundation`
- auth → `scaffold-auth`, then `sec-authz`
- multi-tenant storage → `scaffold-tenant-schema`, then `tenant-boundaries`
- deployment/distribution → `scaffold-deploy`, then `operations-readiness`
- design foundation → `scaffold-design-system`, then `ux-design` and rendered evidence
- LLM call → `llm-ops`, then `llm-evals-orchestrator` and `sec-llm`
- secrets → `scaffold-secrets`, then `sec-appsec`

Scaffolds establish contracts after inspecting the repository and chosen profile. They must not inject a framework, provider, tenant column, public deployment, analytics stack, or billing model merely because one is common.
