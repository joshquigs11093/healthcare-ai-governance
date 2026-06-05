# ADR-001: Leader-facing framing

**Status:** Accepted

## Context

The toolkit has two distinct audiences: governance leadership (CDOs, CMIOs, AI
governance committees) who decide *whether and how* to deploy AI, and ML
engineers who *produce* the artifacts. These audiences want different things from
the same repository. Leaders want to understand the program, see the portfolio,
and read a board report; engineers want CLIs, schemas, and tests. A project that
leads with engineering detail risks being unreadable to the people who actually
own AI governance.

## Decision

Prioritize the governance-leadership audience in the headline presentation. The
README, the primer, the dashboard, and the board report speak to leaders first
and assume no machine-learning background. Engineering documentation
(PRACTITIONERS.md, module docstrings, schemas) is one click deeper, not on the
front page.

## Alternatives considered

- **Engineer-first framing.** Lead with the CLI and library API. Rejected: it
  matches most open-source norms but alienates the primary decision-making
  audience and undersells the governance value.
- **Two separate projects.** Split a "for leaders" repo from a "for engineers"
  repo. Rejected: duplicates the inventory and artifacts, which are the shared
  source of truth; the integration is the point.

## Consequences

- The primer and templates are treated as first-class artifacts, reviewed with
  the same care as code.
- Engineers must look slightly harder for API detail (mitigated by
  PRACTITIONERS.md and thorough docstrings).
- The dashboard, not the CLI, is the default entry point (`docker compose up`).
