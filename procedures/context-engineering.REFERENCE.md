# Context-engineering source register

Verified 2026-08-03.

## Anthropic

- Source: [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- Publisher/date/access: Anthropic, published 2026-07-24; accessed 2026-08-03.
- Applies to: Claude Opus 5 and Fable 5, Claude Code, CLAUDE.md, skills, tools, and agent harnesses.
- Conclusion: remove duplicated and overly absolute scaffolding; rely more on model judgment; design expressive tool interfaces; use progressive disclosure; keep CLAUDE.md lightweight and focused on repository gotchas; keep skills opinionated but not overconstrained.
- Evidence gap: Anthropic reports no measurable coding-eval loss after removing over 80% of its own prompt for selected models, but that result is not a universal safe-deletion percentage for this repository.

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
- Publisher/access: OpenAI, accessed 2026-08-03.
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
