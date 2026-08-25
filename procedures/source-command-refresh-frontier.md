---
name: source-command-refresh-frontier
description: Re-verify and restamp the canonical model cost and capability frontier from current primary sources and measurements, then flag purposes for evaluation.
---

# Refresh the model frontier

Update `procedures/model-frontier.REFERENCE.md`, the dated shared reference.

For each hosted candidate actually under consideration, use that provider's current official documentation for the exact model identifier, capabilities, availability, context limits, and prices. For an open-weight candidate, use the publisher's canonical model card/license and the selected runtime's official documentation, then measure the actual runtime/model/quantization/hardware tuple when performance or economics affects the decision. Secondary benchmarks may help find candidates but do not replace primary verification or local measurement.

Recompute the documented hosted-cost heuristic using its declared weighting. For open-weight rows, record quality evidence separately from throughput, tail latency, hardware availability, energy or hosting cost, amortized hardware where material, and operational failure behavior. Preserve `(verify)` on unresolved fields, restamp only rows actually checked, and list every purpose whose incumbent was renamed, repriced, dominated, or challenged.

Do not silently repin. Run the registered purpose-specific parity evaluation first; an exploration smoke result cannot authorize a production promotion or blocking-Judge qualification.

Then run:

```shell
python3 snippets/sync_agent_stubs.py --artifacts-only
python3 snippets/sync_agent_stubs.py --check --artifacts-only
```
