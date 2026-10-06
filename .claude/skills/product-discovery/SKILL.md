---
name: "product-discovery"
description: "Turns a vague greenfield product or underspecified feature idea into a bounded MVP problem statement, acceptance criteria, risks, and implementation-ready scope before coding."
when_to_use: "Use when user intent is not yet specific enough to implement safely; not for routine repository changes that already have clear acceptance criteria."
allowed-tools:
  - "Skill(current-docs-research *)"
---
# Product discovery

Convert intent into the minimum durable specification needed to avoid building the wrong thing. Do not create a heavyweight product document unless the task requires one.

Establish:

- target user and job-to-be-done;
- observable problem or opportunity;
- MVP outcome and explicit non-goals;
- primary user flows and failure cases;
- data handled plus trust, security, and privacy implications;
- external systems and operational constraints that materially affect feasibility;
- observable/testable acceptance criteria;
- decisions that are reversible versus expensive to reverse.

Do not force a methodology, architecture, cloud, database, framework, or testing doctrine before requirements justify it. If current platform/API/library capabilities materially affect feasibility, invoke `current-docs-research` with one focused question.

Use information the user already supplied. Ask only when an unresolved product/security decision would materially change the MVP; otherwise make the smallest safe assumption explicit and continue.

## Completion criterion

Discovery is complete when an implementation owner can identify the objective, in/out scope, acceptance criteria, constraints, major risks, and next smallest slice without guessing product intent.

## Handoff

End with:

- `status`: `READY` or `NEEDS_DECISION`
- `objective`: bounded MVP outcome
- `acceptance`: observable acceptance criteria
- `scope`: in-scope and explicit non-goals
- `constraints`: operational, security, privacy, data, and external-system constraints
- `decisions`: resolved and unresolved high-impact choices
- `next`: `recon-gate` for an existing repository, `architecture-gate` if a material design choice must be made, or `implementation-slice` only when implementation readiness is already proven
