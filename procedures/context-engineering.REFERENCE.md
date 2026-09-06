# Context-engineering source register

Source register with access dates per entry. Current collaboration guidance checked 2026-09-06; older entries below retain their historical scope.

## Current model applicability — 2026-09-06

Use these findings when diagnosing a runtime or evaluating a migration. They do not add model-specific policy to every task, change the fleet route, or establish cross-model qualification. Keep the shared outcome, authorization, and evidence requirements unchanged. Test any adjustment against the actual host instructions and tool/display behavior; remove it when the observed need disappears.

- **Astra:** [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model), accessed 2026-09-06, now describes GPT-6 Astra. It identifies extra clarification, sensitivity to conflicting skills, detailed prose, and broad verification as behaviors to calibrate. Preserve explicit follow-through and completion boundaries; prune competing process. The URL is mutable and is no longer current evidence for Sol-specific behavior.
- **Sol:** the GPT-5.6 conclusions below are a historical 2026-08-25 observation. Reuse the common contract provisionally; qualify Sol separately on the same scenarios rather than inferring performance from Astra or silently treating a changed URL as fresh Sol evidence.
- **Opus 5:** [Anthropic prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5), accessed 2026-09-06, advises calibrating verbose narration and removing generic repeated checks that amplify proactive verification. Preserve repository-specific acceptance gates.
- **Fable 5.1:** [Anthropic prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), accessed 2026-09-06, describes sparse progress updates and recommends inspecting client display behavior and suppressive instructions first. Also check follow-through and unintended scope expansion when observed. This is a distinct version from the Fable 5 reference below.
- **Gemini/Flash:** [Google prompt strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies), accessed 2026-09-06, recommends direct structure, prominent critical constraints, and explicit task requirements. Preserve these during pruning. Model-specific date/cutoff or grounding examples apply only to their named version and task; do not freeze dates or impose extraction-only behavior on creative/product work.

The shared user experience is purposeful progress and a self-contained result. Corrections for an overly talkative model and a quiet model need not use identical wording. Host rendering, available tools, model version, and effort belong in the evaluation record; effort names do not demonstrate equivalent capability. This register is guidance, not evidence that every named model/runtime has passed the local suite.

## Anthropic

- Source: [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- Publisher/date/access: Anthropic, published 2026-07-24; accessed 2026-08-03.
- Applies to: Claude Opus 5 and Fable 5, Claude Code, CLAUDE.md, skills, tools, and agent harnesses.
- Conclusion: remove duplicated and overly absolute scaffolding; rely more on model judgment; design expressive tool interfaces; use progressive disclosure; keep CLAUDE.md lightweight and focused on repository gotchas; keep skills opinionated but not overconstrained.
- Evidence gap: Anthropic reports no measurable coding-eval loss after removing over 80% of its own prompt for selected models, but that result is not a universal safe-deletion percentage for this repository.

- Source: [What's new in Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/whats-new-opus-5)
- Publisher/access: Anthropic, accessed 2026-08-25.
- Applies to: Claude Opus 5 agent and coding contexts.
- Conclusion: Opus 5 proactively checks its work. Repeated generic verification instructions can cause wasteful over-verification; retain explicit verification only when it defines evidence, risk control, or a completion gate.
- Evidence gap: model initiative does not replace deterministic tests or repository-specific acceptance criteria.

- Source: [A field guide to Claude Fable 5: Finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns)
- Publisher/date/access: Anthropic, published 2026-07-06; accessed 2026-08-03.
- Applies to: Fable 5 long-horizon collaboration.
- Conclusion: outcome-focused context still needs explicit load-bearing unknowns; use code, tests, prototypes, rubrics, and plans as richer references, and allow iteration when implementation reveals unknowns.

- Source: [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code)
- Publisher/date/access: Anthropic, published 2026-07-07; accessed 2026-08-03.
- Applies to: Claude Code with Fable 5, Opus, and Sonnet.
- Conclusion: select larger models for ambiguous or knowledge-limited work and smaller models for routine work; use effort to control thoroughness, including files read, tools used, and verification. This supports the existing orchestrator/workhorse split without making one model universally preferred.
- Evidence gap: the article gives qualitative routing guidance, not repository-specific quality, latency, or quota measurements.

## OpenAI

- Source: [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- Publisher/access: OpenAI, accessed 2026-08-25.
- Applies to: GPT-5.6 Sol, Terra, and Luna prompting and agent workflows.
- Conclusion: OpenAI independently recommends leaner prompts, one statement per instruction, concise tool descriptions, explicit autonomy and approval boundaries, outcome-focused prompts, stopping conditions, and representative evals. This directly supports applying the same design direction to GPT-5.6.
- Evidence gap: OpenAI does not state that Anthropic’s exact prompt-removal percentage transfers to GPT-5.6. Treat cross-provider equivalence as a direction backed by separate guidance, not as a shared benchmark.

## Google

- Source: [Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- Publisher/date/access: Google AI for Developers, updated 2026-06-10; accessed 2026-08-03.
- Applies to: Gemini 3.x prompt and agent design, including Gemini 3.6.
- Conclusion: keep instructions clear, direct, and consistently structured; place critical constraints early; structure long context deliberately; tune agent reasoning and completeness to the task.

- Source: [Building Managed Agents](https://ai.google.dev/gemini-api/docs/custom-agents)
- Publisher/date/access: Google AI for Developers, updated 2026-07-30; accessed 2026-08-03.
- Applies to: the `antigravity-preview-05-2026` Gemini API managed-agent preview, whose default model is Gemini 3.6 Flash.
- Conclusion: AGENTS.md, skills, system instructions, files, and tool selection are distinct additive layers. Use the closest layer for the information instead of duplicating it across all of them.
- Evidence gap: managed agents are preview-only, have no agent-definition versioning, and do not support subagent nesting. Google does not make Claude’s “remove most of the system prompt” claim. Preserve Gemini-specific structure and critical-instruction placement while removing only demonstrated duplication.

## Open-weight runtimes

- Source: [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)
- Publisher/access: Qwen team, accessed 2026-08-25.
- Applies to: current Qwen-family and compatible open-weight agent runtimes using tool calling or MCP.
- Conclusion: capable open-weight runtimes can use the same canonical outcome, schema, tool-interface, and progressive-disclosure contracts. Keep runtime adapters thin and validate structured output and tool behavior on representative repository tasks.
- Evidence gap: tool-calling support, parameter count, or an upstream benchmark does not establish parity for implementation, blocking audit, or synthesis. Qualify each model/runtime pair through the same dated capability receipt used for hosted models; malformed output or a missing required capability yields `HOLD`.
