#!/usr/bin/env python3
"""Argument-sensitive shell guard plus bounded pre-command scope snapshot."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

from control_common import capture_git_state, deadline_after, find_project_root, read_baseline, read_surface, state_dir, validate_binding

# Direct secret-store access and execution-policy bypasses are defense-in-depth here.
# They are not represented as a complete credential boundary; host filesystem/egress and
# credential reachability controls remain the authoritative boundary where available.
HARD_RULES = [
    (r"\b(curl|wget|iwr|invoke-webrequest|irm|invoke-restmethod)\b[^\n]*\|\s*(sh|bash|zsh|python\d?|node|iex|invoke-expression)\b", "downloaded content is piped directly into an interpreter"),
    (r"(^|[\s;|&])(iex|invoke-expression|eval)(\s|$)", "dynamic expression evaluation bypasses ordinary command inspection"),
    (r"\bbase64\b[^\n]*(\s-d\b|--decode\b)|\bfrombase64string\b|\b-encodedcommand\b|(^|\s)-enc\s", "obfuscated or encoded code execution"),
    (r"\b(?:cat|type|more|less|head|tail|sed|awk|grep|rg|findstr|get-content|gc)\b[^\n]*(?:^|[\\/])?\.env(?:\.[\w.-]+)?\b", "direct secret-file access"),
    (r"\b(?:python\d?|py)\b[^\n]*(?:open|read_text|read_bytes)\s*\([^\n]*[\"'](?:[^\"']*[\\/])?\.env(?:\.[\w.-]+)?[\"']", "scripted secret-file access"),
    (r"\b(?:printenv|env)\b(?:\s+[A-Za-z_][A-Za-z0-9_]*)?\b|\bget-childitem\s+env:|\bgci\s+env:|\$env:[A-Za-z_][A-Za-z0-9_]*|\becho\s+\$[A-Za-z_][A-Za-z0-9_]*", "environment variable or credential discovery"),
    (r"(?:^|[\s\"'=:/\\])(?:\.aws|\.ssh|\.gnupg|\.kube|\.docker|\.config[/\\](?:gh|gcloud|openai|anthropic))(?:[/\\]|$)|\.git-credentials\b|\.netrc\b|\.npmrc\b|\.pypirc\b|(?:^|[/\\])\.env(?:\.[\w.-]+)?(?:$|[\s\"'])|credentials\.json\b|\bid_rsa\b|\bid_ed25519\b", "credential or secret store access"),
    (r"(?:>|>>|out-file|set-content|add-content|remove-item|move-item|copy-item)[^\n]*(?:\.claude[/\\]settings\.json|\.claude[/\\]hooks[/\\])", "attempt to mutate protected control-plane enforcement files from the shell"),
]

# Declarative permissions handle standard spellings. These rules cover normalized or
# alternate command forms and contextual gaps that project permission patterns may miss.
ASK_RULES = [
    (r"\bgit\b[^\n;|&]{0,160}\breset\b[^\n;|&]*--hard\b", "git reset --hard can destroy uncommitted work"),
    (r"\bgit\b[^\n;|&]{0,160}\bclean\b[^\n;|&]*(-[a-z]*f[a-z]*|--force)\b", "git clean -f can delete untracked work"),
    (r"\bgit\b[^\n;|&]{0,160}\bpush\b", "pushing changes mutates a remote repository"),
    (r"\bgit\b[^\n;|&]{0,160}\bbranch\b[^\n;|&]*\s-D\b", "git branch -D force-deletes a branch"),
    (r"\bgit\b[^\n;|&]{0,160}\b(checkout|restore)\b[^\n;|&]*(\s--\s|\s\.(\s|$)|--source|--staged\s+--worktree)", "destructive checkout/restore can overwrite working-tree changes"),
    (r"\bgit\b[^\n;|&]{0,160}\bstash\s+(drop|clear)\b", "git stash drop/clear destroys stashed work"),
    (r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|--recursive\s+--force|--force\s+--recursive)\b", "recursive forced delete"),
    (r"\bremove-item\b[^\n;|&]*-recurse[^\n;|&]*-force|\bremove-item\b[^\n;|&]*-force[^\n;|&]*-recurse", "recursive forced delete"),
    (r"\bset-executionpolicy\b", "PowerShell execution-policy changes alter a host security boundary"),
    (r"\bdrop\s+(table|database)\b|\btruncate\s+table\b", "destructive database statement"),
    (r"\b(npm|pnpm|yarn)\s+(install|i|add)\b|\b(pip|pip3)\s+install\b|\buv\s+add\b|\bcargo\s+add\b|\bpoetry\s+add\b", "dependency installation/addition changes the dependency surface or executes downloaded packages"),
    (r"\bnpx\s+(?:-y|--yes)\b|\bpnpm\s+dlx\b|\byarn\s+dlx\b|\buvx\b|\bpipx\s+run\b", "ephemeral package runners can download and execute third-party code"),
    (r"\b(?:npm|pnpm|yarn)\s+publish\b(?![^\n;|&]*--dry-run)|\btwine\s+upload\b|\bcargo\s+publish\b(?![^\n;|&]*--dry-run)|\bdocker\s+push\b", "publishing creates an external artifact or release effect"),
    (r"\bgh\s+(pr|issue|release|repo)\s+(create|delete|merge|close|reopen|archive)\b", "GitHub mutation changes external state"),
    (r"\b(terraform|tofu)\s+(apply|destroy|import)\b", "infrastructure mutation can change external resources"),
    (r"\bkubectl\s+(?:apply|create|delete|patch|replace|scale)\b(?![^\n;|&]*--dry-run)|\bkubectl\s+rollout\s+(?:restart|undo)\b|\bkubectl\s+set\b", "Kubernetes mutation changes cluster state"),
    (r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b(?![^\n;|&]*--dry-run)", "Helm mutation changes cluster/release state"),
]

HARD_COMPILED = [(re.compile(p, re.IGNORECASE), r) for p, r in HARD_RULES]
ASK_COMPILED = [(re.compile(p, re.IGNORECASE), r) for p, r in ASK_RULES]


def block(reason: str) -> None:
    sys.stderr.write(
        "BLOCKED by project control plane: " + reason + "\n"
        "The command is not an authorized route around project policy. Use an inspectable alternative.\n"
    )
    raise SystemExit(2)


def ask(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": reason}}))
    raise SystemExit(0)


def is_statectl(command: str) -> bool:
    return bool(re.search(r"(?:^|\s)(?:python\d?|py)\s+[^\n]*\.claude[/\\]bin[/\\]statectl\.py\b", command, re.IGNORECASE))


def stale_diagnostic_command(command: str, root: Path) -> bool:
    """Allow bounded read-only diagnostic chains while binding is stale."""
    value = command.strip()
    if not value or any(char in value for char in "|;<>`$\n\r"):
        return False
    parts = [part.strip() for part in value.split("&&")]
    if any(not part or "&" in part for part in parts):
        return False
    patterns = (
        r"git\s+status(?:\s+--short)?",
        r"git\s+diff(?:\s+--(?:stat|name-only|check))?",
        r"git\s+log(?:\s+(?:-\d+|--oneline)){0,2}",
        r"git\s+show(?:\s+--stat)?(?:\s+[0-9a-f]{7,40})?",
        r"git\s+rev-parse\s+--(?:show-toplevel|show-prefix|abbrev-ref\s+HEAD|verify\s+HEAD)",
        r"git\s+branch(?:\s+--show-current)?",
    )
    for part in parts:
        if re.fullmatch(r"(?:python\d?|py)\s+\.claude[/\\]bin[/\\]statectl\.py\s+status", part, re.IGNORECASE):
            continue
        cd = re.fullmatch(r"cd\s+(['\"])(.*?)\1", part, re.IGNORECASE)
        if cd:
            try:
                if Path(cd.group(2)).resolve() == root.resolve():
                    continue
            except OSError:
                pass
            return False
        if re.fullmatch(r"wc\s+-l\s+READ-ONLY-RECON\.md\s+SYNTHESIS-BARRIER\.md", part, re.IGNORECASE):
            continue
        if any(re.fullmatch(pattern, part, re.IGNORECASE) for pattern in patterns):
            continue
        return False
    return True


def stale_binding(root: Path) -> bool:
    surface = read_surface(root)
    if surface is None:
        return False
    try:
        validate_binding(root, surface, read_baseline(root), deadline_after())
        return False
    except ValueError:
        return True


def guard_authority_files(command: str) -> None:
    if is_statectl(command):
        if re.search(r"\b(update-scope|deactivate)\b", command, re.IGNORECASE):
            ask("task authority is being changed; scope widening, ownership assignment, or deactivation requires an explicit transition")
        return
    if not re.search(r"\.claude[/\\]state[/\\](?:change-surface|ownership-baseline)\.json\b", command, re.IGNORECASE):
        return
    block("direct shell mutation/access of task authority files is prohibited; use .claude/bin/statectl.py")


def snapshot_shell_scope(root: Path, tool_use_id: str | None, surface: dict | None, deadline: float) -> None:
    if surface is None:
        return
    if not tool_use_id:
        block("active change-surface state requires tool_use_id to audit shell-side file effects")
    try:
        baseline = read_baseline(root)
        current = validate_binding(root, surface, baseline, deadline)
        snapshots = state_dir(root) / ".hook-snapshots"
        snapshots.mkdir(parents=True, exist_ok=True)
        now = time.time()
        # Bounded cleanup: inspect at most 64 stale entries.
        for old in list(snapshots.glob("*.json"))[:64]:
            try:
                if now - old.stat().st_mtime > 86400:
                    old.unlink()
            except OSError:
                pass
        name = hashlib.sha256(tool_use_id.encode("utf-8")).hexdigest() + ".json"
        payload = {"tool_use_id": tool_use_id, "created": int(now), "state": surface, "baseline": baseline, "git": current}
        (snapshots / name).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    except SystemExit:
        raise
    except Exception as exc:
        block(f"could not establish bounded pre-command Git scope baseline ({type(exc).__name__}: {exc})")


def main() -> None:
    deadline = deadline_after(6.0)
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name")
        if tool_name not in {"Bash", "PowerShell"}:
            raise ValueError("unexpected tool_name")
        command = payload["tool_input"]["command"]
        if not isinstance(command, str):
            raise TypeError("command is not a string")
        cwd = payload.get("cwd") or os.getcwd()
        root = find_project_root(cwd)
        tool_use_id = payload.get("tool_use_id")
    except Exception as exc:
        block(f"guard input could not be parsed ({type(exc).__name__})")

    try:
        guard_authority_files(command)
        for regex, reason in HARD_COMPILED:
            if regex.search(command):
                block(reason)
        surface = read_surface(root)
        if surface is not None and stale_binding(root):
            recovery = re.fullmatch(
                r"(?:python\d?|py)\s+\.claude[/\\]bin[/\\]statectl\.py\s+recover\b[^\n;&|<>`]*",
                command.strip(), re.IGNORECASE,
            )
            if recovery:
                ask("stale task authority recovery replaces the active task identity, captures a new Git baseline, and invalidates prior verification; confirm fresh reconnaissance and this exact task/scope")
            if stale_diagnostic_command(command, root):
                raise SystemExit(0)
            block("active task authority is stale; only statectl status and the bounded standalone Git read-only inspection commands are available until approved recovery")
        snapshot_shell_scope(root, tool_use_id if isinstance(tool_use_id, str) else None, surface, deadline)
        for regex, reason in ASK_COMPILED:
            if regex.search(command):
                ask(reason)
    except SystemExit:
        raise
    except Exception as exc:
        block(f"guard internal error ({type(exc).__name__}: {exc})")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
