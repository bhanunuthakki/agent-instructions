# Gemini

@./AGENTS.md

Gemini-specific mechanics:

- If the active runtime does not auto-load a matched skill, load the canonical procedure before acting.
- Use only tool and delegation surfaces exposed by the active runtime. Fall back to serial execution when equivalent; return `HOLD` when a missing capability prevents required evidence.

<!-- BEGIN:triggers -->
Procedure routing is inherited from `AGENTS.md`.
<!-- END:triggers -->
