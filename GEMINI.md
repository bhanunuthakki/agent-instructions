# Gemini

@./AGENTS.md

Gemini-specific mechanics:

- If the active runtime does not auto-load a matched skill, load the canonical procedure before acting.
- Use exposed delegation interfaces through `agent-operations`; missing capability that prevents required evidence yields `HOLD`.
- Cross-service session handoffs: When coordinating with Codex or Claude from Gemini/Antigravity without desktop GUI automation, dispatch non-interactively via the repository's membership CLI transports (`snippets/codex_cli.py`, `snippets/claude_cli.py`).

<!-- BEGIN:triggers -->
Procedure routing follows the [canonical catalog](procedures/INDEX.md).
<!-- END:triggers -->
