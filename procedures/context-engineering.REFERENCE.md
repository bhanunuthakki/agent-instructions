# Context-engineering source register

Verified 2026-07-29.

## Anthropic

- Source: [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- Publisher/date: Anthropic, 2026-07-24.
- Applies to: Claude 5 generation models, Claude Code, CLAUDE.md, skills, tools, and agent harnesses.
- Conclusion: remove duplicated and overly absolute scaffolding; rely more on model judgment; design expressive tool interfaces; use progressive disclosure; keep CLAUDE.md lightweight and focused on repository gotchas; keep skills opinionated but not overconstrained.
- Evidence gap: Anthropic reports no measurable coding-eval loss after removing over 80% of its own prompt for selected models, but that result is not a universal safe-deletion percentage for this repository.

- Source: [A field guide to Claude Fable 5: Finding your unknowns](https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns)
- Publisher/date: Anthropic, 2026-07-06.
- Applies to: Fable 5 long-horizon collaboration.
- Conclusion: outcome-focused context still needs explicit load-bearing unknowns; use code, tests, prototypes, rubrics, and plans as richer references, and allow iteration when implementation reveals unknowns.

## OpenAI

- Source: [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- Publisher/access: OpenAI, accessed 2026-07-29.
- Applies to: GPT-5.6 Sol, Terra, and Luna prompting and agent workflows.
- Conclusion: OpenAI independently recommends leaner prompts, one statement per instruction, concise tool descriptions, explicit autonomy and approval boundaries, outcome-focused prompts, stopping conditions, and representative evals. This directly supports applying the same design direction to GPT-5.6.
- Evidence gap: OpenAI does not state that Anthropic’s exact prompt-removal percentage transfers to GPT-5.6. Treat cross-provider equivalence as a direction backed by separate guidance, not as a shared benchmark.

## Google

- Source: [Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- Publisher/access: Google AI for Developers, accessed 2026-07-29.
- Applies to: Gemini 3 prompt and agent design.
- Conclusion: keep instructions clear, direct, and consistently structured; place critical constraints early; structure long context deliberately; tune agent reasoning and completeness to the task.

- Source: [Building Managed Agents](https://ai.google.dev/gemini-api/docs/custom-agents)
- Publisher/access: Google AI for Developers, accessed 2026-07-29.
- Applies to: Gemini Antigravity managed agents.
- Conclusion: AGENTS.md, skills, system instructions, files, and tool selection are distinct additive layers. Use the closest layer for the information instead of duplicating it across all of them.
- Evidence gap: Google does not make Claude’s “remove most of the system prompt” claim. Preserve Gemini-specific structure and critical-instruction placement while removing only demonstrated duplication.
