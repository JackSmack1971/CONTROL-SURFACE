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
FINGERPRINT_VERSION = 2
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


def complete_file_signature(path: Path, deadline: float) -> dict[str, Any]:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return {"kind": "missing"}
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if not path.is_file():
        raise ValueError(f"cannot fully hash non-file path: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            remaining(deadline)
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return {"kind": "file", "size": st.st_size, "mode": st.st_mode,
            "sha256": digest.hexdigest()}


def capture_git_state(root: Path, deadline: float, *, full_content: bool = False) -> dict[str, Any] | None:
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
            "signature": (complete_file_signature(root / rel, deadline) if full_content
                          else bounded_file_signature(root / rel, budget)),
        }
    # NUL-delimited records preserve paths (including tabs/newlines), modes,
    # blob identities and conflict stages without Git's display quoting.
    index = run_git(root, ["ls-files", "--stage", "-z"], deadline).stdout
    index_entries = []
    for record in index.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        rel = raw_path.decode("utf-8", errors="surrogateescape")
        if rel == ".claude/state" or rel.startswith(".claude/state/"):
            continue
        mode, blob, stage = metadata.decode("ascii").split()
        index_entries.append({"path": rel, "mode": mode, "blob": blob, "stage": stage})
    payload = {"fingerprint_version": FINGERPRINT_VERSION,
               "content_mode": "full" if full_content else "sampled",
               "branch": branch, "head": head, "entries": entries,
               "index": index_entries}
    payload["fingerprint"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8", errors="surrogatepass")
    ).hexdigest()
    return payload


def _changed_commit_paths(root: Path, before_head: str, after_head: str, deadline: float) -> list[str]:
    if before_head == after_head:
        return []
    raw = run_git(
        root,
        ["diff", "--name-status", "--find-renames", "-z", before_head, after_head, "--"],
        deadline,
    ).stdout
    records = raw.split(b"\0")
    paths: set[str] = set()
    index = 0
    while index < len(records):
        status = records[index]
        index += 1
        if not status:
            continue
        status_text = status.decode("ascii", errors="replace")
        count = 2 if status_text.startswith(("R", "C")) else 1
        for record in records[index:index + count]:
            if record:
                paths.add(record.decode("utf-8", errors="surrogateescape").replace("\\", "/"))
        index += count
    return sorted(paths)


