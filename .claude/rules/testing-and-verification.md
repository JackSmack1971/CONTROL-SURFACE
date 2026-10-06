---
paths:
  - "**/test/**"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/pytest.ini"
  - "**/pyproject.toml"
  - "**/jest.config.*"
  - "**/vitest.config.*"
  - "**/playwright.config.*"
---

# Testing and verification policy

Tests are evidence about behavior, not obstacles to make green.

- Preserve pre-existing tests unless requested behavior legitimately changes the contract.
- Never delete, skip, loosen, snapshot-overwrite, or rewrite a valid assertion merely to make a failing implementation pass.
- Prefer an oracle that is independent of the implementation under test. Avoid computing the expected result with the same production path being verified.
- Use mocks only where they isolate a real boundary; do not mock away the behavior the test claims to prove.
- For bug fixes, preserve a reproducible regression case when proportionate.
- For brownfield refactors with unclear behavior, characterization tests can preserve observed behavior before structural changes.
- A test passing proves only what its oracle and exercised path actually establish. Keep integration, platform, and production claims bounded to executed evidence.
