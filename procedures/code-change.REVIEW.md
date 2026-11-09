# Code review and architecture reference

Use this reference for consequential refactors, architecture design (`/architect`), blast-radius verification (`/blast-radius`), adversarial review (`/interrogate`), comment/suppression hygiene (`/no-comments`), automated review triage (`bugbot-triage`), or code review.

## Architect sketch and design red flags (`/architect`)

Before writing implementation logic that crosses a module or function boundary or locks in a non-trivial data shape:

1. **Ground:** establish how the surrounding subsystem works (`code-archaeology` `/how`, plus `/why` when redefining ownership or layering). Skip only for genuinely greenfield modules.
2. **Sketch:** write the domain types, function signatures, and module boundaries with `not implemented` bodies and brief pseudocode. For consequential or open designs, explore at least two structurally distinct candidates (`agent-operations` `/arena`) before synthesizing a base design.
3. **Screen every candidate against the 9 design red flags (`design-red-flags`):**
   - **Shallow module:** public interface is nearly as complex as the behavior it hides, or callers must coordinate multiple methods to complete one operation.
   - **Information leakage:** two modules share unencapsulated knowledge of a file format, wire shape, SQL schema, or ordering invariant; if they repeatedly change together, move the shared knowledge behind one owner.
   - **Temporal decomposition:** module boundaries mirror execution order (`read → parse → process → write`) while scattering knowledge of the same data structure across steps.
   - **Pass-through layer:** methods forward arguments or variables unchanged through layers that do not transform or own them.
   - **Special-general mixture:** a general mechanism is polluted with caller-specific `if` branches or configuration flags instead of offering a clean general-purpose primitive.
   - **Conjoined methods:** a reader cannot understand one method without reading another method line by line.
   - **Unclear nominal types:** raw primitives (`string`, `number`, `boolean`) or structurally identical bags are passed where branded types or discriminated unions would make invalid calls fail to compile.
   - **Comment-dependent interface:** a caller must read a docstring or implementation body to learn required call ordering, locking, idempotency, or error behavior.
   - **Local-agent hazard:** an agent that opens only one file, copies the nearest example, and takes the shortest compiling path would introduce a bug across the repository.
4. **Implement against the sketch:** replace `not implemented` bodies with logic. Treat signature or parameter deviations from the sketch as signal to surface, not friction to absorb silently.
5. **Scrap when the architecture is wrong:** if implementation produces a recurring pattern of friction (`>= 2` workarounds of the same shape, repeated special-case branches for unrelated edge cases, escape-hatch casts/optional fields always set in practice, or unexpected locks on supposedly unshared state), throw the sketch out and redesign from first principles rather than bolting on patches.

## Blast-radius proof (`/blast-radius`)

When evaluating what a change could break beyond its diff:

1. **Trace where symbol search stops:** inspect pinned library/dependency source, lifecycle/microtask/teardown ordering, serialization/wire formats, database columns, feature flags, and cross-process consumers three hops downstream.
2. **Prove the load-bearing safety fact:** identify the one or two facts the change's safety depends on and push each as far down this certainty ladder as practical:
   1. *Assertion only* (worthless on its own).
   2. *Source citation* (exact `file:line` in repository or dependency source).
   3. *Step-by-step trace* showing the failure state is unreachable.
   4. *Executed script or test* that imports the real code and fails loudly if the assumption is false.
   5. *Live reproduction* in the running application.
3. **Report in five sections:**
   - **What it does:** what changed, including non-obvious side effects.
   - **The one fact it's safe because of:** state the safety invariant, the certainty step reached, and the proof output (or mark `unproven`).
   - **Risks:** each confirmed risk with `file:line`, failure mechanism, likelihood, impact, and how to check.
   - **Cleared:** hypotheses checked and ruled out with `file:line` citations.
   - **Before you merge:** the cheapest executable test or reproduction script that guards the real risk.

## Adversarial review (`/interrogate`)

When stress-testing a diff or contested design, dispatch independent worker reviewers (`agent-operations`; these are execution workers supplying evidence, never formal `judging.md` Judge seats—use diverse model families when available) briefed to break the change with a concrete input, concurrency interleaving, or reproduction script:

- Findings proven by an execution run or deterministic reproduction are reported as **confirmed defects**.
- Plausible findings that cannot be executed locally (such as external service races, authz policy gaps, or unmockable production failure paths) are retained as **risks** with the missing proof named—never silently dropped and never reported as confirmed defects.

## Comment and suppression hygiene (`/no-comments`)

Scope strictly to the active diff unless the user explicitly invokes `/no-comments` on a wider target. Never strip existing unrelated comments outside the authorized scope.

- **Allowed comments:** legal/license headers, public API contract docstrings, issue/RFC links for constraints code cannot express, and non-obvious behavior forced by an external dependency, platform, vendor, or protocol (if an external claim cannot be verified against upstream docs/source, retain it verbatim and flag `REVIEW`).
- **Delete in-diff noise:** narration of what the next line does, section banners, commented-out code, and phase-narrating test comments (use assertion messages instead).
- **Reshape internal surprises (`MUST KILL`):** when a diff-scoped comment apologizes for a surprise in our own code, or a lint/type suppression (`@ts-ignore`, `@ts-expect-error`, `eslint-disable`) disables a real correctness or safety check, refactor, rename, or retype the symbol in scope so the comment or suppression is unnecessary. Report out-of-diff discoveries briefly without mutating unrelated files.

## Automated review triage (`bugbot-triage`)

When triaging automated PR review bots or security review comments:

- **Verify skeptically against the current tip:** check whether a later commit on the branch already fixed the claim, and run any contract test on the tip empirically before classifying a drift claim.
- **Fix real bugs red-first in the owning PR:** land a failing-then-passing test in the lowest PR that owns the code rather than patching at the stack tip.
- **Never widen deliberately narrow error guards blindly:** when a fallback is gated on a specific condition (such as `ENOENT` for a missing binary), do not widen it into a catch-all retry that masks real runtime, auth, or network errors.
- **Never auto-dismiss high-risk categories:** always evaluate and escalate security, privacy, authz, billing, data-retention, migration, idempotency, concurrency, and manual browser-primitive reimplementation findings (such as custom JS sticky/scroll/hit-testing). Never churn code merely to quiet a bot; dismiss proven false positives with concrete disproof on the thread.

## Additional review smells

- Defensive defaults, broad exception catches, or compatibility shims that can absorb unrelated defects.
- A discriminator that never varies in real inputs; sentinels such as `unknown` comparing equal and licensing a false conclusion.
- Fixtures that reconstruct a schema by hand and silently drift from migrations.
- Network test doubles that can fall through to a live service.
- A successful file or database write that is not followed by integrity or round-trip verification where corruption would be silent.
