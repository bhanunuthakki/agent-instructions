# Agent portability catalog — 2026-09-08

## Requested standard

Treat `AGENTS.md` as the canonical project instruction entry point. Runtime-specific files are
thin discovery adapters only. Canonical skills live in a runtime-neutral location and generated or
runtime-specific copies never own policy. This matches the relevant NowStack instruction topology;
the projects also retain a thin Gemini adapter where that runtime needs one.

## Scope

The audit covered the 13 Git projects under `/Applications`, their root and nested rulebooks,
first-party `SKILL.md` files, generated global/runtime artifacts, the shared procedure graph, and
first-party memory files and memory-maintenance code. It excluded virtual environments,
`node_modules`, third-party plugin caches, deployment snapshots, and historical worktrees as
non-canonical or externally owned material.

## Findings and disposition

| Area | Finding | Owner | Disposition |
|---|---|---|---|
| Shared contract | `GLOBAL.md` is provider-neutral; procedures own reusable workflow and runtime wrappers are derived. | `agent-instructions` | Keep |
| Project topology | All 13 projects have canonical `AGENTS.md` rulebooks and thin `CLAUDE.md`/`GEMINI.md` imports; the central sync check passes. | `sync_agent_stubs.py` | Keep and enforce |
| Blog skills | `blog-engine/AGENTS.md` names Codex while describing a cross-runtime skill invocation. | `blog-engine` | Replace with capability-based language |
| Angel LLM entry point | `angel-memos/AGENTS.md` names `claude.py` as the permanent application-LLM boundary; code and UI copy preserve the legacy provider name and route order. | `angel-memos` | Move canonical entry point to a neutral module; keep provider adapters behind it |
| Memory runner | `repo-maintenance` defaults to Codex, duplicates provider-priority configuration, and falls back to a legacy Claude/Gemini Windows memory path. | `repo-maintenance` | Resolve the fleet route and require an explicit memory root |
| Application LLM migrations | `date-suggester` and `earnings-summary` are recorded as migration holds because active routing work is already uncommitted. | owning projects plus `llm_usage_index.json` | Preserve active work; validate through the fleet index before clearing |
| Personal sync skill | `~/.codex/skills/gemini-instruction-artifact-sync` is a stale runtime-named adapter for a cross-runtime job already owned by `source-command-sync-agent-stubs`. | generated/personal runtime state | Retire after canonical sync proves the neutral skill is available |
| Legacy adapter discovery | Active launchers and LLM adapters in Date Suggester, Earnings Summary, Harness, HuntDesk, and Wealthplan still locate shared tooling through the old `.gemini` runtime home. | owning project adapters | Resolve `AGENT_INSTRUCTIONS_HOME`, a sibling canonical checkout, or the script's own repository |
| Memories | No provider-specific text was found in first-party memory data. Matches under dependency packages are third-party implementation files, not project memory. | project memory owners | No content change |
| Legitimate provider specificity | Runtime wrappers, provider transports, model-frontier/reference evidence, and built-in Codex product-management skills name their actual runtime or service. | adapter/reference/product owner | Keep isolated; do not promote into canonical policy |

## Why drift occurred

1. The repositories evolved from a Claude- and Gemini-shaped Windows setup. Several paths and
   module names became durable before `AGENTS.md` and the shared fleet policy became canonical.
2. The 2026-09-04 memory refactor correctly isolated model judgment behind adapters, but replaced
   the Claude default with a Codex default instead of consuming the already-owned fleet route.
3. Existing synchronization tests prove byte equality, wrapper thinness, reference closure, and
   registration. They did not inspect canonical instruction text for provider leakage, so a
   structurally valid rulebook could still encode a runtime name.
4. Tests sometimes asserted the incumbent provider order. That preserved a migration snapshot as
   behavior instead of asserting the portable boundary and its configured route.
5. Runtime-specific adapters and provider-specific references are necessary. Without an explicit
   classification and allowlist, legitimate adapter names and accidental policy coupling looked
   alike during review.

## Prevention plan

- Add a blocking portability check to the central sync command for canonical project rulebooks,
  canonical project skills, and first-party memory instructions.
- Permit provider names only in registered runtime adapters, transport implementations, and dated
  provider/model references, or through a narrow inline exception with a reason.
- Keep application provider priority in `config/llm_routing_policy.json`; projects consume the
  typed resolver rather than creating provider-default environment variables.
- Make `config/llm_usage_index.json` a release gate: `fleet_default` or an explicit governed Judge
  route is conforming; `migration_required` and `migration_hold` remain visible debt.
- Test override behavior and backend substitution. Do not make the incumbent provider name the
  semantic expectation unless the test is specifically for that adapter.
- Continue generating runtime files from canonical sources and reject substantive prose in runtime
  wrappers.

## Completion evidence

The remediation is complete when the central sync check reports no portability findings, affected
project tests pass, generated artifacts converge, and the usage index contains no unjustified
application-route migration state. Historical worktrees and third-party caches remain unchanged.

## Remediation result — 2026-09-09

- All 13 canonical project instruction topologies conform: `AGENTS.md` owns project policy and
  runtime entry files remain thin adapters. Projects without canonical-text findings required no
  rulebook edits, though several active adapters still needed path-resolution cleanup.
- Canonical instruction wording was repaired in `blog-engine` and `angel-memos`. The Angel Memos
  LLM boundary moved to `llm.py`; `claude.py` remains only as a compatibility import alias.
- `angel-memos`, `date-suggester`, `earnings-summary`, and `repo-maintenance` now consume the shared
  fleet subscription resolver. Project-specific provider-default controls were removed. Angel
  Memos' Judge route is separately registered, and Earnings' comparative Judge remains explicitly
  project-owned.
- Provider-branded interactive UI was replaced with active-agent language in Angel Memos and Date
  Suggester. Their launch/call paths now resolve through the fleet-selected adapter.
- Legacy runtime-home discovery was removed from Date Suggester, Earnings Summary, Harness,
  HuntDesk, and Wealthplan; adapters now use `AGENT_INSTRUCTIONS_HOME` or the sibling canonical
  checkout, and Date Suggester's Windows launcher derives its repository from the script location.
  Blog Engine's WordPress credential file default and existing credential moved from a
  runtime-branded home to its project configuration directory.
- The stale personal `gemini-instruction-artifact-sync` skill was retired after the neutral
  `source-command-sync-agent-stubs` artifact was regenerated.
- The central sync command now scans canonical project `AGENTS.md`, `SKILL.md`, and memory Markdown
  for provider leakage. The shared pre-push hook runs that scan narrowly against every project being
  pushed.
- Final central result: `python3 snippets/sync_agent_stubs.py --check` reports
  `no content drift detected`; the fleet usage index validates with no migration holds for ordinary
  application routing.

