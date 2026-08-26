# Agent Instructions

Shared system instructions, safety contracts, and canonical workflow procedures for
local AI coding pairs (Claude Code, Codex, Gemini, Antigravity).

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
