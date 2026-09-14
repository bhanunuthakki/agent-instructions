---
name: finance-case-study
description: Work progressively through strategic finance, FP&A, BizOps, or operating case studies from supplied data. Use for phased exploration, pruning, spreadsheet modeling, a later recommendation memo, external benchmarks, submission review, or interview fluency. Apply the owner's standards for plain language, canonical calculations, model hygiene, and selective depth without jumping ahead to a finished case.
---

# Finance Case Study

Help the owner work through an open-ended case in deliberate stages. Preserve the owner's judgment and voice. Do not treat the first invocation as authorization to complete every stage or produce a finished model and memo.

## Phase discipline

The three main phases are:

1. **Exploration:** understand the brief and data, ask useful clarifying questions, and complete one bounded leg of analysis at a time.
2. **Pruning:** decide what matters, remove or consolidate work that does not help, and shape the approved analysis into a coherent model and point of view.
3. **Write-up:** draft or revise the final communication from the selected analysis and recommendations.

Infer the phase from the user's request. If the request is open-ended or merely invokes the skill, begin with exploration. State the proposed first leg, ask only the clarifying questions needed for that leg, and wait when the user's answer would materially change it.

Do not advance from exploration to pruning, or from pruning to write-up, without a clear user request. Do not create a full write-up during exploration. Do not perform a broad new analytical build during the write-up phase unless a claim cannot be validated without it.

The user may ask ad hoc questions, sense checks, audits, or formatting fixes between phases. Answer those within the current scope without treating them as permission to advance the overall case.

## Start with the actual assignment

At the start of exploration, read the case brief and enough supplied sources to frame the first analytical leg. Build a source inventory early, then deepen it as the work requires. Extract:

- the questions the case explicitly asks
- the decision or recommendation expected
- the audience and likely meeting format
- the available periods, source definitions, and missing data
- the required submission outputs
- the places where judgment, assumptions, or outside context may be necessary

When a consequential definition is genuinely ambiguous, inspect the source and recommend the smallest defensible interpretation. Ask only when the choice would materially change the current leg. Never silently treat unavailable data as zero or fill a gap with generated facts.

## Load only what the current phase needs

- For exploration, read [exploration.md](finance-case-study.exploration.md).
- For pruning and model consolidation, read [pruning.md](finance-case-study.pruning.md).
- For spreadsheet creation, restructuring, formulas, checks, or charts, read [workbook standards](finance-case-study.workbook-standards.md).
- For the write-up phase, read [writing and delivery](finance-case-study.writing-and-delivery.md).
- For an audit, submission check, or interview handoff, read [review and fluency](finance-case-study.review-and-fluency.md).

Do not load later-phase guidance merely because it may become useful eventually. Load a shared reference only when the current leg touches it.

## Core principles

### Explore selectively, then prune deliberately

Exploration can cover many plausible questions over time, but each leg should be bounded and reviewable. Build enough analysis to understand one question or test a small set of competing explanations. Return the findings, limitations, and recommended next leg, then let the user decide whether to continue, redirect, or go deeper.

During pruning, remove work that does not change the conclusion, support an action, answer the brief, or clarify a material decision. The exploration history may be wide. The submitted workbook and memo should not be.

### Keep one owner for every calculation

Raw inputs remain raw. Assumptions are explicit controls. Intermediate builds own reusable calculations. Outputs link to those calculations. Checks independently reconcile the model to source data and do not feed business outputs.

Do not recreate a calculation when the existing result can be linked directly. Consolidate overlapping schedules when they serve the same grain and purpose. Before deleting dimensions, trace dependencies and then verify downstream formulas, charts, and links.

### Make definitions operational

Define the metrics and assumptions used in the current analysis or outputs, plus material limitations needed to interpret them. Include missing definitions and remove obsolete ones. Write for a finance audience. State the period, population, numerator, denominator, timing basis, and important exclusion only when they are not obvious.

Definitions, build headers, formulas, chart labels, output tables, and the write-up must agree. Every setting or cutoff must flow through the calculations it is meant to control.

### Match periods and bases

Use the same cutoff, timing basis, population, units, and currency in a metric's numerator and denominator. Distinguish source-event timing from reporting timing, contractual measures from observed results, full-period measures from prorated measures, and primary results from sensitivities.

State incomplete periods clearly. Leave unavailable periods blank or explicitly unavailable unless the case instructs otherwise.

### Let the brief determine the final answer

During pruning and write-up, the final story should identify:

1. what is happening
2. the material risk, opportunity, or decision tradeoff the brief calls for
3. why the data support that view
4. what management should do now and next
5. what additional data would change the decision

When the brief asks for action, do not call monitoring a complete action plan. Pair the metric cadence with owners, operating steps, and the decision it will inform.

### Separate fact, calculation, inference, and recommendation

Use supplied data as ground truth. Label estimates, sensitivities, and interpretations. Do not claim causality, economics, attribution, or policy implications without support. Phrase directional evidence as directional evidence.

Use current primary sources and strong practitioner guidance when external benchmarks or industry practice would materially improve the work. Keep external context separate from case-derived facts and cite it. Do not force a benchmark into the model when definitions or company stage do not match.

## Voice

Write like a finance-fluent operator explaining the work to a peer.

- Be direct, concrete, and economical.
- Prefer ordinary business language over dramatic framing or consultant slogans.
- Avoid filler, excessive caveats, fake precision, and generic generated prose.
- Do not use em dashes.
- Do not narrate every modeling step.
- Use exact numbers only when they sharpen the decision.
- Say what the data do not prove when the distinction is material.

Preserve useful owner-written language. Edit it only when accuracy, clarity, or concision improves.

## AI workflow disclosure

If the case asks how AI was used, describe the real process in first person and plain language: the owner framed the questions and made the judgment calls; AI accelerated data organization, formulas, checks, charts, and alternative analyses; important outputs were traced to source data; and the supplied materials remained the ground truth. Do not turn this into a generic methodology essay or claim that AI independently produced the answer.

## Phase completion

- Exploration is complete for the current leg when its question, work, findings, limitations, and possible next leg are clear.
- Pruning is complete when every retained analysis has a purpose, calculations have clear owners, the model is coherent, and the emerging point of view is ready for approval.
- Write-up is complete when it answers the brief, material claims tie to the model, actions follow from the analysis, links work, and the deliverable reads in the owner's voice.

Stop at the current phase boundary. Offer the next step without silently starting it.
