---
name: linear-pr-sync
description: Synchronize an existing Linear issue with branch and pull-request progress. Use when starting issue work, opening or readying a PR, reporting a material blocker, merging or closing a PR, reconciling stale Linear states, or when asked to update Linear from Git or GitHub evidence.
---

# Linear PR Sync

Keep Linear aligned with verified repository state without producing a comment stream for every commit. Prefer an existing issue; create one only when the user explicitly asks.

## Authority and issue resolution

- Treat Linear changes as external writes. Proceed only when the current request or a durable repository rule authorizes the update.
- Resolve the issue in this order: explicit identifier from the user, exact key in the branch name, exact key in the PR title/body, then an existing linked issue. Accept keys matching `[A-Z][A-Z0-9]+-[0-9]+`.
- Read the issue before writing. Never select an issue by keyword similarity alone. If zero or multiple keys remain, stop and report the ambiguity.
- Do not change priority, assignee, labels, project, milestone, cycle, estimate, or dates unless the user asks or an established project rule requires it.

## Evidence pass

1. Inspect the current branch, worktree status, scoped diff, and relevant repository instructions.
2. Read the PR state, draft/ready status, merge state, review state, required checks, and URL. If no PR exists, distinguish active branch work from an abandoned branch rather than guessing.
3. Read the Linear issue, team statuses, existing links, and recent comments.
4. Summarize the user-visible scope, validation actually run, material blockers, and remaining acceptance gaps. Do not paste logs or expose credentials.

## State contract

Apply only a transition supported by current evidence:

| Repository evidence | Linear state |
|---|---|
| Work has begun on a cleanly mapped branch | Move `Backlog` or `Todo` to `In Progress` |
| Draft PR exists | Keep or move to `In Progress`; attach the PR |
| PR is ready for review | Move to `In Review`; attach the PR |
| Material blocker prevents progress | Keep the current active state and add one blocker update |
| PR merged and required checks plus acceptance evidence are complete | Move to `Done` and record the merge |
| PR merged but required proof is missing or failing | Keep `In Review` and state the exact evidence gap |
| PR closed without merge | Never cancel automatically; report the closure and leave ownership/status for a human decision |

Use the team's equivalent status names when its workflow differs. Never mark `Done` from a local commit, an open PR, a draft, unknown required checks, or green checks that do not cover the issue's acceptance criteria.

## Minimal update

- Add the PR as a Linear link when it is not already attached.
- Change state only when the desired state differs from the current state.
- Comment only for a meaningful phase transition, a material blocker, or merge completion. Do not comment for every push, review refresh, or unchanged reconciliation run.
- Keep the update concise: PR link, phase, shipped scope, strongest validation, blocker or remaining gap.
- Read existing comments first. Reuse or update an existing sync comment for the same PR when supported; otherwise skip an unchanged duplicate.
- Re-read the issue after writing and verify the state, link, and comment outcome.

## Reconciliation mode

For a scheduled or manual sweep, enumerate open/recently merged PRs with exact Linear keys, compare their evidence to issue state, and emit a compact drift report. Auto-correct only deterministic link/state mismatches permitted by the state contract. Never create issues, infer mappings, change planning fields, or close work during reconciliation.

## Handoff

Report the issue identifier and link, before/after state, PR link status, comment action, evidence used, and any skipped update with its reason. Authentication or connector failure stops external writes immediately.
