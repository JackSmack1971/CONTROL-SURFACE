# Task-local control-plane state

This directory holds optional ephemeral task state. It is ignored by Git except for this README and `.gitignore`; it is not authoritative project documentation.

## Authority files

- `ownership-baseline.json` — immutable-for-the-active-task Git-derived baseline: repository/worktree root, branch, baseline HEAD, and exact pre-task dirty paths.
- `change-surface.json` — mutable but governed task identity, expected/protected paths, and deliberate assignment of pre-task dirty paths.

Create both atomically after reconnaissance:

```text
python .claude/bin/statectl.py init --task "fix retry backoff" --expected "src/retry/**" --expected "tests/retry/**" --protected "src/generated/**"
```

Do not hand-edit `ownership-baseline.json`. Direct writes are denied. Scope changes should use `statectl.py update-scope`; widening expected paths, removing protection, assigning user-owned dirty paths, or deactivation is an explicit approval transition. If repository root/worktree, branch, or baseline HEAD diverges, active state is stale: perform fresh reconnaissance and reinitialize rather than silently refreshing it.

## Structured continuation/evidence files

- `active-task.json` — bounded data fields such as `objective`, `phase`, `scope`, `oracle`, `unresolved_decisions`.
- `decisions.json` — `{"decisions": [...]}` for durable task decisions only.
- `check-evidence.json` — execution records produced by `statectl.py run-check`; failed, timed-out, stale, or state-changing checks cannot support a seal.
- `verification.json` — current state-bound verification seal created after independent verification with `statectl.py seal-verification`.
- `control-plane-health.json` — latest SessionStart health diagnostic.
- `runtime-validation.json` — optional evidence from `RUNTIME-VALIDATION.md` after an actual Claude Code canary.
- `.hook-snapshots/` — transient bounded PreToolUse Git snapshots paired to shell calls.

Resume/compaction reinjects only selected JSON fields and labels them **DATA ONLY**. Do not persist pasted external instructions or raw repository/document content in these files.

The PostToolUse audit runs after a shell command. Its output is detection/feedback, never proof that an effect was prevented or reverted.

Run inspected checks with `python .claude/bin/statectl.py run-check --criterion "..." --timeout 300 -- <executable> <arguments>`, then seal with `python .claude/bin/statectl.py seal-verification --summary "..."`. Schema 2 rejects legacy prose-only seals; rerun checks rather than converting old claims. Rerunning the same command and criterion replaces its earlier result; other current-state failures remain blocking. Records are locally mutable evidence, not authenticated provenance or authorization.
