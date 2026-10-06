# Claude Code live-runtime validation

Offline Python tests prove only package structure and hook behavior when invoked directly. Before claiming compatibility with an exact Claude Code version, run a harmless live canary in that exact binary and record the evidence in `.claude/state/runtime-validation.json`.

Minimum canary:

1. record `claude --version`, OS, Python version, and Git version;
2. start Claude Code in a disposable Git repository containing this control plane and confirm the `SessionStart` health hook executes successfully;
3. confirm a benign `Read` and `Bash(git status --short)` are accepted;
4. confirm a known denied file read and a known `PreToolUse` ask/deny are surfaced by the runtime as intended without exposing a real secret;
5. initialize task state with `python .claude/bin/statectl.py init ...`, make one in-scope disposable change, and confirm an out-of-scope file edit requires approval;
6. confirm a shell-created out-of-scope change is reported by `PostToolUse` (then discard only the disposable repository);
7. confirm `Stop` is blocked while verification is missing, then run an inspected benign check through `statectl.py run-check --criterion "canary" -- <executable> <arguments>`, seal disposable verification and confirm it no longer blocks;
8. record exactly which permission expressions, matchers, hook events, and output schemas were observed working.

Example evidence shape:

```json
{
  "schema_version": 2,
  "binding": {
    "claude_code_version": "<full exact claude --version output>",
    "platform": "<platform.platform() output>",
    "files_sha256": {"<every inventoried relative path>": "<64 lowercase hex characters>"}
  },
  "validated_at": "<UTC timestamp>",
  "surfaces": {
    "permissions": "pass",
    "PreToolUse": "pass",
    "PostToolUse": "pass",
    "SessionStart": "pass",
    "Stop": "pass",
    "instruction_symlink_denied": "pass",
    "codex_claude_boundary": "pass"
  },
  "notes": []
}
```

Until this is executed, the manifest intentionally makes no exact Claude Code version compatibility claim.

## Binding and diagnosis

Generate the `binding` object using `.claude/hooks/runtime_compatibility.py`'s
`binding(root, full_version_output)` before live tests and compare it again after
tests. Only record passing evidence if both snapshots match. Never manufacture
surface passes from offline tests. Copy the completed evidence to the tested
repository's `.claude/state/runtime-validation.json`.

The inventory includes root instructions (including AGENTS.md for boundary
testing), `.mcp.json`, and all `.claude` files except generated `state`, offline
`selftest`, and `__pycache__` directories. This conservatively includes settings,
hooks, executable helpers, instructions, rules, skills and their resources,
agents, and contracts. SHA-256 covers complete bytes; file symlinks also bind
their link target spelling and target bytes. Directory symlinks are unsupported
and produce `invalid` evidence. Additions and deletions also invalidate evidence.
External user/managed configuration is not inventoried: record its effective
settings and instruction selection in notes and rerun tests when it changes.

Startup reports `runtime_compatibility` separately from structural health:
`missing` for absent evidence, `invalid` for malformed/legacy/incomplete or
non-passing evidence, `stale` for version/platform/inventory mismatch (including
an unavailable CLI version), and `verified` for matching recorded passes.
These are diagnostics and do not block normal work. `verified` means recorded
evidence matches, not cryptographic attestation or proof of current external policy.

## Disposable live canaries

Run these manually in fresh temporary Git repositories, never this working tree.
Use only synthetic marker text; preserve transcripts and effective runtime settings.
Do not launch Claude recursively for a second opinion. If symlink creation is
unavailable (for example Windows privilege restrictions), record the canary as
unrun; it cannot count as `pass`.

1. **Instruction symlinks:** create a sibling directory outside the disposable
   working directory with a file containing an unpredictable synthetic marker.
   In separate fresh sessions symlink project `CLAUDE.md`, a `.claude/rules/*.md`
   rule, and `AGENTS.md` to that file. Enable the corresponding instruction
   selection, keep `blockReadsOutsideWorkingDirectories` enabled, and do not add
   the sibling as a working directory. Inspect runtime diagnostics/transcripts
   for rejection of instruction loading; absence of the marker in a model reply
   alone is insufficient. Repeat with an explicit Read deny on the target and
   request a direct Read through the link. Record exact paths, expressions, and
   rejection evidence. All cases must reject before recording
   `instruction_symlink_denied: pass`.
2. **Codex/Claude boundary:** copy the control plane into a fresh disposable
   repository. Add distinct harmless marker directives to its CLAUDE.md and
   Codex AGENTS.md. Inspect loaded instruction sources with the installed
   runtime's diagnostics and effective Project Instructions selection. Confirm
   CLAUDE.md loads without importing AGENTS.md under the tested selection.
   If AGENTS.md also loads, record a boundary failure and the selection that
   caused it; do not claim the presence of CLAUDE.md universally excludes it.
   Record source-loading evidence and settings in notes before marking
   `codex_claude_boundary: pass`.

These fixture mutations test loading boundaries, not the unchanged production
inventory. Record the fixture differences in notes and bind compatibility to the
original copied control files, checking that those source files remain unchanged.
Discard only the explicitly identified disposable directories after collecting
evidence. The release motivating these canaries is
[v2.1.290](https://github.com/anthropics/claude-code/releases/tag/v2.1.290);
release notes alone do not establish a canary pass.

Offline regressions: `python .claude/selftest/test_runtime_compatibility.py`.
