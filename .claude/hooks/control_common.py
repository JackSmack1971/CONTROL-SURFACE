#!/usr/bin/env python3
"""Shared bounded state helpers for deterministic control-plane hooks."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any

STATE_SCHEMA = 2
BASELINE_SCHEMA = 1
VERIFICATION_SCHEMA = 2
MAX_DIRTY_PATHS = 256
MAX_SAMPLE_BYTES = 8 * 1024 * 1024
PER_FILE_SAMPLE = 128 * 1024


def deadline_after(seconds: float = 6.0) -> float:
    return time.monotonic() + seconds


def remaining(deadline: float, cap: float = 2.5) -> float:
    left = deadline - time.monotonic()
    if left <= 0.15:
        raise TimeoutError("control-plane internal deadline exhausted")
    return max(0.15, min(cap, left - 0.05))


def canonical_root(path: Path | str) -> Path:
    return Path(path).resolve()


def find_project_root(start: Path | str) -> Path:
    current = canonical_root(start)
    for candidate in (current, *current.parents):
        if (candidate / ".claude").is_dir():
            return candidate
    return canonical_root(os.environ.get("CLAUDE_PROJECT_DIR") or start)


def run_git(root: Path, args: list[str], deadline: float, *, text: bool = False) -> subprocess.CompletedProcess[Any]:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=text,
        check=False,
        timeout=remaining(deadline),
    )
    if proc.returncode != 0:
        stderr = proc.stderr if text else proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError((stderr or "git command failed").strip())
    return proc


def parse_porcelain_z(data: bytes) -> tuple[str | None, dict[str, str]]:
    records = data.split(b"\0")
    branch: str | None = None
    paths: dict[str, str] = {}
    i = 0
    while i < len(records):
        raw = records[i]
        i += 1
        if not raw:
            continue
        text = raw.decode("utf-8", errors="surrogateescape")
        if text.startswith("## "):
            branch = text[3:].split("...", 1)[0].strip()
            continue
        if len(text) < 4:
            continue
        status = text[:2]
        path = text[3:].replace("\\", "/")
        if path:
            paths[path] = status
        if ("R" in status or "C" in status) and i < len(records):
            other_raw = records[i]
            i += 1
            if other_raw:
                other = other_raw.decode("utf-8", errors="surrogateescape").replace("\\", "/")
                paths[other] = status
    return branch, paths


def bounded_file_signature(path: Path, remaining_budget: list[int]) -> dict[str, Any]:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return {"kind": "missing"}
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if not path.is_file():
        return {"kind": "other", "size": st.st_size, "mtime_ns": st.st_mtime_ns, "mode": st.st_mode}

    size = st.st_size
    budget = max(0, remaining_budget[0])
    sample_cap = min(PER_FILE_SAMPLE, budget)
    digest = hashlib.sha256()
    sampled = 0
    if sample_cap > 0:
        with path.open("rb") as fh:
            if size <= sample_cap:
                data = fh.read(sample_cap)
                digest.update(data)
                sampled = len(data)
            else:
                first_n = sample_cap // 2
                last_n = sample_cap - first_n
                first = fh.read(first_n)
                fh.seek(max(0, size - last_n))
                last = fh.read(last_n)
                digest.update(first)
                digest.update(b"\0<sample-boundary>\0")
                digest.update(last)
                sampled = len(first) + len(last)
    remaining_budget[0] -= sampled
    return {
        "kind": "file",
        "size": size,
        "mtime_ns": st.st_mtime_ns,
        "mode": st.st_mode,
        "sampled": sampled,
        "sample_sha256": digest.hexdigest() if sampled else None,
    }


def capture_git_state(root: Path, deadline: float) -> dict[str, Any] | None:
    try:
        proc = run_git(root, ["status", "--porcelain=v1", "-z", "-b", "--untracked-files=all"], deadline)
    except RuntimeError:
        return None
    branch, paths = parse_porcelain_z(proc.stdout)
    paths = {rel: status for rel, status in paths.items() if not (rel == ".claude/state" or rel.startswith(".claude/state/"))}
    if len(paths) > MAX_DIRTY_PATHS:
        raise RuntimeError(f"dirty path count {len(paths)} exceeds bounded snapshot limit {MAX_DIRTY_PATHS}")
    head_proc = run_git(root, ["rev-parse", "--verify", "HEAD"], deadline, text=True)
    head = head_proc.stdout.strip()
    budget = [MAX_SAMPLE_BYTES]
    entries: dict[str, Any] = {}
    for rel in sorted(paths):
        entries[rel] = {
            "status": paths[rel],
            "signature": bounded_file_signature(root / rel, budget),
        }
    payload = {"branch": branch, "head": head, "entries": entries}
    payload["fingerprint"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8", errors="surrogatepass")
    ).hexdigest()
    return payload


def state_dir(root: Path) -> Path:
    return root / ".claude" / "state"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def read_surface(root: Path) -> dict[str, Any] | None:
    path = state_dir(root) / "change-surface.json"
    if not path.is_file():
        return None
    state = read_json(path)
    if not state.get("active", False):
        return None
    if state.get("schema_version") != STATE_SCHEMA:
        raise ValueError("unsupported change-surface schema_version")
    for field in ("expected", "protected", "authorized_dirty"):
        value = state.get(field, [])
        if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
            raise ValueError(f"{field} must be a list of non-empty strings")
    for field in ("task_id", "baseline_id"):
        if not isinstance(state.get(field), str) or not state[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    return state


def read_baseline(root: Path) -> dict[str, Any]:
    path = state_dir(root) / "ownership-baseline.json"
    baseline = read_json(path)
    if baseline.get("schema_version") != BASELINE_SCHEMA:
        raise ValueError("unsupported ownership-baseline schema_version")
    for field in ("baseline_id", "repository_root", "baseline_head"):
        if not isinstance(baseline.get(field), str) or not baseline[field].strip():
            raise ValueError(f"baseline {field} must be a non-empty string")
    dirty = baseline.get("preexisting_dirty", [])
    if not isinstance(dirty, list) or not all(isinstance(x, str) and x for x in dirty):
        raise ValueError("baseline preexisting_dirty must be a list of non-empty strings")
    return baseline


def validate_binding(root: Path, surface: dict[str, Any], baseline: dict[str, Any], deadline: float) -> dict[str, Any]:
    if surface["baseline_id"] != baseline["baseline_id"]:
        raise ValueError("change surface is not bound to the ownership baseline")
    if canonical_root(baseline["repository_root"]) != canonical_root(root):
        raise ValueError("ownership baseline belongs to a different repository/worktree root")
    current = capture_git_state(root, deadline)
    if current is None:
        raise ValueError("active change surface requires a Git worktree")
    if current["head"] != baseline["baseline_head"]:
        raise ValueError("baseline HEAD diverged; perform fresh reconnaissance and reinitialize task state")
    baseline_branch = baseline.get("branch")
    if baseline_branch and current.get("branch") and current["branch"] != baseline_branch:
        raise ValueError("baseline branch diverged; perform fresh reconnaissance and reinitialize task state")
    return current


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def validate_checks(checks: Any, baseline_id: str, current: dict[str, Any]) -> None:
    """Validate execution records; this is not an authentication boundary."""
    if not isinstance(checks, list) or not checks or len(checks) > 64:
        raise ValueError("verification requires 1-64 executed checks")
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("check must be a structured execution record")
        argv = check.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            raise ValueError("check requires command arguments")
        if type(check.get("exit_code")) is not int or check["exit_code"] != 0 or check.get("timed_out") is not False:
            raise ValueError("failed or timed-out check cannot support verification")
        if check.get("baseline_id") != baseline_id or check.get("head") != current["head"]:
            raise ValueError("check belongs to a different baseline/HEAD")
        if check.get("before_fingerprint") != current["fingerprint"] or check.get("after_fingerprint") != current["fingerprint"]:
            raise ValueError("check is stale or changed the working state")
        for field in ("criterion", "started_at", "finished_at"):
            if not isinstance(check.get(field), str) or not check[field].strip():
                raise ValueError(f"check requires {field}")
