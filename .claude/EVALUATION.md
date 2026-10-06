# Control-plane evaluation and ablation contract

The package distinguishes **hard invariants** from **advisory complexity metrics**. A mechanism should remain only when it prevents a documented failure mode, improves evidence quality, or materially reduces operator/context cost.

## Hard release invariants

`selftest.py` and `metrics.py` must establish at minimum:

- settings and manifest parse; required control files exist;
- hook scripts compile and bounded guard probes behave as declared;
- common direct secret probes are blocked as defense in depth;
- ownership baseline cannot be directly edited while scope changes require an explicit transition;
- stale repository identity/HEAD invalidates active task authority;
- shell drift outside expected scope or into user-owned/protected paths is reported;
- structured resume state is bounded and treated as data;
- Stop gate rejects missing/stale verification for an active task;
- specialist agents have no direct write tools and cannot recursively spawn;
- required lifecycle skills, explicit narrow tool preapprovals, and path-scoped rules are internally consistent;
- verification rejects empty, failed, timed-out, stale, and state-changing execution records.

These are package invariants, not claims of full host/runtime compatibility.

## Advisory measurements

Agent count, hook count, description-character budgets, total rules/skills, and root instruction length are reported as measurements. They are not release failures merely because a fixed arbitrary budget is exceeded. A meaningful increase should still be justified by a new failure mode or measured benefit.

## Ablation procedure

For any proposed rule/hook/skill/agent:

1. name the failure mode or measurable objective;
2. construct a representative task/probe that fails or degrades without the mechanism;
3. compare baseline versus mechanism on correctness, false approvals/blocks, context/token cost, latency, and operator friction;
4. remove or simplify mechanisms that do not materially improve the target;
5. record version-sensitive assumptions separately from repository-independent policy.

Do not invent a universal quality score. Evaluation should use task-specific evidence and false-positive/false-negative observations.
