# Arena, swarm, autonomous runs, and decision-trail reference

Use this reference under `agent-operations` when running a multi-candidate design/implementation bakeoff (`/arena`), a parallel coverage or race fan-out (`/swarm`), an unattended predicate-driven loop (`autonomous-run`), a multi-PR program (`orchestrate` / `autopilot-stack` / `multi-phase-plan`), or a decision trail (`/show-me-your-work`).

## Arena (`/arena`)

Use Arena when a single attempt at a non-trivial architecture sketch, algorithm, or implementation risks locking in a suboptimal shape:

1. **Frame:** define the exact artifact each candidate must produce and write a 3–6 criterion grading rubric. Withhold the rubric from candidates so they optimize for the task rather than gaming the rubric.
2. **Fan out:** dispatch 2–3 parallel `implementation-worker` or `frontier-synthesizer` candidates in isolated worktrees or scratch directories with the identical prompt. Exceeding three concurrent workers requires explicit user opt-in with the cost tradeoff stated.
3. **Blind cross-judge (advisory):** when comparing nontrivial candidates, optionally pass the sanitized candidate outputs (labeled `A`, `B`, `C` without model/worker identity) and the rubric to an independent worker reviewer. This cross-judge is advisory worker evidence, never a formal `judging.md` Judge seat.
4. **Pick base and graft:** the root inspects all candidate diffs directly, selects the strongest structural base, and grafts specific superior mechanisms, edge-case handling, or tests from the other candidates into the base before running verification and cleaning up disposable candidate worktrees.

## Swarm (`/swarm`)

Use Swarm when partitioning bounded independent slices (such as per-package checks, feature-map verification waves, or adversarial audit angles) or racing alternative hypotheses:

1. **Declare the shape and done predicate:** specify whether workers partition disjoint slices or race on identical briefs, and for a race declare `first pass`, `rank all`, or `best-of` before dispatch. Keep concurrent workers within the one-to-three default unless the user explicitly authorizes a wider fan-out.
2. **Isolate writes and pin inputs:** give each writing worker exclusive file or worktree ownership (`separate-before-serializing-shared-state`). When workers verify or measure code, pin the exact commit SHA and measurement protocol in every brief.
3. **Drain and synthesize:** aggregate worker findings into one root-verified report rather than pasting raw worker logs.

## Autonomous run and multi-PR orchestration (`autonomous-run` / `orchestrate` / `autopilot-stack`)

When the user authorizes a long-running loop ("run until done", `/goal`) or a multi-PR program:

1. **Define a falsifiable exit predicate first:** state the checkable condition (`tests green`, `repro fixed`, `pixel-diff 0`, `all N slices verified`) before the first iteration. Never relax the predicate to declare completion.
2. **One verifiable unit per iteration (`sequence-verifiable-units`):** make the smallest evidence-justified change, verify against the predicate on the real artifact, commit if it advanced, and revert belt-and-suspenders that did not move the predicate. Log every iteration in `decision.tsv` (`/show-me-your-work`). On a plateau, pivot approach rather than repeating equivalent retries; surface only genuine product/preference decisions, irreversible actions, or true dead ends.
3. **Multi-PR program topology (`orchestrate` / `autopilot-stack` / `multi-phase-plan`):**
   - Take one unit end-to-end through build and verification before fanning out across a queue.
   - Assign **one owner per branch/PR** so no two workers write the same branch; stack a PR on another branch only when it directly depends on that branch's code.
   - Supervise active workers by observable side effects (commits, test runs, `decision.tsv` rows) rather than status text, and replace stalled workers immediately.
   - Require a non-author verification check at the code-ready head SHA (unit + live surface + perf where applicable, re-checked via `git patch-id` after any rebase) before merge or operator handoff (merging and pushing remain governed by the user's explicit authorization scope). On an operator hold or stop, issue an immediate zero-writes order to all active workers.

## Decision trail (`/show-me-your-work`)

For long-running, multi-phase, hillclimb, or unattended tasks where the owner will audit decisions after the fact:

- Maintain a single append-only TSV file (`decision.tsv`) in task-owned scratch storage (governed by `storage-lifecycle` and excluded from public commits unless the user asks to commit the trail).
- Record one single-line row per material decision or iteration with columns: `ts` (ISO-8601), `phase`, `decision`, `why` (plain language, no jargon tags), `evidence` (commit SHA, `file:line`, test command, or artifact path), and `result` (e.g., `tests green`, `reverted`, `pixel-diff 0`, `open`).
