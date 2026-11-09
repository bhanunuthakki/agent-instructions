---
name: verification-engineering
description: Generate or maintain a project-local live verification skill with a feature map (/create-verification-skill, /maintain-verification-skill) or a formal verification / TLA+ statechart model (/create-formal-verification-skill, /maintain-formal-verification-skill, /statechart).
---

# Verification Engineering

Use this procedure when a repository needs a repeatable, scripted way to drive the real application and prove user-observable behavior, or when concurrency, retries, state machines, parsers, or critical invariants need formal model checking beyond unit tests.

All generated verification skills and harnesses live in the **target project repository** (such as its project skill directory or test suite), never in this global instruction repository. Every live verification run must obey the canonical-host invariant in `GLOBAL.md` and [machine-operations](machine-operations.md): drive only supervised transient instances with isolated synthetic fixtures, never mutate or duplicate live persistent state, and terminate all spawned servers, browsers, and child processes before completion.

## Create a project-local live verification skill (`/create-verification-skill`)

1. **Inspect the repository before asking:** determine from source, scripts, and configs:
   - **Surface:** what a user touches (web UI, CLI/TUI, desktop, API, mobile).
   - **Run:** how to start an isolated local instance (commands, ports, environment variables, synthetic seed fixtures).
   - **Drive:** how an agent interacts programmatically (reuse existing Playwright/Cypress, PTY/expect, or HTTP harnesses first; otherwise use headless browser/CDP for web, tmux/PTY for CLI/TUI, or HTTP requests for services).
   - **Observe:** what deterministic evidence is captured (screenshots, DOM/accessibility snapshots, terminal transcripts, response bodies, exit codes, SQLite/DB state).
   - **Isolate:** how concurrent or repeated runs avoid port, profile, or data-directory collisions and stay strictly isolated from live user sessions.
2. **Generate and prove:** write the project-local skill (`verify-<app>/SKILL.md` plus a `features/` map with one file per user-facing capability) addressed to a cold-start agent. Execute at least one end-to-end feature recipe against a transient isolated instance to prove the skill works before declaring completion, then verify all spawned processes and listeners are stopped.

## Maintain a live verification skill (`/maintain-verification-skill`)

Feature maps rot when application behavior changes. During a maintenance pass:

1. **Edit scope:** modify only the verification skill's own directory (`SKILL.md`, `features/`, and its harness scripts). Never edit product code during a verification-maintenance run.
2. **Source wave + live pass:** dispatch read-only `mechanical-worker` checks ([agent-operations](agent-operations.md)) across the feature files to flag source drift and produce concise live recipes, reconcile them into a minimal set of isolated app sessions, and execute the live checks.
3. **Classify mismatches honestly:** if the application no longer does what the feature map states, distinguish **documentation drift** (update the feature map) from a **product regression** (report the bug with reproduction evidence; never paper over a broken feature by weakening the verification map). Report the final outcome as `clean`, `changed`, or `blocked`.

## Create or maintain formal verification (`/create-formal-verification-skill` / `/maintain-formal-verification-skill`)

When bugs in state ordering, retries, leases, distributed coordination, or parsers are high-cost and poorly covered by example-based tests:

1. **Select the target and tool:** pick the highest-risk invariant in the repository and the lightest verifier that answers the question—a model checker (TLA+ / TLC by default for concurrency and state ordering in any language), a code-level verifier or property-based generator for data/input invariants, or a proof assistant when unbounded proof is required.
2. **Keep the model true to code and able to fail:** map every indivisible action in the spec to an exact `file:line` in the repository. Before trusting a passing run, confirm the check catches a known bug or a deliberate mutation of the invariant. Package the spec, config, and runner instructions into a project-local verification skill.
3. **Maintain against code drift (`/maintain-formal-verification-skill`):** after commits touch verified code, update the model or harness to reflect current code and rerun. Classify each property as:
   - `in sync` — code changes did not alter modeled behavior and the check passes;
   - `updated` — model updated to match intentional code changes and the check passes;
   - `bug` — current code violates the invariant (report the counterexample trace; never weaken an invariant or model to make a failing check pass); or
   - `blocked` — tool or environment prevented execution.

## Statechart visualization (`/statechart`)

When a product owner or reviewer needs to inspect state-machine behavior and invariant counterexamples visually rather than reading raw TLA+:

1. Write the TLA+ specification and `INVARIANT` rules in an isolated scratch directory, naming actions as a disjunction in `Next` and adding an explicit stutter step (`UNCHANGED vars`) for valid terminal states so `NoDeadlock` distinguishes terminal completion from unintended deadlocks.
2. Run the model checker and project the reachable states into a Mermaid `stateDiagram-v2` labeled in user-observable domain terms rather than internal variable names. Mark every state that violates an invariant and report the shortest action trace from the initial state to each violation.
3. If a target repository needs automated TLC-to-Mermaid rendering on every change, install the TypeScript statechart runner inside that project's local verification tooling from upstream MIT-licensed [`backnotprop/pstack` (`skills/statechart/scripts/` at commit `7e026ff`)](https://github.com/backnotprop/pstack/tree/7e026ff/skills/statechart/scripts) with its MIT license notice, rather than vendoring Java/TLC artifacts into this global instruction repository.
