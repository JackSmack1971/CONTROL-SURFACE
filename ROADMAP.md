# Control-plane improvement roadmap

**Status:** decision artifact only. This roadmap does not authorize implementation. The source register is `SYNTHESIS-BARRIER.md`; candidate IDs below refer to that file. All candidate decisions were reviewed by four independent read-only lanes and then adjudicated against repository evidence and current official Claude Code documentation. Reviewer agreement is evidence, not a vote.

## Evidence boundary

- **CURRENT:** repository `HEAD` is `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`; branch is `main`. At review start, the worktree had pre-existing untracked `READ-ONLY-RECON.md` and `SYNTHESIS-BARRIER.md`. Neither was edited.
- **CURRENT:** `claude --version` reports `2.1.290`. This identifies the binary only; it does not verify settings, hook delivery, payloads, or instruction selection.
- **CURRENT:** `python .claude/bin/statectl.py status` fails with `baseline HEAD diverged`. The ignored task state is stale and was not refreshed or treated as verified.
- **CURRENT:** no self-tests or live Claude canaries were run for this review. No runtime behavior is claimed as verified for 2.1.290.
- **CURRENT, documented:** the official [Claude Code Hooks reference](https://code.claude.com/docs/en/hooks) documents `PostToolUseFailure`, `PostToolBatch`, and `InstructionsLoaded`; it describes `PostToolUseFailure` as applying after a tool fails, and excludes failures before execution such as permission denials and schema rejection. It describes `InstructionsLoaded` as event-based observability, not enforcement. These are current docs, not evidence that this binary delivered those events in this project.
- **CURRENT, repository:** `.claude/RUNTIME-VALIDATION.md` already specifies disposable live canaries and a version-bound `runtime-validation.json` evidence record. The record is absent in the evidence captured by `SYNTHESIS-BARRIER.md`.

## Adjudication summary

Verdicts are independent reviewer classifications: **A** Architecture, **P** Product contract, **M** Minimalist, **V** Verifier. The primary decision follows the table and is not a majority tally.

| ID | A | P | M | V | Primary adjudication |
|---|---|---|---|---|---|
| C01 | REVISE | ACCEPT | ACCEPT | ACCEPT | **DEFER / DECISION REQUIRED.** The split authority update is a real defect, but the transaction, locking, task identity, and interrupted-recovery design is unresolved. Select the smallest coherent state protocol before scheduling implementation. |
| C02 | ACCEPT | ACCEPT | ACCEPT | ACCEPT | **ROADMAP.** A direct producer/consumer mismatch is evidenced and has a deterministic fixture matrix. |
| C03 | ACCEPT | REVISE | REVISE | REVISE | **ROADMAP, BOUNDED.** Reuse the existing audit for failed *started* shell executions only; treat missing evidence as incomplete. Canary the exact runtime first. Do not promise coverage for denied or pre-execution-rejected calls. |
| C04 | REVISE | ACCEPT | NEEDS EXPERIMENT | ACCEPT | **EXPERIMENT / DECISION REQUIRED.** Root selection mismatch is plausible, but universal Git-root equality could break nested projects and worktrees. Reproduce and define mismatch policy first. |
| C05 | REVISE | REVISE | REVISE | NEEDS EXPERIMENT | **OPEN ARCHITECTURAL DECISION.** Choose whether startup health is diagnostic or a completion precondition. Do not add session identity machinery until a reliable key and intended invariant are established. |
| C06 | ACCEPT (conditional) | ACCEPT | NEEDS EXPERIMENT | ACCEPT (conditional) | **EXPERIMENT.** Preserve raw path identity only if POSIX/WSL is a supported or claimed target and a collision fixture demonstrates exposure. |
| C07 | ACCEPT | ACCEPT | ACCEPT | REVISE | **ROADMAP, NARROW.** Remove true duplicate procedure from always-loaded instructions while preserving universal triggers/invariants; require checklist and route-quality evidence, not token savings alone. |
| C08 | REVISE | ACCEPT | REVISE | NEEDS EXPERIMENT | **DEFER / EXPERIMENT.** Existing kernel, workflow, and implementation-slice layers have distinct purposes. Identify exact contradictory duplication and establish a blinded baseline before deleting routing text. |
| C09 | REJECT | ACCEPT | REJECT | REVISE | **REJECT broad derivation/registry proposal.** The overlap has not caused a demonstrated damaging drift incident; the inventories serve different contracts. Repair a specific inconsistency if one is observed. |
| C10 | NEEDS EXPERIMENT | ACCEPT (qualified) | REJECT | NEEDS EXPERIMENT | **REJECT always-on project telemetry for now.** `InstructionsLoaded` is partial observability and cannot be a complete effective-instructions inventory. Use a one-off native canary if a concrete diagnostic need arises. |
| C11 | NEEDS EXPERIMENT | REVISE | NEEDS EXPERIMENT | NEEDS EXPERIMENT | **EXPERIMENT ONLY.** Reproduce false alerts or attribution gaps under parallel calls before adding batch lifecycle state. Current docs offer a post-batch event, not a batch-start event. |
| C12 | ACCEPT | ACCEPT | REVISE | ACCEPT | **ROADMAP, USING EXISTING CONTRACT.** Execute and retain the canary record already specified in `.claude/RUNTIME-VALIDATION.md`; do not build a new ledger framework first. Bind each result to version, platform, timestamp, and tested cases. |
| C13 | NEEDS EXPERIMENT | NEEDS EXPERIMENT / REVISE | REJECT | NEEDS EXPERIMENT | **DEFER.** No recurring measured workload is established, and “dynamic workflows” is not a precise product contract. Name a specific supported capability and benchmark a representative workload before reconsidering. |
| C14 | REVISE | ACCEPT | REVISE | REVISE | **DEFER.** Resume context already labels cached state as data-only; demonstrate that stale content is mistaken for current evidence before adding fingerprint work. |
| C15 | REVISE | ACCEPT | REVISE | REVISE | **MERGE INTO C12.** Bind evidence to the platform actually tested; do not create a parallel platform matrix or imply untested parity. |
| C16 | REJECT as artifact; accept as principle | ACCEPT | ACCEPT | ACCEPT as gate | **RETAIN AS A REVIEW CONSTRAINT.** No new policy artifact. Require a distinct uncovered failure mode and exact-version canary before adding a hook. |
| C17 | REJECT implementation | ACCEPT | ACCEPT | ACCEPT | **RETAIN AS A THREAT-MODEL CONSTRAINT.** No MAC/seal implementation while data and key share the same mutable trust boundary. |
| C18 | REJECT implementation | ACCEPT | ACCEPT | ACCEPT | **KEEP CURRENT DEFAULT.** Existing policy already favors one implementation owner and isolates concurrent writers; no measured peer-write workload justifies more machinery. |
| C19 | REJECT implementation | ACCEPT | ACCEPT | ACCEPT | **KEEP CURRENT BOUNDARY.** Existing policy already treats regexes as defense in depth. Do not broaden patterns as a claim of host containment. |

## Ordered roadmap

Only the following bounded slices advance. An implementation phase must still revalidate the baseline and execute its stated checks. A roadmap entry is not runtime evidence and does not authorize implementation.

### R1 — Establish exact-version runtime evidence (C12, C15)

- **Problem:** Structural self-tests cannot establish whether Claude Code accepts this project configuration, fires the configured hooks, or reports the expected runtime behavior. The repository prescribes canaries but no current result is retained.
- **Evidence:** `.claude/RUNTIME-VALIDATION.md:1-14, 27-50` describes the procedure and record; `.claude/MANIFEST.json` distinguishes runtime validation from structural checks; `SYNTHESIS-BARRIER.md` records no canary and no evidence artifact. Installed CLI reports 2.1.290.
- **Exact scope:** Run the already documented disposable canary for the claimed platform/version; retain its existing evidence record with version, platform/OS, Python/Git versions, timestamp, cases, outcomes, and limitations. Mark every unrun case/platform `UNVERIFIED`. Do not add a general telemetry service or claim untested combinations.
- **Files likely affected:** `.claude/state/runtime-validation.json` (ignored runtime evidence); only if the existing record format cannot represent observed facts, a narrowly scoped update to `.claude/RUNTIME-VALIDATION.md` and its validator.
- **Dependencies:** None. Use a disposable repository as required by the existing validation procedure.
- **Owner:** Control-plane maintainer; runtime canary operator records observed evidence.
- **Acceptance criteria:** Every claimed case has an observed outcome tied to `claude --version` and platform; failed/unrun cases remain explicit; missing, expired, wrong-version, or wrong-platform evidence cannot be labeled pass; no claim exceeds the cases run.
- **Verification strategy:** Follow `.claude/RUNTIME-VALIDATION.md`; inspect the retained record and run its evidence validator. Keep the live transcript/observations for the disposable canary. The version query alone is not a pass.
- **Risk:** Low for a bounded disposable canary; medium if effective local/managed settings or external environment are inadvertently included in the claim.
- **Rollback:** Remove or mark the evidence record obsolete and revert any narrow validator/documentation edit. Do not convert a failed observation into a passing result.
- **Why first:** Establishes the actual runtime/platform evidence baseline needed before event-dependent slices; also prevents Windows or other platform claims from being inferred from another host.

### R2 — Compare every captured Git state dimension (C02)

- **Problem:** Snapshot/fingerprint production records HEAD, index, and worktree state, while post-tool drift reporting compares worktree entries only. An index-only or HEAD-only delta can therefore escape the reported comparison.
- **Evidence:** `.claude/hooks/control_common.py` snapshot/fingerprint functions; `.claude/hooks/posttool_scope_audit.py` changed-path calculation; `.claude/selftest/selftest.py:385-405` already exercises index changes while status entries remain equal. Candidate details and source references are in `SYNTHESIS-BARRIER.md` C02.
- **Exact scope:** Use one shared classifier for the captured HEAD, index, and worktree dimensions; report which dimension changed and whether affected paths/commit deltas are in expected or protected scope. Specify intended staging/commit transitions. Do not redesign task state or add a new audit subsystem.
- **Files likely affected:** `.claude/hooks/control_common.py`, `.claude/hooks/posttool_scope_audit.py`, `.claude/selftest/selftest.py`.
- **Dependencies:** R1 is useful for an exact runtime compatibility claim; local algorithm correctness can be verified independently with temporary Git repositories.
- **Owner:** Hook/governance maintainer.
- **Acceptance criteria:** Fixtures classify worktree-only, index-only, HEAD-only, rename, mode, and combined changes; expected dimension and scope are correct; no protected delta is silent; legitimate staged/committed flows have explicit expected outcomes.
- **Verification strategy:** Add/use temporary Git repository matrix; run focused self-tests and the repository control-plane checks for changed hook code; inspect `git diff --check` and final diff. Any claim that Claude invoked the hook requires R1 canary evidence.
- **Risk:** Medium: legitimate staging/commit operations may produce noise if metadata transitions are not specified.
- **Rollback:** Revert the shared classification change and focused tests together; prior worktree-only audit behavior is restored.
- **Why second:** This is a directly demonstrated local correctness gap with deterministic tests and no unresolved product-policy choice. It improves the evidence consumed by subsequent audit work.

### R3 — Audit failed started shell calls and expose missing evidence (C03)

- **Problem:** The configured shell audit runs on `PostToolUse`; a shell call that fails after partial effects can escape this success-path comparison. Missing/malformed snapshots currently return quietly, which is indistinguishable from no recorded change.
- **Evidence:** `.claude/settings.json:203-213` binds the existing success event; `.claude/hooks/posttool_scope_audit.py:30-60` reads and compares snapshots and silently returns for absent/invalid evidence. Current official docs list `PostToolUseFailure` for failed calls but exclude denials and pre-execution validation failures. See the official [Hooks reference](https://code.claude.com/docs/en/hooks#posttoolusefailure).
- **Exact scope:** First make active-task missing/malformed audit evidence explicitly incomplete/diagnostic. Reuse the comparison from R2 for failed *started* Bash/PowerShell calls if the R1 disposable canary confirms the event, matcher, payload, and hook behavior in 2.1.290. Do not imply rollback, universal failed-attempt coverage, or host containment.
- **Files likely affected:** `.claude/settings.json`, `.claude/hooks/posttool_scope_audit.py`, `.claude/selftest/selftest.py`, and possibly `.claude/RUNTIME-VALIDATION.md` to record the new observed case.
- **Dependencies:** R2 shared state classifier; R1 exact-version failed-call canary and event contract.
- **Owner:** Hook/policy maintainer.
- **Acceptance criteria:** Missing/malformed evidence is distinguishable from a clean comparison during active task state; a failed started command that leaves an out-of-scope delta is surfaced; failed no-op does not create a false scope alert; denials/schema rejection behavior matches observed documented exclusions; no assertion of rollback.
- **Verification strategy:** Direct fixtures for missing/malformed/inactive state plus R1 disposable live cases: partial mutation then failure, no-op failure, permission denial, and schema rejection. Preserve observed payload/version with the evidence record.
- **Risk:** Medium: hook invocation ordering, duplicate events, missing tool-use IDs, and noisy concurrent changes.
- **Rollback:** Remove the additive failure-event binding and focused behavior while retaining the previously configured success audit; revert any evidence-format addition.
- **Why third:** It depends on reliable dimension comparison and exact runtime evidence, and is additive to the current hook surface. Its narrower event scope avoids overstating product semantics.

### R4 — Remove duplicated reconnaissance procedure from the kernel (C07)

- **Problem:** `CLAUDE.md` carries a detailed nontrivial-write checklist and task-state procedure that overlaps `.claude/skills/recon-gate/SKILL.md`, charging all sessions for phase-specific procedure.
- **Evidence:** `CLAUDE.md` sections “Evidence before nontrivial writes” and task authority; `.claude/skills/recon-gate/SKILL.md`; `READ-ONLY-RECON.md` estimates a potential 250–350 heuristic-token reduction. The estimate is not a measured behavioral improvement.
- **Exact scope:** Keep a concise universal trigger, preservation rule, and critical evidence/authority invariants in `CLAUDE.md`; remove only duplicated sequencing and statectl steps that remain discoverable in `recon-gate`. Do not weaken the workflow or move all guidance to an automatically assumed skill load.
- **Files likely affected:** `CLAUDE.md`, `.claude/skills/recon-gate/SKILL.md`, and a small fixed routing/checklist evaluation fixture if none already covers these cases.
- **Dependencies:** None. R1 is not a runtime prerequisite for text simplification, but routing claims require their own evaluation.
- **Owner:** Definition-plane maintainer.
- **Acceptance criteria:** Always-loaded instruction size falls by a recorded amount; the skill retains every required checklist step; a fixed blinded set covering read-only, trivial-write, and nontrivial-write requests does not lose a required route or invariant and does not introduce extra process for the first two cases.
- **Verification strategy:** Compare exact bytes/characters or token count using the same tokenizer; inspect retained skill procedure; run fixed, independently scored routing cases before/after. If only size improves but route quality is unknown or regresses, do not accept.
- **Risk:** Low to medium: a consequential checklist may be missed if the trigger or skill discoverability is weakened.
- **Rollback:** Restore the removed kernel text while retaining the evaluation fixture.
- **Why fourth:** It is a reversible context simplification with lower direct operational risk than hook/state changes. It follows the reliability work so it does not distract from observed audit gaps.

### R5 — Recover and diagnose stale task authority (C01, new live-session evidence)

- **Problem:** A changed HEAD makes active task authority stale, but the current binding check also appears to reject the normal recovery command. In the reported live session, ordinary shell inspection was blocked as well, leaving no clear way to diagnose the state before deciding whether to reinitialize. This is a recovery and diagnosis gap beyond C01's split-write transaction defect.
- **Evidence:** **USER-REPORTED:** the live session reproduced the stale-HEAD condition, blocked ordinary shell inspection, and found the apparent recovery path subject to the stale check. **CURRENT, repository:** `validate_binding` rejects a divergent HEAD with a fresh-reconnaissance/reinitialize message; `statectl.py status` calls that validator; `update-scope` also validates before writing. `pretool_guard.py` allows commands recognized as `statectl.py` through its command guard, but that allowance does not bypass validation inside the command. Exact Claude hook delivery and runtime interaction remain unverified by this evidence.
- **Exact scope:** First reproduce the precise case in a disposable repository: initialize task state, change HEAD, then attempt supported read-only Git/state inspection and each proposed recovery action. Define a bounded recovery transition that permits enough read-only diagnosis, requires fresh reconnaissance and explicit user approval before changing active authority, invalidates prior verification/check evidence, and records the transition. Recovery must not silently update the old baseline, preserve the old task's authority, or treat stale `VERIFIED` state as current. Keep diagnosis available even when mutation/recovery is denied. Do not select a lock/journal/session-identity architecture until the fixtures show it is needed.
- **Files likely affected:** `.claude/bin/statectl.py`, `.claude/hooks/control_common.py`, `.claude/hooks/pretool_guard.py`, `.claude/hooks/change_surface_guard.py`, `.claude/hooks/completion_gate.py`, `.claude/selftest/selftest.py`, and narrowly scoped task-state documentation. Actual scope depends on the selected transition contract.
- **Dependencies:** None for reproducing local logic. R1 is required before claiming Claude Code hook/runtime behavior. C01's paired-write/concurrency design remains a related but separable decision; avoid folding it into this recovery slice absent a demonstrated dependency.
- **Owner:** Task-state/governance maintainer.
- **Acceptance criteria:** In the exact stale-HEAD fixture, read-only status and Git inspection have an explicit, tested policy and expose enough evidence to decide next steps; state-changing commands remain blocked until fresh reconnaissance and an explicit approval transition; approval is bound to the observed current repository state and intended task; old verification and check evidence cannot satisfy completion; no recovery invocation silently rebinds the previous authority; interrupted recovery leaves a diagnosable state and does not produce active authority without the approved transition.
- **Verification strategy:** Use disposable temporary Git repositories and preserve the stale state fixture. Exercise `status`, read-only Git commands through the configured guard, `update-scope`, `init`, and the selected recovery path against changed HEAD; inspect all state/evidence before and after. Include denied/no-approval, approval against changed state, interrupted transition, and post-recovery completion cases. Then run focused self-tests and the relevant exact-version disposable Claude canary before claiming the hook path works. Do not alter this checkout's ignored stale task state to run the fixture.
- **Risk:** Medium to high: an overly broad bypass can turn recovery into silent authority reset, while a fully fail-closed path can prevent diagnosis and strand users. Explicitly distinguish read-only diagnostics, authorization, approval, and execution.
- **Rollback:** Revert the recovery transition and its tests together; stale state remains blocked and must be handled through a documented manual process until a replacement is designed. Never restore old verification as current.
- **Why next:** The live-session report adds a concrete operational dead end to C01's already evidenced task-state integrity problem. It warrants priority over the earlier mechanical skill-integrity idea because it can strand an active task and obscure whether old verification remains trusted. This entry advances recovery diagnosis and policy definition; it does not authorize implementation or resolve C01's full transaction model.

### R6 — Surface missing audit evidence during active task authority (C03, phase A split from R3)

- **Problem:** `posttool_scope_audit.py` exits silently when the pre-command snapshot is absent (`snapshot_path.is_file()` false) or when the payload lacks a `tool_use_id`. During active task authority that silence is indistinguishable from a clean comparison, so a shell effect can go unaudited without any signal.
- **Evidence:** **CURRENT, repository:** `.claude/hooks/posttool_scope_audit.py:36-45` returns exit 0 with no output for missing `tool_use_id` or missing snapshot; malformed snapshots already produce a block reason (lines 59-61). R2's shared classifier (`classify_git_state_changes`) is implemented, so R3's comparison dependency is met. R3's failure-event half still depends on R1; this missing-evidence half does not.
- **Exact scope:** When task authority is active, report a missing snapshot or missing `tool_use_id` as explicitly incomplete audit evidence (diagnostic reason, not a silent pass). When no task authority is active, keep the current silent exit. Do not add the `PostToolUseFailure` binding here; that remains R3 after R1.
- **Files likely affected:** `.claude/hooks/posttool_scope_audit.py`, `.claude/selftest/selftest.py`.
- **Dependencies:** None for local logic. Claims that Claude Code delivers this path at runtime still require R1.
- **Owner:** Hook/policy maintainer.
- **Acceptance criteria:** Fixtures cover active + missing snapshot, active + missing `tool_use_id`, active + malformed snapshot, inactive + missing snapshot, and active + clean comparison; only the active-incomplete cases emit an incomplete-evidence reason; the clean and inactive cases stay silent.
- **Verification strategy:** Direct hook invocation fixtures in temporary Git repositories; `python .claude/selftest/selftest.py` and `python .claude/selftest/metrics.py`; inspect final diff.
- **Risk:** Low to medium: snapshot races or legitimately skipped pre-hooks could create noise; the fixture set must include the inactive case to avoid alerting outside governed tasks.
- **Rollback:** Revert the hook branch and its fixtures together; prior silent behavior returns.
- **Why next:** R2 and R5 have landed. R1 remains the top priority but needs a live canary operator in the exact binary; R6 is the highest-value slice that can be implemented and verified offline today, and it narrows R3 to its runtime-dependent remainder.

## Progress (as of 2026-10-06)

- **R2 — implemented** in `6210e71` (shared HEAD/index/worktree classifier used by `posttool_scope_audit.py`).
- **R5 — implemented** in `8293767`, `a44bd6e`, `e256a64` (stale-authority recovery, bounded diagnostics, prompt before deactivation).
- **R1 — open.** `.claude/state/runtime-validation.json` is absent; SessionStart reports runtime compatibility `missing`. Requires a live canary run, not offline work.
- **R3 — open, narrowed.** Missing-evidence handling split into R6; the `PostToolUseFailure` binding remains blocked on R1.
- **R4 — open.**
- **Recommended order now:** R1 (when a canary operator is available) and R6 (offline) in parallel, then R3, then R4.

## Deferred ideas

- **C08 — Lifecycle routing ownership:** defer pending a fixed blind routing evaluation and an exact map of genuinely contradictory duplicate statements. Preserve the distinct purposes of kernel routing, multi-stage workflow, and bounded implementation.
- **C14 — Resume freshness presentation:** defer until a reproduced case shows historical `DATA ONLY` context was mistaken for current evidence. Do not duplicate completion-gate hashing in a resume hook without evidence of need.
- **C15 — Platform support claims:** merged into R1. Do not create a second platform ledger.
- **C16–C19 — Negative decisions:** retain as constraints in review, not roadmap implementation tasks; see below.

## Rejected ideas + why

- **C09 — Universal derived inventory/registry:** reject the broad abstraction. The sources have different contracts, and no harmful drift incident is established. Fix a specific observed mismatch instead of adding a registry or broad discovery mechanism.
- **C10 — Always-on instruction-load telemetry:** reject for now. The documented event is partial observability and cannot represent a complete effective instruction set; runtime and AGENTS coverage boundaries make persistent telemetry easy to overclaim. Use the existing one-off canary process for a concrete question.
- **C13 — Enable dynamic workflows by default:** reject under current evidence. There is no recurring measured workload, and the candidate does not identify one precise Claude capability/product contract. Reopen only after a paired benchmark of a recurring broad read-heavy audit proves net benefit and equal coverage.
- **C16 — Add hooks for surface coverage:** no new subsystem or artifact. Keep the gate that each hook addresses a distinct uncovered failure mode and has a measurable test plus exact-version canary.
- **C17 — Add local MAC/cryptographic seals:** reject under the stated same-principal mutable-state model. Reopen only if a threat model supplies independent key custody.
- **C18 — Enable agent teams/concurrent worktree writers by default:** reject. Existing single-writer/read-specialist design fits observed work; no measured peer-write workload supports the added state and merge paths.
- **C19 — Broaden shell regexes as host containment:** reject. Pattern rules are request-level defense in depth; they cannot establish OS-level effect containment. Add a pattern only for a concrete tested request gap.

## Experiments needed

- **C04 — Root identity:** temporary parent/child repositories with distinct `.claude` state; vary event `cwd`, `CLAUDE_PROJECT_DIR`, Git top-level, worktree, symlink/junction. Require either the intended root or explicit mismatch, never silent use of another project’s state. Decide mismatch action only after observing legitimate layouts.
- **C06 — Path identity:** first state whether POSIX/WSL is in the supported/claimed platform set; then construct a POSIX Git repository with both `a/b` and `a\\b`. If they alias in scope accounting, narrowly preserve raw path identity; otherwise do not broaden path normalization machinery.
- **C08 — Route simplification:** fixed blinded cases across read-only, trivial, bug, feature, architecture, and end-to-end tasks; independently score correct route, omitted gates, and unnecessary steps before/after. No deletion based only on textual similarity.
- **C10 — One-off native observability check:** if a concrete support question arises, observe `InstructionsLoaded` on 2.1.290 for root instructions and a lazily activated path rule. Record known omissions, especially direct AGENTS.md configuration. Do not turn partial event data into persistent complete-policy telemetry.
- **C11 — Parallel audit race:** repeated controlled disjoint and overlapping calls; retain per-call snapshots, event timing, and resulting alerts. No batch logic unless a false alert or attribution gap reproduces. Any later design must acknowledge the documented lack of a pre-batch event.
- **C13 — Workload benchmark:** identify the exact capability first (e.g., bounded subagent orchestration, agent teams, or generated script); verify its availability/semantics in the target binary; compare against current capped fan-out on the same audit corpus for coverage, accuracy, source quality, coordinator tokens, latency, and recovery.

## Open architectural decisions

- **C01 — Task authority transaction model:** decide whether authority should be one atomically replaced document, a journaled transition, or another minimal single-owner protocol. Define duplicate-init behavior, concurrent mutator serialization, task identity versus Claude session identity, and safe interrupted-write recovery. Do not implement a lock/recovery framework before selecting this contract.
- **C04 — Root mismatch policy:** define which runtime root is authoritative, whether event `cwd` must be contained by it, and what an out-of-root event does. Git top-level should initially be diagnostic evidence rather than assumed equal to project root; validate nested project/worktree cases first.
- **C05 — Health semantics:** decide whether startup health is diagnostics only or a completion condition. If a completion condition, specify what makes evidence current and how absent/unhealthy records behave. SessionStart diagnostics are not a mechanism to prevent session startup; do not describe them as such.
