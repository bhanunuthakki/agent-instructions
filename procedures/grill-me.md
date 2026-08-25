---
name: grill-me
description: Interview the user to uncover load-bearing unknowns before a feature, design, plan, or consequential decision. Use when the user says “grill me”, “interview me”, “interrogate me”, invokes `/grill-me`, or asks to restart requirements discovery after an under-specified result.
---

# Grill Me

The user explicitly wants requirements discovery before a committed deliverable. Inspect the repository and supplied references first, then ask only questions whose answers could change scope, architecture, authority, data, or user-visible behavior.

## Find the unknowns

Separate:

- known unknowns the user already recognizes;
- assumptions recoverable from code, tests, prior decisions, or a safe default;
- unknowns the user may only recognize when shown an interface, reference, or reversible prototype;
- implementation details that can remain with the agent.

Start with the highest-cost-to-reverse unknown. Resolve dependencies before leaf preferences.

## Interview

- Ask one focused round at a time, sized for a real answer.
- Name a recommended default and its tradeoff when the options are understood.
- Probe interfaces, state ownership, failure behavior, permissions, data handling, out-of-scope cases, and the proof of success.
- Do not ask for facts available in the repository or current context.
- Use a reference, mockup, or disposable prototype when recognition is more informative than abstract questioning. Label it exploratory and do not let it silently become the accepted design.
- If implementation later reveals a load-bearing unknown, pause at that decision and resume the interview rather than forcing the original map onto the codebase.

## Stop

Stop when the consequential branches are resolved or the user explicitly asks to proceed. Summarize the agreed outcome, decision boundaries, open assumptions, and validation bar. Ask for confirmation only when a remaining ambiguity would materially change the deliverable.

For frontend work, `frontend-quality` remains the normal task-reasoning owner. Use this interview only for a material unresolved product choice; do not turn ordinary visual judgment into a ceremony.
