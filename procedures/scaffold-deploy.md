---
name: scaffold-deploy
description: Establish a reproducible, secure release and operation baseline for the selected local, private, hosted, or distributed profile. Use for deployment, hosting, containers, CI/CD, distribution, or going live.
---

# Scaffold Deployment and Distribution

Start from the chosen product profile, not a preferred cloud or framework.

1. Inspect the stack, current build, runtime/state boundaries, users, network exposure, availability need, and recovery target.
2. For local/private tools, prefer native service supervision, private networking, signed/reproducible packaging, and truthful operator health. For public hosting, prefer a maintained managed platform when it materially reduces solo-operator burden. Use a raw server, container orchestrator, or IaC only for a named requirement.
3. Verify the selected platform/runtime against current primary documentation before generating configuration.

The resulting baseline must include:

- reproducible dependency-locked build and an artifact that excludes secrets and local state;
- least-privilege runtime identity, explicit configuration/secrets boundary, and no surprise public listener;
- distinct liveness and readiness semantics that prove dependencies required for serving;
- migration ordering, compatibility window, rollback or roll-forward plan, and data-preserving failure behavior;
- release gate using the repository's configured checks, with no invented dependency install or test command;
- structured logs, actionable failure visibility, capacity/cost signals proportional to the profile, and ownership for scheduled jobs;
- backup and a tested restore for durable state, plus export/upgrade behavior for local products;
- release, rollback, restart, and recovery evidence from the actual target environment.

Do not emit a generic Dockerfile, provider manifest, CI workflow, health route, or database add-on before repository and profile inspection. Use `external-practice` for drift-sensitive platform/security choices and finish with the `operations-readiness` hardening gate.
