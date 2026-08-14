# Judge calibration and sampling

## Separate routing, execution, and outcomes

Audit three questions independently:

1. Did the router select at least the required tier?
2. Did the tier run with the required proof, Judges, verdict handling, and owner gate?
3. Did later evidence reveal a material or critical miss?

A well-executed under-tier review remains a routing failure. Correct routing with missing proof is
an execution failure. Later outcomes never rewrite the original receipt.

## Mandatory controls are not statistical samples

Review 100% of J3 tasks, disagreements, owner overrides, and policy changes. These are Mandatory
Control Reviews selected because of known risk. Keep them out of ordinary prevalence estimates;
mixing targeted cases into an unbiased sample creates selection bias.

## Ordinary statistical sampling

Do not assign permanent audit percentages. For each `tier x task_class` stratum, the owner first
ratifies a Tolerable Error Rate and confidence objective. Derive the Statistical Sample Target. If
zero failures are observed, the one-sided target is:

`n = ceil(log(1 - confidence) / log(1 - tolerable_error_rate))`

At 95% confidence, detecting a true 10%, 5%, or 2% failure rate requires 29, 59, or 149 independent
audits respectively. The Sampling Fraction is the target divided by available eligible volume and
therefore changes with volume. If the available population is smaller, audit the population and
report `INSUFFICIENT_EVIDENCE`; never weaken the claim to fit a budget.

Select exactly the derived count without replacement by ranking centrally generated, sealed root
episode IDs against the immutable policy hash. Retries share their root episode and count once.
Coding and research are separate inferential strata. Record the one-group J1 and two-group J2 sides
of the routing boundary as analysis attributes; do not force their inclusion or double-count them as
independent samples unless a future policy defines a separate weighted design.

Until targets are owner-ratified, ordinary receipts remain `shadow_pending_parameters` and no
sampling percentage or confidence claim is emitted.

Receipt sampling estimates correctness only among recorded episodes. It cannot detect substantive
work for which no receipt exists. Invocation coverage requires an independent Task Population Frame
such as governed Git/PR work anchors for coding and an output/session registry for research. Sample
that frame and treat a missing receipt as `routing_miss`. Until that frame exists, report invocation
coverage as unproven and do not activate repository blocking.

The append-only ledger drives adaptation. Any completed routing, execution, material, or critical
miss—or an owner overturn—recommends review of a one-tier promotion. A one-tier demotion is eligible
only after both coding and research meet their own zero-failure targets for the tier under review.
Other tiers and Mandatory Control Reviews do not count toward those targets. The owner decides;
neither recommendation changes policy automatically.

## Audit schema

The auditor must differ from the original Judges and use an independently issued audit-session ID
and context. Record rubric version, evidence references, finding, reason, routing correctness,
execution correctness, and completion time. Findings are `none`, `routing_miss`, `execution_miss`,
`material_miss`, or `critical_miss`. Missing schema fields leave a selected audit due.

## Representative judge calibration

Every Judge purpose and rubric must exist in the immutable Judge registry. Each purpose covers
normal, empty, long-context, malformed, adversarial, degraded, and
conflicting-evidence cases. Pairwise comparisons are blind to author/provider and run in both slot
orders. Human agreement below the owner-ratified threshold halts that Judge purpose; adding more of
the same uncalibrated Judge is not evidence.

Coding facets: contract correctness, regression detection, scope preservation, architecture,
security, and validation adequacy. Research facets: claim/evidence coverage, primary-source
quality, freshness, conflict handling, arithmetic, uncertainty, and decision relevance.

Track calls, tokens, latency, disagreement, and owner minutes separately from statistical
assurance. Budget exhaustion rolls work forward or reports insufficient evidence; it never
manufactures confidence, silently de-tiers work, or teaches a Judge from its own unreviewed output.
