---
name: linear-pipeline-hygiene
description: Audit and conservatively reconcile Linear pipelines across projects. Use for backlog or pipeline cleanup, stale or contradictory issue states, duplicate or dependency review, missing planning metadata, completed-work hygiene, or scheduled cross-project Linear sweeps.
---

# Linear Pipeline Hygiene

Keep Linear trustworthy across code, research, operations, and content projects without erasing history or turning judgment calls into silent automation.

## Authority and project profile

- Treat every Linear mutation as an external write. Write only when the user or a durable project or scheduled-task rule authorizes the exact class of change.
- Read the team, projects, workflow statuses, issues, relations, and recent updates before proposing or applying cleanup.
- Resolve the project profile before judging drift: scope, completion evidence, planning-field requirements, staleness policy, and terminal-state behavior. Project rules override this generic workflow.
- Use repository and PR evidence through `linear-pr-sync` when a work item maps exactly to code. Do not require a PR for research, operations, content, or other non-code work.
- If no staleness threshold is defined, report age bands instead of declaring work stale. Never infer repositories, issue mappings, dependencies, or duplicates from keyword similarity alone.

## Evidence contract

Classify completion using evidence appropriate to the work:

| Work type | Completion evidence |
|---|---|
| Code change | Exact issue mapping, merged PR, required checks, and acceptance evidence under `linear-pr-sync` |
| Research or analysis | Named deliverable exists, required review or acceptance is recorded, and no stated evidence gap remains |
| Operations or activation | The requested action ran in the intended environment and its health or acceptance evidence is current |
| Content or design | The requested artifact exists and the required review, approval, or publication state is explicit |

Artifact existence, a local commit, an open PR, green checks with uncovered acceptance criteria, or an unverified status comment is not completion.

## Pipeline audit

For every project in scope, inventory:

- counts by workflow state and, when applicable, priority, milestone, assignee, and age;
- active issues with no meaningful update under the project staleness policy;
- `In Progress` work with no current execution evidence;
- `In Review` work whose evidence is complete, blocked, missing, or contradicted;
- candidate duplicates, broken or contradictory dependencies, and parent or child inconsistencies;
- missing project-required planning fields;
- completed work that remains in an active state; and
- terminal issues whose recorded evidence appears incomplete or later contradicted.

Treat `Done`, `Canceled`, `Duplicate`, and archived as distinct outcomes. Do not use deletion or archival as a substitute for correct lifecycle state.

## Mutation boundary

Auto-correct only deterministic drift authorized for the run:

- an exact lifecycle transition whose completion or active-work evidence satisfies the applicable contract;
- an exact missing source link when the issue-to-source mapping is unambiguous; or
- an unchanged duplicate comment or update that can be safely skipped.

Keep these report-only unless the user or project rule explicitly authorizes them: stale-item downgrades, reopening, cancellation, duplicate marking, dependency edits, priority, milestone, project, assignee, labels, cycle, estimate, dates, deletion, and archival. Never create new issues during a cleanup sweep unless the user explicitly asks.

Before writing, read the current issue and existing comments. After writing, re-read it and verify the resulting status, links, and comment state. Authentication, schema, or connector failure stops writes; do not convert partial visibility into a clean bill of health.

## Scheduled sweep

- Bound each run to named teams or projects and a stated lookback or age policy.
- Process independent issues even when one item lacks evidence; place that item in human review.
- Keep comments to meaningful lifecycle transitions, blockers, or completion evidence. Do not emit weekly no-change comments.
- Never broaden a project-specific automation to new teams, repositories, or destructive actions without durable authorization.

## Handoff

Report:

1. scope and project profile used;
2. pipeline counts and findings;
3. each deterministic change with before and after state plus evidence;
4. skipped or ambiguous items requiring human review; and
5. authentication, coverage, or freshness limitations.

If nothing changed, say so while still returning the audit. A clean report means no drift was found in the observed scope, not that unobserved projects or evidence are healthy.
