---
name: external-practice
description: Verify a consequential, drift-sensitive implementation or design choice against current primary sources. Use for current model guidance, LLM evals, retrieval or embeddings, databases and migrations, auth or cryptography, payments, email, deployment, browser APIs, and material library or vendor choices.
---

# External Practice Check

Verify the decision at the real code or configuration seam. This is not a generic best-practices essay.

## Workflow

1. Inspect the affected entrypoint, adapter, manifest or lockfile, configuration, schema or migration, prompt or eval, and deployment definition as applicable.
2. Record only load-bearing choices that are consequential and plausibly sensitive to provider, version, standard, security, or research drift.
3. Assign one owner:
   - build/buy, library, service, or vendor comparison → `tool-selector`;
   - algorithm, protocol, configuration, or domain practice → the owning expert;
   - cross-boundary structure → `architecture-reviewer`.
4. Verify with current official documentation, standards, security advisories, primary research, or maintained benchmarks. Secondary sources may help discovery or triangulation but do not solely support a consequential recommendation.
5. State the applicability conclusion and the remaining uncertainty. A URL list is not a completed check.

Use this inventory:

`area | code/config seam | decision | why drift-sensitive | owner | evidence status`

For each conclusion record source title and URL, publisher, published or updated date when available, access date, applicable product and version, conclusion, and evidence gap. If nothing qualifies, record `none` with the scope rationale.

A cached conclusion expires when the relevant implementation seam, provider or dependency version, or governing standard changes. Otherwise recheck at the cadence justified by that evidence class; do not invent one universal freshness period.
