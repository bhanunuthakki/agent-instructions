# Claude Code

@AGENTS.md

Claude-specific context only:

- Canonical workflows live in this instruction repository's `procedures/` directory. `snippets/sync_agent_stubs.py` generates Claude skills, the `/harden` command, and specialist agents from those sources; edit the procedure, not `~/.claude/skills`, `~/.claude/commands`, or `~/.claude/agents`.
- Use the Agent tool for bounded delegation. Fable owns ambiguous architecture and synthesis; Sonnet is the normal execution or audit tier; Haiku is for deterministic extraction. The task contract and quota rules are in the `agent-operations` skill.
- Python code that deliberately calls a subscription-backed model uses the governed wrappers in this instruction repository's `snippets/` directory. Load `llm-ops` for transport, isolation, fallback, schema, and ledger requirements. Do not substitute a metered SDK for a membership-backed route.
- Resolve executable paths before launching them from Python and use UTF-8 explicitly for subprocess text. On Windows, use native PowerShell path validation for filesystem changes. On macOS, use POSIX paths and the repository's documented shell entrypoints.
- On the Windows runner, Drive-synced worktrees are removed with a validated PowerShell `Remove-Item -Force` target; `git worktree remove` is unreliable for those legacy Drive paths. This does not apply to normal local macOS worktrees.
- Headroom is not a default Claude or Codex route. Do not enable or depend on it without checking the current runtime configuration and process-lifecycle constraint.

Project `CLAUDE.md` files should contain only `@./AGENTS.md` plus, when unavoidable, a terse Claude-only gotcha.
