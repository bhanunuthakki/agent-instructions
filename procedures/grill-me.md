---
name: grill-me
description: Resolve load-bearing product unknowns before a feature, design, plan, or consequential decision. Use for a lightweight initial clarification round when needed, or for a deeper interview when the user explicitly asks to be grilled or interviewed.
---

# Grill Me

Inspect the repository and supplied references first, then ask only questions whose answers could change the outcome, scope, authority, data, user-visible behavior, or another expensive-to-reverse decision.

## Choose the mode

- **Lightweight clarification:** use one concise initial round when an unresolved goal, success condition, scope boundary, or product tradeoff is load-bearing, or when a short answer is likely to avoid materially more user/agent effort. Recommend a default and continue once the branch is resolved.
- **Deep interview:** use iterative rounds only when the user explicitly invokes `/grill-me`, asks to be interviewed, or asks to restart requirements discovery. Do not silently turn the lightweight route into a prolonged interview.

## Find the unknowns

Separate:

- known unknowns the user already recognizes;
- assumptions recoverable from code, tests, prior decisions, or a safe default;
- unknowns the user may only recognize when shown an interface, reference, or reversible prototype;
- implementation details that can remain with the agent.

Start with the highest-cost-to-reverse unknown. Resolve dependencies before leaf preferences.

## Interview

- In lightweight mode, ask one concise round. In deep mode, ask one focused round at a time, sized for a real answer.
- Name a recommended default and its tradeoff when the options are understood.
- Probe interfaces, state ownership, failure behavior, permissions, data handling, out-of-scope cases, and the proof of success.
- Do not ask for facts available in the repository or current context.
- Use a reference, mockup, or disposable prototype when recognition is more informative than abstract questioning. Label it exploratory and do not let it silently become the accepted design.
- If implementation later reveals a load-bearing unknown, pause at that decision and resume the interview rather than forcing the original map onto the codebase.

## Stop

Stop when the consequential branches are resolved or the user explicitly asks to proceed. Summarize the agreed outcome, decision boundaries, open assumptions, and validation bar. Ask for confirmation only when a remaining ambiguity would materially change the deliverable.

For frontend work, `frontend-quality` remains the normal task-reasoning owner. Use this interview only for a material unresolved product choice; do not turn ordinary visual judgment into a ceremony.
