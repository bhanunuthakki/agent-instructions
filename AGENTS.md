# Agent-instructions — project rulebook

This repository owns the shared contract, procedures, runtime adapters, and their verification. GLOBAL already applies; this file adds local guidance.

## Purpose and improvement latitude

Make agents useful, decisive, and economical while preserving authority, truth, privacy, and recovery. Improve ownership, discovery, and task outcomes. Remove redundant process or restructure within an authorized instruction task when it resolves a demonstrated problem; fewer words alone do not prove better behavior.

## Source and state ownership

- `GLOBAL.md` owns cross-project invariants and initiative. This `AGENTS.md` owns this repository's work. `CLAUDE.md` and `GEMINI.md` add runtime-only mechanics.
- `procedures/INDEX.md` owns workflow selection and composition. `procedures/<name>.md` owns the reusable workflow; linked references hold conditional detail. Generated skills, commands, and agents are adapters. Edit tracked sources, then regenerate.
- `snippets/sync_agent_stubs.py` owns artifact generation, runtime path resolution, recursive reference closure, project wrappers, and hook composition. Project rulebooks remain owned by their repositories.
- `config/llm_routing_policy.json` and `config/llm_usage_index.json` own fleet application routing and registered entry points; Judge purposes retain explicit separate authorities. Policy changes do not qualify their own outcomes.
- `DEFINITIONS.md`, versioned policy/schema files under `config/`, and their deterministic validators own governed evidence semantics. Raw measurements, ratification, and live ledgers belong in the ignored private state root, never this public repository. `README.md` owns private-state migration and configuration.
- `evals/agent_system/` owns routing and interaction corpora; tests establish structural correctness, while isolated model trials establish only their measured behavioral claims. Preserve unfavorable valid evidence.

## Work and validation

Use `context-engineering` for instructions and `code-change` for generators or validators. Record where removed safety and authority rules survive; do not test preservation through verbatim prose.

Check current generated state before editing: `python3 snippets/sync_agent_stubs.py --check --artifacts-only`. Preserve any genuine generated-only addition in its canonical owner before regeneration.

Test changed generators, loaders, and contracts with a verified Python interpreter and `requirements-test.lock` dependencies. Use a compatible existing environment or an isolated one; missing pytest is unavailable evidence. The complete repository gate is `PYTHON_BIN=<verified-python> sh githooks/pre-push`; it composes the public-boundary check, generated-artifact check, deterministic suites, and applicable private governance checks without pushing.

For canonical changes, regenerate with `python3 snippets/sync_agent_stubs.py --artifacts-only`, then run `python3 snippets/sync_agent_stubs.py --check` and `git diff --check`. A changed skill/catalog inventory also needs `AGENTS_GUIDE.md` regeneration via `snippets.sync_agent_stubs.materialize_guide(False)`; this updates only the derived guide. Use full sync only when project wrapper or hook wiring changes are in scope. The generator has `--check`, `--artifacts-only`, and `--dry-run`; it has no conventional `--help` mode.

A generator/source-layout change also needs the sync and loader regression tests. An authority/routing rewrite needs representative positive initiative and negative boundary cases; follow `evals/agent_system/README.md`. Never present structural tests or an advisory judge score as empirical proof of better production behavior. Do not rewrite historical worktrees en masse.

## Interface

- Profile: none
