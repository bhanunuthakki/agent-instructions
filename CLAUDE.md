# Claude Code Instructions

@AGENTS.md

---

The block above (`AGENTS.md`) is the canonical, tool-agnostic rulebook. Everything below is **Claude-Code-specific**: machine paths, subscription-billing wrappers, concrete model IDs, and the native skills/commands/hooks that implement the procedures `AGENTS.md` points to. Gemini never loads this file.

## Native implementations of the AGENTS.md procedures

`AGENTS.md` references procedures by name; on Claude these are real auto-loading skills / commands / hooks (no manual file-reading needed):

| AGENTS.md reference | Claude mechanism |
|---|---|
| Grill-Me | `grill-me` skill (auto-triggers) |
| Definitions | `definitions` skill (auto-triggers) |
| Hardening Fleet | `/harden` command + subagents in `~/.claude/agents/` |
| LLM-Native Engineering | `llm-ops` skill + `model-frontier` reference + `/refresh-frontier` command |
| Building Secure Apps | `scaffold-secrets`, `scaffold-auth`, `scaffold-tenant-schema`, `scaffold-design-system`, `scaffold-deploy` skills |
| Reviewing LLM-written code | `explain-change` skill |
| log-redaction guidance | `log-redaction` skill |
| Pre-Push / credential scan | shared git hooks in `githooks/`, wired per-repo via `core.hooksPath` (by `/sync-agent-stubs`) |

Human-facing map of the whole system (not loaded into context): `C:\Users\Bhanu\.gemini\AGENTS_GUIDE.md`.

## Path Conventions in Messages

**User profile = `bhanu`.** In messages/links/commands to the user, render the **literal resolved path** rooted at `C:\Users\bhanu\...` (Windows) or `/c/Users/bhanu/...` (bash). Never `%USERPROFILE%`, `~`, or `$HOME` — those aren't clickable/pasteable. Use lowercase `bhanu` consistently (Windows is case-insensitive).

## This Machine

- OS: Windows 11. `%USERPROFILE%` = `C:\Users\bhanu`; bash equivalent `/c/Users/Bhanu/`.
- Common project parent: `C:\Users\Bhanu\.gemini\antigravity\scratch\`.
- ffmpeg at `C:\ffmpeg\bin\ffmpeg.exe` (not on PATH; pass `FFMPEG_LOCATION` or `--ffmpeg-location`).
- Claude Code CLI: `C:\Users\Bhanu\AppData\Roaming\npm\claude.CMD` (resolvable as `claude` from PATH-aware lookups; bare-name `subprocess.run(["claude", ...])` fails — see below).
- GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe` (`gh --version` works in any shell).
- Worktrees: remove with PowerShell `Remove-Item -Force`, **not** `git worktree remove/prune` — Drive sync breaks it.

## Concrete Model IDs (single source of truth)

**Primary interactive orchestrator: `claude-fable-5`.** The delegation *logic* — execution-shaped work defaults to a cheaper worker; orchestrator-inline execution is a named exception — is `AGENTS.md` §Session & Agent Model Selection; don't re-derive it here. Claude's spawn **mechanics**: the `Agent` tool with `model: "sonnet"` (workhorse) or `model: "haiku"` (mechanical); `subagent_type: general-purpose` for implementation briefs, `Explore` for read-only search sweeps. Hardening-fleet agents already pin `model: sonnet` in their frontmatter — don't override upward without a demonstrated failure at that tier.

`AGENTS.md` owns the model-selection *logic* (cheapest-sufficient, delegate execution downward, escalate only on failure); this file only names Claude's current classes and IDs so that logic has concrete targets. **The `claude-api` skill is authoritative for current IDs and pricing — defer to it; treat the list below as a convenience cache that goes stale as versions churn (e.g. Sonnet moved 4.x → 5). Verify before pinning.**

- **Haiku-class** — `claude-haiku-4-5` (Haiku 4.5). Cheapest/fastest.
- **Sonnet-class** — `claude-sonnet-5` (Sonnet 5). Workhorse; default for implementation.
- **Opus-class** — `claude-opus-4-8` (Opus 4.8). Heavy general reasoning.
- **Fable-class** — `claude-fable-5` (Fable 5). Its own class and the strongest for complex planning, architecture, spec development, and reviews — the judgment-heavy work the delegation rule tells you to reserve the top of your budget for.

These are not a single cheap→dear axis: pick by the task, per AGENTS.md. The subscription Python wrapper's default is set in `claude_cli.py` (Sonnet-class). Per-repo model pins (e.g. angel-memos) are legitimate project choices and live in that repo's file.

## Calling Claude from Python (subscription billing, not API)

When a Python script invokes Claude, **route through the CLI subprocess wrapper at `C:\Users\Bhanu\.gemini\snippets\claude_cli.py`** so calls bill against the Pro/Max subscription. Do **not** use the `anthropic` SDK or `claude_agent_sdk` — both bill the metered API regardless of CLI auth.

```python
import sys
sys.path.insert(0, r"C:\Users\Bhanu\.gemini\snippets")
from claude_cli import call_claude
response = call_claude("Your prompt here")  # claude-sonnet-5 by default
```

The wrapper handles three Windows gotchas that silently break naive `subprocess.run(["claude", ...])`:
1. Resolves the absolute path to `claude.CMD` via `shutil.which` (PATHEXT isn't applied to bare names by Python subprocess).
2. Forces `encoding="utf-8"` with `errors="replace"` (Windows cp1252 default kills prompts containing `−`/`–`/`—`/arrows or PDF-extraction garbage).
3. Fails loud if `ANTHROPIC_API_KEY` is set — without this guard the CLI silently falls back to API billing.

One-time setup: install Node, `npm i -g @anthropic-ai/claude-code`, `claude auth login`, ensure `ANTHROPIC_API_KEY` is unset. Don't reinvent this — copy `claude_cli.py` or `sys.path.insert` to it.

For an llm-ops purpose pinned to an OpenAI `gpt-*` model, route through `C:\Users\Bhanu\.gemini\snippets\codex_cli.py`. It invokes the managed standalone Codex CLI under `C:\Users\Bhanu\.gemini\.tools`, authenticates from the dedicated `C:\Users\Bhanu\.gemini\.codex-membership` home, and fails if `OPENAI_API_KEY` or `CODEX_API_KEY` is present. This is the ChatGPT-membership path; never substitute the metered OpenAI SDK.

## Headroom Context Compression (Claude CLI sessions only)

Route interactive `claude` through the Headroom proxy to optimize tokens — use the global wrapper `ch` (alias `claude-headroom`) instead of raw `claude`, with `HEADROOM_REQUIRE_RUST_CORE=false` and `ANTHROPIC_BASE_URL=http://127.0.0.1:8787`. This governs **your own CLI sessions only**; it does NOT override a project's in-app LLM transport/billing — e.g. earnings-summary's metered `src/llm/cli.py`, or the subscription `claude_cli.py` wrapper (which requires `ANTHROPIC_API_KEY` unset). Those follow their own config and are not auto-routed through the proxy.
