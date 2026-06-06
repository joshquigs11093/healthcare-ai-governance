# Security Policy

## Reporting a vulnerability

Please report security issues **privately**. Do not open a public issue for a
vulnerability.

- Use GitHub's **[private vulnerability reporting](https://github.com/joshquigs11093/healthcare-ai-governance/security/advisories/new)**
  ("Report a vulnerability" under the Security tab), or
- Open a minimal GitHub issue asking for a private channel, without details.

Please include enough information to reproduce: affected component, version/commit,
steps, and impact. We aim to acknowledge reports within a few days. As a personal,
best-effort open-source project there is no formal SLA, but credible reports will
be taken seriously.

## Scope

This is a **reference implementation**, not a production system. The most relevant
security considerations:

- **No real PHI.** All data in this repository is synthetic/fictional. Do not
  commit real protected health information. If you find any, report it privately.
- **PHI detection is best-effort.** The output auditor's PHI check uses
  open-source Presidio plus custom recognizers and is *not* a guaranteed
  de-identification tool (see [ADR-005](docs/decisions/005-presidio-and-its-limits.md)).
  Do not rely on it as the sole control for production de-identification.
- **The document "signature" is tamper-evidence, not authentication** — a SHA-256
  content hash, not a cryptographic signature (see
  [ADR-006](docs/decisions/006-content-hash-signing.md)).
- **Secrets.** API keys are read from environment variables and must never be
  committed. `.env` is gitignored.

## Supported versions

The latest commit on `main` is the supported version. There are no long-term
support branches.
