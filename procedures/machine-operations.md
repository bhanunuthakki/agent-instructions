---
name: machine-operations
description: Resolve this machine's approved credential source and client before OpenRouter or Linear operations, or the live host authority before cross-machine work. Does not authorize spend, sending, publication, or production mutation.
---

# Machine operations

Use this narrow adapter before an OpenRouter, Linear, credential-resolution, or cross-machine operation. It owns configured source/client selection; the user task and project contracts own permission and product semantics. Never read an entire secret-bearing file into tool output or model context. Load only the named variable inside the process that needs it.

## OpenRouter on this Mac

For a user-requested OpenRouter operation on this Mac, use `OPENROUTER_API_KEY` from `/Applications/agent-instructions/.env` when the active project has no narrower credential. Load only that variable at runtime; never print it, copy it into a project, or commit it. Credential availability does not authorize calls or spend beyond the user's task. If the file is unavailable or invalid, report the configuration blocker without searching for other credentials.

## Linear on this Mac

For a user-requested Linear operation on this Mac, use `LINEAR_API_KEY` from `/Applications/agent-instructions/.env` when the active project has no narrower credential. Load only that variable at runtime; never print it, copy it into a project, or commit it. The canonical CLI client is `/Applications/agent-instructions/snippets/linear_cli.py`. If this configured source is unavailable, report the blocker rather than searching unrelated files. Follow the applicable Linear workflow for task scope and mutation authority.

## Host and scheduler resolution

Use the live target's configured network identity. Loopback names the machine running the client, not the remote host. Read the affected project's listener, database, recovery, and scheduler owners before cross-machine work; no remembered hostname or sibling checkout becomes a fallback authority. Resolve services and state read-only first. Public listeners, production changes, and GUI/resource handoffs require their existing task authority.

For subscription-backed scheduling or a material agent burst, use [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) and the named project schedule registry. This adapter does not duplicate its windows or install jobs. Other machines use their configured adapter; do not infer that the Mac paths above exist or are authorized there.
