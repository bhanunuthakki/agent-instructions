---
name: source-command-refresh-frontier
description: Re-verify and restamp the canonical model cost and capability frontier from current primary provider sources, then flag purposes for evaluation.
---

# Refresh the model frontier

Update `procedures/model-frontier.REFERENCE.md`, which is canonical. Use current official Anthropic,
OpenAI, and Google documentation for exact model ids, capabilities, context limits, and prices.
Secondary benchmarks may help find candidates but do not replace provider verification.

Recompute the documented blended cost, preserve `(verify)` on unresolved fields, restamp only rows
actually checked, and list every purpose whose incumbent was renamed, repriced, dominated, or
challenged by a new candidate. Do not silently repin: run the registered parity evaluation first.

Then run:

```shell
python snippets/sync_agent_stubs.py --artifacts-only
python snippets/sync_agent_stubs.py --check --artifacts-only
```
