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
  "schema_version": 1,
  "claude_code_version": "<exact observed version>",
  "platform": "<os>",
  "validated_at": "<UTC timestamp>",
  "surfaces": {
    "permissions": "pass",
    "PreToolUse": "pass",
    "PostToolUse": "pass",
    "SessionStart": "pass",
    "Stop": "pass"
  },
  "notes": []
}
```

Until this is executed, the manifest intentionally makes no exact Claude Code version compatibility claim.
