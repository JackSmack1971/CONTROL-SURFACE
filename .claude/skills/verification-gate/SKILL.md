---
name: "verification-gate"
description: "Independently executes acceptance and regression checks for the current repository change and returns VERIFIED or NOT VERIFIED without repairing failures."
when_to_use: "Use after implementation and blocking review findings are resolved, when the current changed behavior must be proven with executable evidence."
argument-hint: "[acceptance criteria and required checks]"
context: "fork"
agent: "verifier"
background: false
compatibility: "Targets Claude Code v2.1.218+ and requires the custom verifier subagent."
---
# Verification gate

Independently verify the current change against these task requirements and acceptance criteria:

$ARGUMENTS

You do not inherit the parent conversation. Derive repository commands and changed boundaries from the working tree and project documentation. Before first running an unfamiliar repository-controlled script, inspect its definition and refuse opaque or unsafe execution. Do not install dependencies or repair files. When task authority is active, the check runner may write execution records in `.claude/state/`.

Use the requirements-derived oracle matrix from `oracle-design` when supplied. Account for each criterion as executed, failed, or unverified; do not silently replace it with implementation-derived expectations.

With active task authority, execute each inspected, authorized check through:

```text
python .claude/bin/statectl.py run-check --criterion "<acceptance criterion>" --timeout 300 -- python -m pytest tests/relevant_test.py
```

The runner uses literal argument vectors without a shell. It records exit status, timeout, timestamps, and before/after Git fingerprints. A check that changes the working state cannot support a seal; inspect its effects and rerun against the final state. Shell scripts and external effects still require normal authorization; wrapping a command does not authorize it.

Start with focused checks, then run broader repository-required checks when proportionate. Inspect changed tests for weakened, skipped, tautological, implementation-mirroring, or over-mocked oracles when those defects could invalidate the result.

An unexecuted check is never a pass. Distinguish environment blockers from product failures.

## Handoff

End with:

- `status`: exactly `VERIFIED` or `NOT VERIFIED`
- `commands`: exact checks executed and outcomes
- `proof`: what each successful result establishes
- `failures`: failed checks or blockers with evidence
- `unverified`: behavior not proven by the executed evidence
- `next`: `complete`, `debug-loop`, or `implementation-slice`

State that the verdict becomes stale if the working-tree diff/state changes after evidence collection.

If the parent accepts a `VERIFIED` result, `.claude/bin/statectl.py` exists, and active task authority was initialized, the parent may seal that exact current Git state with:

```text
python .claude/bin/statectl.py seal-verification --summary "<criteria satisfied and evidence limits>"
```

Do not create task authority merely to produce a seal.

Sealing requires nonempty successful current-state execution records. Records are local evidence, not authenticated attestations: they do not prove independence, completeness, or a correct oracle. Exit zero alone does not establish acceptance. Timeouts terminate the direct process; they do not guarantee cleanup of descendant processes.
