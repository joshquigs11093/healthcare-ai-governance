# ADR-002: File-based YAML inventory in version control

**Status:** Accepted

## Context

The AI system inventory is the single source of truth for the toolkit. It needs
to support multi-stakeholder review, carry version history (who changed what and
why), be readable without running software, and remain trustworthy as an audit
trail. The expected scale is small: tens to low hundreds of systems for a typical
health system.

## Decision

Store the inventory as one YAML file per system under `inventory/systems/`,
committed to git. Validation is performed against a Pydantic schema. Writes are
atomic (write-temp-then-rename). The git history *is* the audit trail; the
dashboard's activity feed reads `git log`.

## Alternatives considered

- **SQLite.** Single-file database, easy to ship. Rejected: not human-readable,
  no native diff/PR review, version history requires extra tooling.
- **PostgreSQL / managed DB.** Scales and supports concurrency. Rejected:
  operational overhead with no benefit at this scale; harder to run as a
  reference implementation; review happens in a separate UI rather than familiar
  PR tooling.
- **NoSQL document store.** Flexible schema. Rejected: schema flexibility is a
  liability for governance records, where consistency and validation matter.

## Consequences

- Multi-stakeholder review happens through pull requests — tooling teams already
  know.
- The inventory is diffable and readable in any text editor or on the git host.
- Concurrency and very large scale are not supported, which is acceptable for the
  target use; an organization outgrowing files can migrate to a database behind
  the same registry interface.
- The registry API (`load_inventory`, `save_system`) abstracts storage, so a
  future backend swap does not ripple through the codebase.