def classify_git_state_changes(before: dict[str, Any], after: dict[str, Any], root: Path, deadline: float) -> dict[str, list[str]]:
    """Classify captured HEAD, index, and worktree deltas by affected path."""
    before_entries = before.get("entries", {})
    after_entries = after.get("entries", {})
    if not isinstance(before_entries, dict) or not isinstance(after_entries, dict):
        raise ValueError("captured worktree entries are invalid")

    before_index = before.get("index", [])
    after_index = after.get("index", [])
    if not isinstance(before_index, list) or not isinstance(after_index, list):
        raise ValueError("captured index entries are invalid")

    def by_path(entries: list[dict[str, Any]]) -> dict[str, tuple[tuple[str, str, str], ...]]:
        grouped: dict[str, list[tuple[str, str, str]]] = {}
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise ValueError("captured index entry is invalid")
            values = tuple(str(entry.get(field, "")) for field in ("mode", "blob", "stage"))
            grouped.setdefault(entry["path"], []).append(values)
        return {path: tuple(sorted(values)) for path, values in grouped.items()}

    old_index, new_index = by_path(before_index), by_path(after_index)
    index_paths = sorted(path for path in set(old_index) | set(new_index)
                         if old_index.get(path) != new_index.get(path))
    before_head, after_head = before.get("head"), after.get("head")
    if not isinstance(before_head, str) or not isinstance(after_head, str):
        raise ValueError("captured HEAD is invalid")
    head_paths = _changed_commit_paths(root, before_head, after_head, deadline)

    # Dirty paths already have a pre-command filesystem signature. For paths
    # that were clean, compare the post-command worktree directly with the old
    # HEAD so staging alone is not mislabeled as a worktree change.
    old_dirty = set(before_entries)
    candidates = set(old_dirty) | set(after_entries) | set(index_paths) | set(head_paths)
    worktree_paths: set[str] = set()
    current_budget = [MAX_SAMPLE_BYTES]
    for path in sorted(old_dirty):
        current_signature = bounded_file_signature(root / path, current_budget)
        if before_entries[path].get("signature") != current_signature:
            worktree_paths.add(path)

    clean_before_candidates = candidates - old_dirty
    old_index_paths = set(old_index)
    filemode = False
    if clean_before_candidates:
        filemode_result = subprocess.run(
            ["git", "-C", str(root), "config", "--bool", "core.filemode"],
            capture_output=True, text=True, check=False, timeout=remaining(deadline),
        )
        if filemode_result.returncode not in (0, 1):
            raise RuntimeError((filemode_result.stderr or "could not read core.filemode").strip())
        filemode = (filemode_result.stdout.strip().lower() == "true" if filemode_result.returncode == 0
                    else os.name != "nt")

    for path in sorted(clean_before_candidates):
        prior_entries = old_index.get(path, ())
        prior = next((entry for entry in prior_entries if entry[2] == "0"), None)
        target = root / path
        if prior is None:
            worktree_paths.add(path)
            continue
        if prior[0] == "120000":
            if not target.is_symlink():
                worktree_paths.add(path)
                continue
            link_target = os.readlink(target).encode("utf-8", errors="surrogateescape")
            current_blob = subprocess.run(
                ["git", "-C", str(root), "hash-object", "--stdin"],
                input=link_target, capture_output=True, text=False, check=False,
                timeout=remaining(deadline),
            )
            if current_blob.returncode != 0:
                raise RuntimeError(current_blob.stderr.decode("utf-8", errors="replace").strip())
            current_blob_id = current_blob.stdout.decode("ascii", errors="replace").strip()
        elif prior[0] == "160000":
            if not target.is_dir():
                worktree_paths.add(path)
                continue
            current_commit = subprocess.run(
                ["git", "-C", str(target), "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, check=False, timeout=remaining(deadline),
            )
            if current_commit.returncode != 0:
                raise RuntimeError((current_commit.stderr or "submodule HEAD unavailable").strip())
            current_blob_id = current_commit.stdout.strip()
        elif target.is_file() and not target.is_symlink():
            current_blob_id = run_git(
                root, ["hash-object", "--path=" + path, str(target)], deadline, text=True
            ).stdout.strip()
        else:
            worktree_paths.add(path)
            continue
        if current_blob_id != prior[1]:
            worktree_paths.add(path)
            continue
        if filemode and prior[0] in {"100644", "100755"}:
            current_executable = bool(target.stat().st_mode & 0o111)
            indexed_executable = prior[0] == "100755"
            if current_executable != indexed_executable:
                worktree_paths.add(path)

    for path in set(after_entries) - old_dirty - old_index_paths:
        # A newly visible untracked/staged-add path had no prior tracked entry.
        worktree_paths.add(path)
    return {
        "HEAD": head_paths,
        "index": index_paths,
        "worktree": sorted(worktree_paths),
    }


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


def validate_binding(root: Path, surface: dict[str, Any], baseline: dict[str, Any], deadline: float, *, full_content: bool = False) -> dict[str, Any]:
    if surface["baseline_id"] != baseline["baseline_id"]:
        raise ValueError("change surface is not bound to the ownership baseline")
    if canonical_root(baseline["repository_root"]) != canonical_root(root):
        raise ValueError("ownership baseline belongs to a different repository/worktree root")
    current = capture_git_state(root, deadline, full_content=full_content)
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
        if check.get("fingerprint_version") != FINGERPRINT_VERSION or current.get("content_mode") != "full":
            raise ValueError("unsupported verification fingerprint format; rerun checks and reseal")
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
