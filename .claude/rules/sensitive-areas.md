---
paths:
  - "**/package.json"
  - "**/package-lock.json"
  - "**/pnpm-lock.yaml"
  - "**/yarn.lock"
  - "**/pyproject.toml"
  - "**/uv.lock"
  - "**/requirements*.txt"
  - "**/Cargo.toml"
  - "**/Cargo.lock"
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - ".github/workflows/**"
  - "**/migrations/**"
  - "**/infra/**"
  - "**/terraform/**"
  - "**/*.tf"
---

# Sensitive change areas

These files often change dependency, build, deployment, schema, or infrastructure behavior.

- Identify the canonical source before editing generated/lock artifacts.
- Do not add or materially upgrade runtime dependencies without explicit or standing authorization.
- For migrations, distinguish additive/reversible local changes from destructive or production-data effects; consequential migrations require user authorization.
- For CI/deployment/infrastructure changes, verify syntax and the narrowest safe local/static checks available. Do not infer production success from configuration validity.
- Keep secrets and credentials out of repository configuration and logs.
- Explain externally consequential effects before requesting authorization; do not route around denied effects.
