---
name: source-command-refresh-frontier
description: Re-verify and restamp the canonical model cost and capability frontier from current primary sources and measurements, then flag purposes for evaluation.
---

# Refresh the model frontier

Update `procedures/model-frontier.REFERENCE.md`, the dated shared reference.

For each hosted candidate actually under consideration, use that provider's current official documentation for the exact model identifier, capabilities, availability, context limits, and prices. For an open-weight candidate, use the publisher's canonical model card/license and the selected runtime's official documentation, then measure the actual runtime/model/quantization/hardware tuple when performance or economics affects the decision. Secondary benchmarks may help find candidates but do not replace primary verification or local measurement.

Recompute the documented hosted-cost heuristic using its declared weighting. For open-weight rows, record quality evidence separately from throughput, tail latency, hardware availability, energy or hosting cost, amortized hardware where material, and operational failure behavior. Preserve `(verify)` on unresolved fields, restamp only rows actually checked, and list every purpose whose incumbent was renamed, repriced, dominated, or challenged. When provider documentation changes materially, also check and synchronize `procedures/context-engineering.REFERENCE.md` and note any deprecated or repriced IDs found in registered projects.

Do not silently repin voluntary upgrades or downgrades of active incumbents; run the registered purpose-specific parity evaluation first, as an exploration smoke result cannot authorize a production promotion or blocking-Judge qualification.

Handle **forced provider retirements** (models deprecated, shut down, or within 30 days of an official auto-route or shutdown) in every refresh pass:
- Remove deprecated or shut-down model IDs from the active table in `procedures/model-frontier.REFERENCE.md` into a retired note naming the official replacement and cutoff date.
- For registered projects (`config/llm_usage_index.json`), prepare an isolated retirement diff/branch for non-incumbent fallback, adapter, and active-candidate constants (excluding retired IDs from active candidate nomination while preserving historical ledger/replay lookups).
- Escalate any affected active incumbent or Judge pin as a P0 owner action with its cutoff date.

Then run:

```shell
python3 snippets/sync_agent_stubs.py --artifacts-only
python3 snippets/sync_agent_stubs.py --check --artifacts-only
```
