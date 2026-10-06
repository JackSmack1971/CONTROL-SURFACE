---
name: "implementation-slice"
description: "Implements one bounded engineering slice after requirements and evidence are sufficient, preserving user work and verifying the actual changed behavior."
when_to_use: "Use when objective, acceptance criteria, expected change surface, and a credible oracle are known and high-impact decisions are resolved."
argument-hint: "[objective and acceptance criteria]"
allowed-tools:
  - "Skill(oracle-design *)"
  - "Skill(recon-gate *)"
  - "Skill(debug-loop *)"
  - "Skill(architecture-gate)"
  - "Skill(current-docs-research *)"
  - "Skill(review-change *)"
  - "Skill(verification-gate *)"
---
# Implementation slice

Implement the smallest coherent delta that satisfies the active acceptance criteria.

## Readiness gate

Before writing, ensure the task has a current baseline, bounded change surface, and credible oracle.

- If repository ownership/current behavior is unclear, invoke `recon-gate`.
- If a failure is known but its cause is not, invoke `debug-loop`.
- If the task requires a material architecture/security/dependency/persistence choice, invoke `architecture-gate`.
- If a decision depends on current external SDK/API/framework behavior, invoke `current-docs-research` with the narrow question.

Do not repeat a gate when current evidence already satisfies its completion criterion. When invoking any `context: fork` specialist, pass a self-contained argument payload because it does not inherit this conversation.

For nontrivial logic or contract changes, invoke `oracle-design` before implementation with requirements, public signatures, domain constraints, and test-safe interfaces only. Do not supply implementation, diffs, existing test expectations, or the implementer's reasoning. Preserve its acceptance matrix for review and verification. If this separation is unavailable, report the limitation.

## Execution rules

- Keep one implementation owner for overlapping files. Concurrent/background writers must use separate Git worktrees; serialize overlapping work.
- Follow nearby repository patterns before introducing abstractions.
- Edit canonical sources, not generated or vendored artifacts, unless generation output is explicitly in scope.
- Preserve pre-existing dirty, staged, and untracked user work. Never copy ignored secrets or `.env` files into worktrees automatically.
- Avoid dependency churn, opportunistic cleanup, unrelated formatting, and speculative features.
- Change tests only to express requested behavior or regression coverage; never weaken an oracle to make a failure disappear.
- Update docs/contracts when implementation changes an externally meaningful fact.
- Run the narrowest useful check after each meaningful step when feedback is cheap.

If `.claude/bin/statectl.py` exists and task authority was initialized, update expanded scope with `python .claude/bin/statectl.py update-scope ...`. If it does not exist, keep the same scope discipline in the coordinator handoff; do not invent a replacement state system.

## Review and verification loop

1. Inspect the actual diff after implementation.
2. For substantive changes, invoke `review-change` with the objective, acceptance criteria, and intentional scope.
3. Fix blocking review findings with another bounded implementation pass, then re-run `review-change` for the affected current diff.
4. When review has no blockers, invoke `verification-gate` with the acceptance criteria and required regression checks.
5. If verification fails and the cause is unclear, route to `debug-loop`; if the cause is already proven, repair directly, then review and verify again.
6. Do not spin on the same failure: after the same unresolved blocker survives two evidence-producing repair attempts, return it to the user with the evidence and required decision/input.

Reviewer and verifier agents must not edit implementation files.

## Completion criterion

Do not report completion until the current diff has no unresolved blocking review finding and the current state has a `VERIFIED` verification result. Any substantive edit after either result makes that evidence stale.

## Handoff

End with:

- `status`: `VERIFIED`, `NEEDS_REPAIR`, `NEEDS_DECISION`, or `BLOCKED`
- `changed`: files/symbols intentionally changed
- `evidence`: focused checks plus review/verification results
- `scope`: actual changed surface and any deliberate deviations from the expected surface
- `oracle`: final checks that bind the result
- `next`: `complete` or the exact next skill/action required
