---
name: oracle-design
description: Derives an acceptance oracle from requirements and public interfaces before implementation, without inspecting implementation or existing test expectations.
argument-hint: "[requirements, public signatures, domain constraints, test-safe interfaces]"
context: fork
agent: verifier
---
# Requirements-derived oracle design

Design checks only; do not execute commands, inspect implementation or existing tests, or write files. This phase reuses the verifier role for requirements-only analysis, not post-implementation verification.

$ARGUMENTS

If requirements or public interfaces are insufficient, return NEEDS_INPUT with the exact ambiguity. Do not invent contracts or infer expected behavior from implementation. If implementation material was supplied, report contamination and request a fresh requirements-only invocation.

Return a compact acceptance matrix: criterion, authoritative requirement/source, representative inputs and expected outcomes, boundary/failure cases, check level, oracle rationale, and required environment. Distinguish normative acceptance from characterization of legacy behavior; characterization preserves observations and does not prove correctness.

Select the smallest credible strategy:
- Example/regression checks for concrete contracts; integration/E2E where real boundaries are the behavior under test.
- Property-based checks for independently justified domain invariants. Explain why each property follows from requirements; round-trip properties alone can share correlated defects.
- Differential checks only against an independently trusted reference.
- Mutation testing when surviving faults would materially undermine confidence and a repository-supported runner exists. Specify bounded targets, time budget, and survivor adjudication; equivalent mutants and timeouts are not automatically test defects. Do not invent a universal score or install a framework.
- Mocks only at genuine external boundaries; retain a check that exercises the claimed integration where practical.

Return status READY or NEEDS_INPUT, the matrix, assumptions, strategies selected/omitted with reasons, and unverified behavior. The implementation owner may turn this matrix into tests but must preserve requirement-derived expectations. Fresh context reduces correlation; it is not a security boundary or proof of independence.
