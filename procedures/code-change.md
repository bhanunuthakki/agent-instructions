---
name: code-change
description: Implement, fix, refactor, or review code with the repository’s tests and conventions. Use for behavior-changing code edits, bug fixes, frontend work, architectural refactors, or pre-push verification.
---

# Code Change

Match the surrounding code and preserve the repository’s public behavior unless the request changes it. Let the codebase supply ordinary conventions; use this procedure for the non-obvious engineering contract.

## Work loop

1. Inspect the affected interface, nearby tests, repository commands, and current diff.
2. State the next behavior in one sentence.
3. Add the smallest test that should fail for that behavior; confirm the failure is relevant. A bug fix needs a regression test.
4. Implement the minimum coherent change, then refactor only where it improves information hiding or removes genuine duplication.
5. Run targeted validation after each behavior. Finish with the repository’s applicable format, lint, typecheck, tests, and build checks in that order.

Do not weaken, disable, or rewrite a failing test merely to make it pass. Exact prose assertions are appropriate only when wording is the contract; prefer structural and semantic checks.

## Design contract

- Use the strongest practical types and validate untrusted payloads into precise schemas at boundaries.
- Fail with clear errors. A deliberate compatibility or degradation path must emit a structured event naming the branch and reason; returned values also record their provenance when downstream logic depends on it.
- Prefer direct, cohesive modules that hide decisions behind a small interface. Avoid pass-through layers, namespace-only service classes, configuration objects without behavior, and helpers extracted only to shorten one caller.
- Keep imports at module scope unless lazy loading, an optional dependency, or a documented cycle requires otherwise.
- Treat LLM output, network payloads, files, and user input as untrusted. Do not classify with substring heuristics when an enum or validated schema expresses the contract.
- Match local comment density, naming, and idiom. Add explanation where the code cannot make a consequential invariant obvious.

For architecture or review work, read [code-change.REVIEW.md](code-change.REVIEW.md). For browser or UI work, read [code-change.FRONTEND.md](code-change.FRONTEND.md) and `frontend-quality`. `frontend-quality` owns task reasoning, composition, reduction, and rendered evidence; this procedure keeps the engineering loop.

## Network and sensitive surfaces

Keep secrets in headers or typed secret configuration, never query strings or logs. Sanitize exceptions before logging and re-raise credential-bearing HTTP failures without the original traceback. Use `procedures/log-redaction.md` for implementation details.

Call out database/schema, authentication/authorization, money, deletion, credential, external-write, and production-migration surfaces in the handoff. Use the matching scaffold or hardening expert when that risk is material.

## Handoff

Lead with the outcome, changed paths, validation run, and any unverified behavior. For a material frontend change, include the task exercised, rendered proof, and any verification gap required by `frontend-quality`. After a substantial LLM-written change, use `explain-change` so the owner can understand the effect and blast radius without reading the diff.
