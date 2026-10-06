---
name: "debug-loop"
description: "Diagnoses a bug, failing test, regression, or broken behavior through reproduce, localize, hypothesize, discriminate, and root-cause analysis before code is edited."
when_to_use: "Use when behavior is failing and the root cause is not yet established; do not use once a specific causal defect and regression oracle are already proven."
argument-hint: "[failure, symptom, or failing check]"
context: "fork"
agent: "root-cause-debugger"
background: false
compatibility: "Targets Claude Code v2.1.218+ and requires the custom root-cause-debugger subagent."
---
# Debug loop

Diagnose this failure without editing the repository:

$ARGUMENTS

You do not inherit the parent conversation, so derive required repository context from files and executable behavior. Use the repository's existing toolchain; do not install dependencies.

Follow:

`OBSERVE -> REPRODUCE -> LOCALIZE -> HYPOTHESIZE -> DISCRIMINATE -> ROOT CAUSE -> REGRESSION ORACLE`

Prefer the smallest safe reproducer or an existing failing test. Distinguish symptoms from causes. Use competing hypotheses until one is discriminated by evidence. If reproduction is unsafe, unavailable, flaky, environment-dependent, or credential-dependent, report that limitation instead of fabricating evidence.

## Completion criterion

Finish only when either:

- a specific causal defect, minimal correction boundary, and executable regression oracle are established; or
- the missing evidence/blocker preventing root-cause proof is identified precisely.

## Handoff

End with:

- `status`: `ROOT_CAUSE_FOUND` or `BLOCKED`
- `root_cause`: causal defect, not the observed symptom
- `evidence`: reproducer, failing check, traces, or code facts that discriminate the cause
- `scope`: minimal files/symbols likely requiring correction
- `oracle`: exact regression check the implementation owner should use
- `next`: normally `implementation-slice`, or the prerequisite needed to continue
