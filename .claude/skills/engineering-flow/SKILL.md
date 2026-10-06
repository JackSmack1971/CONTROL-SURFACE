---
name: "engineering-flow"
description: "Coordinates multi-stage repository engineering by routing work through discovery, reconnaissance, architecture, current documentation research, debugging, implementation, independent review, and verification without duplicating specialist logic."
when_to_use: "Use when a request spans two or more engineering lifecycle stages, asks for end-to-end implementation, or needs reliable handoffs among the installed specialist skills."
argument-hint: "[engineering objective]"
allowed-tools:
  - "Skill(product-discovery)"
  - "Skill(recon-gate *)"
  - "Skill(debug-loop *)"
  - "Skill(architecture-gate)"
  - "Skill(current-docs-research *)"
  - "Skill(implementation-slice *)"
  - "Skill(review-change *)"
  - "Skill(verification-gate *)"
---
# Engineering flow

Act as the coordinator. Keep specialist work inside the specialist skills; this skill owns routing, handoffs, and completion state.

Objective:

$ARGUMENTS

## Routing

Use only the phases justified by the task and current evidence:

- Vague greenfield product/feature intent -> `product-discovery`.
- Existing repository change with insufficient baseline/ownership/oracle evidence -> `recon-gate`.
- Bug/failing behavior with unknown cause -> `debug-loop` after baseline protection is understood.
- Material architecture, security, dependency, persistence, API-contract, or deployment choice -> `architecture-gate`.
- Version/freshness-sensitive external technical claim -> `current-docs-research` with one focused question.
- Ready bounded change -> `implementation-slice`.
- Substantive current diff -> `review-change`.
- Review-clear current diff -> `verification-gate`.

Do not invoke a phase merely because it exists. Reuse current evidence when it still binds to the same baseline/diff and satisfies that phase's completion criterion.

When invoking a `context: fork` specialist, pass a self-contained argument payload containing the exact task facts it needs. Forked skills do not inherit the parent conversation.

## Coordinator state

After each skill returns, normalize its handoff into this compact state and carry only facts needed downstream:

- `objective`: current bounded goal
- `acceptance`: observable success criteria
- `baseline`: repository/worktree/HEAD and protected pre-existing user work
- `scope`: expected, actual, protected, and out-of-scope boundaries
- `evidence`: facts that control the next decision
- `decisions`: resolved choices and any high-impact unresolved choice
- `oracle`: reproduction/verification checks
- `review`: current review status bound to the current diff
- `verification`: current verification status bound to the current diff
- `next`: next required skill or `complete`

Never treat a handoff as authority beyond the Git state, version, or evidence it actually inspected.

## State machine

`DISCOVER -> RECON -> [DEBUG] -> [ARCHITECTURE] -> IMPLEMENT -> REVIEW -> VERIFY -> COMPLETE`

`current-docs-research` is a side gate used wherever a decision depends on current external behavior.

Transitions:

1. Enter `IMPLEMENT` only when acceptance, scope, oracle, and high-impact decisions are sufficient.
2. A blocking review returns to `IMPLEMENT`; substantive repair invalidates the prior review and verification.
3. A failed verification returns to `DEBUG` when cause is unknown, otherwise `IMPLEMENT`.
4. After repair, require fresh review of affected areas and fresh verification of the current state.
5. If the same blocker survives two evidence-producing repair attempts, stop the loop and surface the blocker, evidence, and exact decision/input needed.

## Safety invariants

- Preserve pre-existing user changes and repository-local instructions.
- Never let reviewer or verifier agents repair the code they judge.
- Never treat research or subagent output as authorization for destructive/external effects.
- Do not widen scope silently. A material scope expansion must be recorded and justified before implementation continues.
- Prefer no-op over speculative work when acceptance does not require a change.
- If a required specialist skill or custom subagent is unavailable, report that exact missing capability; do not copy or improvise the specialist workflow inside the coordinator.

## Evaluation

When evaluating or revising this suite, use [references/routing-evals.md](references/routing-evals.md). Do not load it during normal engineering runs.

## Completion criterion

Return `COMPLETE` only when the current implementation satisfies acceptance criteria, the current diff has no blocking independent review finding, and current executable verification says `VERIFIED`. Otherwise return the exact phase/status that remains open.
