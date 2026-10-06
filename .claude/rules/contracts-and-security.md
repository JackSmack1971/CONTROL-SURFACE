---
paths:
  - "**/openapi*.yaml"
  - "**/openapi*.yml"
  - "**/openapi*.json"
  - "**/*.schema.json"
  - "**/schema/**"
  - "**/schemas/**"
  - "**/auth/**"
  - "**/security/**"
  - "**/permissions/**"
  - "**/migrations/**"
---

# Contracts and security boundaries

Treat public schemas, persisted data, authentication, authorization, and security controls as compatibility boundaries.

- Identify current producers, consumers, and migration/rollback implications before changing a contract.
- Do not silently weaken authentication, authorization, validation, encryption, or audit behavior to simplify implementation.
- Default to backward-compatible evolution unless a breaking change is explicitly requested and authorized.
- Verify framework/SDK security behavior against current primary documentation when version-sensitive.
- Do not inspect credentials to solve an authentication problem. Diagnose configuration shape, identity, scopes, or missing access without exposing secret material.
- Security recommendations do not grant authority to alter production policy or credentials.
