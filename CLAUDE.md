# Claude Code

@AGENTS.md

Claude-specific context only:

- Canonical workflows live in `C:\Users\Bhanu\.gemini\procedures\`. `sync_agent_stubs.py` generates Claude skills, the `/harden` command, and specialist agents from those sources; edit the procedure, not `~/.claude/skills`, `~/.claude/commands`, or `~/.claude/agents`.
- Use the Agent tool for bounded delegation. Fable owns ambiguous architecture and synthesis; Sonnet is the normal execution or audit tier; Haiku is for deterministic extraction. The task contract and quota rules are in the `agent-operations` skill.
- Python code that deliberately calls a subscription-backed model uses the governed wrappers in `C:\Users\Bhanu\.gemini\snippets\`. Load `llm-ops` for transport, isolation, fallback, schema, and ledger requirements. Do not substitute a metered SDK for a membership-backed route.
- This machine is Windows. Resolve executable paths before launching them from Python, use UTF-8 explicitly for subprocess text, and use native PowerShell path validation for filesystem changes.
- Drive-synced worktrees are removed with a validated PowerShell `Remove-Item -Force` target; `git worktree remove` is unreliable here.
- Headroom is not a default Claude or Codex route. Do not enable or depend on it without checking the current runtime configuration and process-lifecycle constraint.

Project `CLAUDE.md` files should contain only `@./AGENTS.md` plus, when unavoidable, a terse Claude-only gotcha.
