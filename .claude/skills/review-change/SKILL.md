---
name: "review-change"
description: "Runs an independent fresh-context review of the actual current repository change for correctness, security, regression, test-quality, and scope problems."
when_to_use: "Use only after an implementation diff exists and before final verification; not for design review or speculative code that has not been changed."
argument-hint: "[objective, acceptance criteria, and intentional scope]"
allowed-tools:
  - "Bash(git status --short)"
  - "Bash(git diff --stat --no-ext-diff)"
  - "Bash(git diff --name-only --no-ext-diff)"
  - "Bash(git diff --cached --name-only --no-ext-diff)"
  - "PowerShell(git status --short)"
  - "PowerShell(git diff --stat --no-ext-diff)"
  - "PowerShell(git diff --name-only --no-ext-diff)"
  - "PowerShell(git diff --cached --name-only --no-ext-diff)"
context: "fork"
agent: "code-reviewer"
background: false
compatibility: "Targets Claude Code v2.1.218+, Git, and the custom code-reviewer subagent."
---
# Review current change

Independently review the current repository change for this task:

$ARGUMENTS

Start from bounded Git evidence instead of front-loading the entire diff.

## Working-tree status

!`git status --short`

## Changed-path summary

!`git diff --stat --no-ext-diff`

## Unstaged changed paths

!`git diff --name-only --no-ext-diff`

## Staged changed paths

!`git diff --cached --name-only --no-ext-diff`

You do not inherit the parent conversation. Use this summary plus repository read/search/navigation tools to retrieve complete relevant changed files and only the diff hunks needed to adjudicate correctness. For untracked paths named by status, read the relevant files directly.

Review against the supplied objective/acceptance criteria and repository rules. Prioritize correctness, security, regression risk, scope drift, broken contracts, and invalid tests. A style preference is not a blocker unless repository policy makes it one.

Do not edit files. If correctness depends on a current external API/library fact you cannot establish from repository evidence, mark that uncertainty explicitly so the parent can invoke `current-docs-research`.

## Handoff

End with:

- `status`: `PASS`, `CHANGES_REQUIRED`, or `BLOCKED`
- `blockers`: severity-ordered findings with concrete file/symbol evidence and smallest correction
- `non_blocking`: meaningful observations only
- `scope`: whether the actual diff matches the intentional change surface
- `uncertainty`: current-docs or runtime facts still unverified
- `next`: `verification-gate` when clear, otherwise `implementation-slice` or `current-docs-research`

The result binds only to the inspected current diff. Later substantive edits require renewed review of affected areas.
