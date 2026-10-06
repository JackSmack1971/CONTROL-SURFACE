---
name: "architecture-gate"
description: "Evaluates architecture, stack, API, data, security, dependency, or deployment decisions against repository evidence and current external constraints before implementation."
when_to_use: "Use only when a decision changes long-lived interfaces, ownership boundaries, dependencies, security posture, persistence, or deployment topology; not for routine local implementation choices."
allowed-tools:
  - "Skill(recon-gate *)"
  - "Skill(current-docs-research *)"
---
# Architecture gate

Choose the smallest durable design justified by evidence. Preserve established repository patterns unless the task supplies a reason to change them.

## Entry gate

Before deciding, require enough repository evidence to name the current design, affected contracts, and verification boundary. If that evidence is missing, invoke `recon-gate` first and use its handoff. If the decision depends on version-sensitive external behavior, invoke `current-docs-research` with one focused question.

## Decision procedure

For each material decision:

1. State the problem and hard constraints.
2. Map affected contracts, data flows, ownership boundaries, failure domains, and migration surface.
3. Compare the smallest viable options, including keeping the current design.
4. Weigh correctness, complexity, migration cost, operability, security, compatibility, and reversibility.
5. Separate repository evidence, verified external facts, and inference.
6. Choose the smallest design supported by the evidence.
7. Define compatibility/migration requirements and the verification strategy.

Use the `system-architect` subagent when independent judgment materially reduces risk or context pollution. Give it the concrete decision, relevant paths, constraints, and known evidence. Treat its result as evidence, not authority.

## Commitment threshold

Do not silently commit a high-impact product, compatibility, security, persistence, or dependency choice when viable options have materially different consequences. Return `NEEDS_DECISION` with the alternatives and consequences instead.

## Handoff

End with:

- `status`: `READY`, `NEEDS_DECISION`, or `BLOCKED`
- `decision`: chosen design or unresolved decision
- `evidence`: repository facts and any verified external constraints that control the choice
- `scope`: contracts/paths/boundaries implementation may change
- `oracle`: checks that would prove the design was implemented correctly
- `next`: normally `implementation-slice`, or the exact prerequisite still required
