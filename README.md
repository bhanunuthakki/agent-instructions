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

- `AGENTS.md`: The canonical, cross-runtime contract.
- `procedures/`: Markdown procedure definitions for specific engineering workflows.
- `snippets/`: Sync scripts and governance tools that maintain consistency across tools.

## Procedure-routing check

Run the small offline discriminability corpus against Sol with:

```shell
python snippets/procedure_routing_eval.py
```

The report is written to `.tmp/procedure_routing_eval.json`. It measures whether the shared
contract distinguishes procedure boundaries; it does not claim that live runtimes invoked every
required procedure.

## Private operational state

This public repository contains governance policy, schemas, rubrics, and synthetic tests. Live
Judge ledgers, hardening qualification receipts, and raw capability-evaluation outputs live under
the ignored `.private-state/` directory. Set `AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT` to an absolute
path to keep that state elsewhere.

Before updating a checkout that still tracks the legacy `governance/` files, run the migration tool
from an updated copy and point it at the old checkout:

```shell
python snippets/migrate_private_state.py \
  --source-root /path/to/old/agent-instructions \
  --state-root /absolute/path/to/private-agent-state
```

The migration copies only the known governance state, verifies every copied file, never deletes the
source, and refuses to overwrite a different destination. Configure the same state root, run
`python snippets/sync_agent_stubs.py`, and only then update the old checkout.
