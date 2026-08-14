# Evidence-governance source register

Accessed 2026-08-13. These sources support the architecture. Routing and adaptation remain local
policy to validate against this system's data. Ordinary audit sample counts must be derived from a
declared tolerable error rate and confidence target for each tier and task class; a fixed percentage
is neither the assurance objective nor a substitute for that derivation.

## Anthropic

- Source: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Publisher/date: Anthropic, 2026-01-09.
- Applies to: coding and research agent evaluation design.
- Conclusion: combine code-based, model-based, and human graders; measure transcripts and end
  states; build representative tasks from real failures; keep capability and regression suites
  distinct. This supports deterministic J0 proof before judge layers and human calibration.
- Gap: it does not define universal J0-J3 thresholds or prove this repository's judge quality.

## OpenAI

- Source: [How evals drive the next chapter in AI for businesses](https://openai.com/index/evals-drive-next-chapter-of-ai/)
- Publisher/date: OpenAI, 2025-11-19.
- Applies to: contextual workflow evaluations and LLM graders.
- Conclusion: specify workflow-specific quality, test real and rare costly edge cases, and have
  domain experts regularly audit automated graders and behavioral logs.
- Gap: it gives no universal sample size, agreement threshold, or automated demotion rule.

- Source: [A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
- Publisher/date: OpenAI, current page accessed 2026-08-13.
- Applies to: agent guardrails and human intervention.
- Conclusion: use layered deterministic and model guardrails; escalate high-risk or irreversible
  actions to humans. This supports the J3 owner gate.

## Standards and primary research

- Source: [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)
- Publisher/date: NIST, current page accessed 2026-08-13.
- Applies to: governance and ongoing testing, evaluation, verification, and validation.
- Conclusion: document objective and repeatable TEVV, use measurement outcomes for monitoring and
  risk response, and integrate feedback and appeal paths. This supports typed receipts and closed
  promotion/demotion feedback.

- Source: [NIST/SEMATECH: Sample Sizes Required](https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm)
- Publisher/date: NIST/SEMATECH e-Handbook of Statistical Methods, current page accessed
  2026-08-13.
- Applies to: choosing ordinary audit sample counts from an explicit confidence target and the
  smallest failure proportion the system is intended to detect.
- Conclusion: sample size follows from the detection objective and confidence requirement. For a
  zero-failure acceptance plan, this system uses the exact binomial relation
  `ceil(log(1 - confidence) / log(1 - tolerable_error_rate))`, then samples sealed root episodes
  without replacement inside each tier-by-task-class stratum.
- Gap: the formula assumes independent sampled episodes and a stable stratum during the evaluation
  window. Mandatory J3, disagreement, override, and policy-change reviews remain census controls and
  are excluded from estimates of ordinary routing error prevalence.

- Source: [JudgeBench: A Benchmark for Evaluating LLM-based Judges](https://openreview.net/pdf?id=G0dksFayVq)
- Publisher/date: ICLR 2025 conference paper.
- Applies to: meta-evaluation of model judges.
- Conclusion: LLM judges have task-dependent vulnerabilities and require their own benchmark and
  calibration. This supports treating each judge as a governed purpose rather than a universal
  reviewer.
- Gap: benchmark results do not transfer directly to local coding or investment-research rubrics.
