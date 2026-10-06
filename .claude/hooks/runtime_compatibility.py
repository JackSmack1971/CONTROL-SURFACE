"""Content-bound diagnostic evidence; this is not authorization or attestation."""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import re

SURFACES = ("permissions", "PreToolUse", "PostToolUse", "SessionStart", "Stop",
            "instruction_symlink_denied", "codex_claude_boundary")


def binding(root: Path, version: str | None) -> dict:
    """Hash bytes and link identity, excluding generated state and bytecode."""
    paths = set()
    for name in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".mcp.json"):
        if (root / name).exists() or (root / name).is_symlink():
            paths.add(root / name)
    base = root / ".claude"
    if base.exists():
        for path in base.rglob("*"):
            relative = path.relative_to(base)
            if relative.parts[0] in {"state", "selftest"} or "__pycache__" in relative.parts:
                continue
            if path.is_symlink() and path.is_dir():
                raise ValueError("directory symlinks cannot be completely inventoried")
            if path.is_file() or path.is_symlink():
                paths.add(path)
    hashes = {}
    for path in sorted(paths):
        content = path.read_bytes()
        if path.is_symlink():
            content = b"symlink\0" + str(path.readlink()).encode("utf-8") + b"\0" + content
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(content).hexdigest()
    return {"claude_code_version": version, "platform": platform.platform(),
            "files_sha256": hashes}


def compatibility(root: Path, version: str | None) -> dict:
    path = root / ".claude/state/runtime-validation.json"
    if not path.exists():
        return {"status": "missing", "reasons": ["runtime-validation.json is absent"]}
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        if evidence["schema_version"] != 2:
            raise ValueError("expected evidence schema_version 2; rerun validation")
        tested = evidence["binding"]
        if not isinstance(tested["claude_code_version"], str) or not tested["claude_code_version"]:
            raise ValueError("missing tested CLI version")
        if not isinstance(tested["platform"], str) or not tested["platform"]:
            raise ValueError("missing tested platform")
        hashes = tested["files_sha256"]
        if not isinstance(hashes, dict) or not hashes or any(
            not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
            for k, v in hashes.items()
        ):
            raise ValueError("invalid complete SHA-256 inventory")
        timestamp = datetime.fromisoformat(evidence["validated_at"].replace("Z", "+00:00"))
        if timestamp.utcoffset() is None:
            raise ValueError("validated_at must include timezone")
        if any(evidence["surfaces"].get(surface) != "pass" for surface in SURFACES):
            raise ValueError("required live surfaces have not all passed")
        current = binding(root, version)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {"status": "invalid", "reasons": [str(exc)]}
    reasons = []
    for key in ("claude_code_version", "platform"):
        if current[key] != tested[key] or current[key] is None:
            reasons.append(key + " differs or is unavailable")
    changed = sorted(k for k in hashes.keys() | current["files_sha256"].keys()
                     if hashes.get(k) != current["files_sha256"].get(k))
    if changed:
        reasons.append("control files changed: " + ", ".join(changed))
    return {"status": "stale" if reasons else "verified", "reasons": reasons,
            "validated_at": evidence["validated_at"]}
