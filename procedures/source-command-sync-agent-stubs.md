---
name: source-command-sync-agent-stubs
description: Audit and synchronize canonical procedures, generated runtime artifacts, rulebook wrappers, semantic references, and composable shared hooks.
---

# Sync agent stubs

Run the canonical generator. `GLOBAL.md` is the shared contract; this repository’s `AGENTS.md` is local guidance. Procedures are reusable sources; generated runtime artifacts are outputs and are overwritten. Preserve real generated-only additions in their canonical owners before regeneration.

```shell
python snippets/sync_agent_stubs.py --check
python snippets/sync_agent_stubs.py
python snippets/sync_agent_stubs.py --check
```

The check audits every visible scratch project, thin runtime wrappers, command/skill/fleet identity,
guide and Gemini inventories, semantic references, and effective shared hooks. A project-local
`.githooks` directory is composed by the shared hooks; it never replaces credential scanning.

Report changed projects and every residual drift line. For a missing project rulebook, inspect the
repository before authoring purpose, entrypoint, verification, state/secret boundaries, vocabulary,
and high-risk constraints. Root runtime wrappers remain hand-authored.
