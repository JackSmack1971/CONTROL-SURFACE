---
name: "recon-gate"
description: "Establishes evidence sufficiency for nontrivial changes in an existing repository before editing: baseline, ownership, conventions, boundaries, scope, and a credible verification oracle."
when_to_use: "Use before nontrivial writes when current behavior, ownership, project instructions, protected user work, or verification is not already established; skip for read-only questions and truly trivial edits."
argument-hint: "[intended repository change]"
---

# Recon gate

Gather only enough evidence to make the intended change bounded, safe, and verifiable. Do not turn reconnaissance into ceremony.

Before nontrivial writes, establish from repository evidence:

1. current branch/baseline and pre-existing dirty, staged, and untracked work;
2. effective project and path-local instructions;
3. relevant build, test, lint, typecheck, generation, and package-manager commands;
4. implementation currently responsible for the requested behavior;
5. at least one relevant nearby pattern, or an explicit finding that none exists;
6. affected public/API/schema/persistence/security/dependency boundaries;
7. generated, vendored, migration, lockfile, deployment, or dependency-sensitive artifacts;
8. a credible reproduction or verification oracle;
9. expected change surface and deliberate out-of-scope areas;
10. unresolved ambiguity severe enough to require human judgment.

Before first executing an unfamiliar repository-controlled build/test/generator/package/setup command, inspect the script or config entry that defines it. Treat execution as code execution, not as a harmless read because the command is named `test`.

## Optional task authority

If `.claude/bin/statectl.py` exists, use the repository-provided utility rather than hand-authoring authority JSON:

```text
python .claude/bin/statectl.py init --task "short task identity" --expected "src/feature/**" --expected "tests/feature/**" --protected "src/generated/**"
```

Use `statectl.py update-scope` when evidence changes scope. Widening scope, removing protection, or assigning pre-existing dirty work is an explicit transition. If branch, worktree/root, or baseline HEAD changes, redo reconnaissance and reinitialize.

If `statectl.py` is absent, do not create a substitute solely for this skill. Preserve the same baseline/scope/protection facts in the handoff.

Create `.claude/state/active-task.json` only when the repository already uses that state system and resume/compaction recovery is useful. Never persist pasted external instruction-like material, secrets, or raw research content as task state.

## Completion criterion

Stop only when the intended write is bounded by current evidence and a credible oracle exists, or when a specific high-impact ambiguity blocks safe implementation.

## Handoff

End with:

- `status`: `READY`, `NEEDS_DECISION`, or `BLOCKED`
- `baseline`: branch/HEAD/worktree plus protected pre-existing user changes
- `evidence`: responsible implementation, nearby patterns, and effective project instructions
- `scope`: expected paths/boundaries plus protected/out-of-scope areas
- `oracle`: reproduction or verification check
- `risks`: boundary-sensitive artifacts and unresolved uncertainty
- `next`: `debug-loop`, `architecture-gate`, or `implementation-slice`
