"""Exact package preapproval policy, distinct from runtime authorization."""
import re


def preapprovals_match(path, manifest):
    frontmatter = path.read_text(encoding="utf-8").split("---", 2)[1]
    match = re.search(r"(?m)^allowed-tools:\s*\n((?:  - .*\n)+)", frontmatter)
    if "allowed-tools:" in frontmatter and not match:
        return False
    actual = [x.strip().strip('"') for x in re.findall(r"(?m)^  - (.*)$", match.group(1))] if match else []
    expected = manifest.get("skill_tool_preapprovals", {}).get(path.parent.name, [])
    return sorted(actual) == sorted(expected) and len(actual) == len(set(actual)) and all(
        re.fullmatch(r"(?:Skill|Bash|PowerShell)\([^\n]+\)", x) for x in actual
    )
