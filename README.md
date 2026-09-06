# Agent Instructions

Shared, provider-neutral system instructions, safety contracts, and canonical
workflow procedures for local AI coding pairs.

This is a reusable public ruleset. It contains no machine migration plans,
launchd files, MCP topology, credentials, or runtime evidence. Those artifacts
belong in a private machine configuration repository and are intentionally
ignored here.

`snippets/mcp_registry.example.json` documents the public registry schema. Copy
it to the ignored `snippets/mcp_registry.json` and configure local commands and
endpoints outside Git.

## What this is

A lightweight, always-loaded contract that defines cross-project invariants, tool-agnostic
safety boundaries, and progressive execution procedures.

- **Context hierarchy**: Project rulebooks layer beneath this contract; detailed workflows
  live in `procedures/` and load only when triggered.
- **Safety boundaries**: Strict rules prohibiting credential exposure, unredacted logging,
  destructive mutations without approval, and untrusted data injection.
- **Deterministic verification first**: Code changes require deterministic proof, strong
  type bounds, regression tests, and repository-appropriate verification before completion.
- **Progressive procedures (`procedures/`)**: Reusable workflows for code changes, evidence
  governance (J0–J3 evaluation tiers), prompt engineering, and hardening audits.

## Layout

- `GLOBAL.md`: The canonical cross-project contract, generated into each runtime’s global rules.
- `AGENTS.md`: This repository’s local purpose, improvement mandate, authorities, and checks.
- `CLAUDE.md` / `GEMINI.md`: Local imports plus runtime mechanics. Global generation strips the local import.
- `procedures/INDEX.md`: The fallback route catalog when native skill discovery is unavailable.
- `procedures/`: Markdown procedure definitions for specific engineering workflows.
- `snippets/`: Sync scripts and governance tools that maintain consistency across tools.

## Runtime installation and relocation

Run `python snippets/sync_agent_stubs.py` from the source checkout to regenerate the
runtime adapters. The global destinations remain `~/.codex/AGENTS.md`,
`~/.claude/CLAUDE.md`, and `~/.gemini/GEMINI.md`; local project wrappers import only
their own `AGENTS.md`. Generated global references point to absolute paths in this
checkout, and sync checks their recursive Markdown reference closure. After moving
the checkout, regenerate before using the moved source.

Keep the source checkout outside runtime configuration directories. A legacy source
checkout directly in `~/.gemini` collides with Gemini's global destination: sync now
stops before writing anything. Preserve local changes and private state, move that
checkout to a separate project directory, and rerun sync from the moved checkout.
No remote machine is migrated automatically. Direct readers and runtimes without
native discovery should load `GLOBAL.md`, the applicable local `AGENTS.md`, and
`procedures/INDEX.md`; the catalog selects further procedures. The
`machine-operations` skill owns host-sensitive paths and the Mac Linear/OpenRouter
credential-loading rules, while credentials themselves remain outside Git.

## Procedure-routing check

Run the small offline discriminability corpus against Sol with:

```shell
python snippets/procedure_routing_eval.py
```

The report is written to `.tmp/procedure_routing_eval.json`. It measures whether the shared
contract plus fallback catalog distinguish procedure boundaries; it does not claim that live runtimes invoked every
required procedure.

## Private operational state

This public repository contains governance policy templates, schemas, rubrics, and synthetic tests.
The tracked hardening evaluation policy is always unratified. Live Judge ledgers, policy
ratification, qualification receipts, and raw capability-evaluation outputs live under the ignored
`.private-state/` directory. Set `AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT` to an absolute path to keep
that state elsewhere.

Before updating a checkout that still tracks the legacy `governance/` files, run the migration tool
from an updated copy and point it at the old checkout:

```shell
python snippets/migrate_private_state.py \
  --source-root /path/to/old/agent-instructions \
  --state-root /absolute/path/to/private-agent-state
```

The migration copies only the known governance state, including the ratified policy snapshot,
verifies every copied file, never deletes the source, and refuses to overwrite a different
destination. Configure the same state root, run
`python snippets/sync_agent_stubs.py`, and only then update the old checkout.
