# ADR-006: Content-hash "signing" for generated documents

**Status:** Accepted

## Context

Risk assessment PDFs (and model card / board report footers) carry a "signature."
Governance users need to detect whether a generated document was altered after the
fact. The spec (§6.3) anticipated this ADR if signing was added; it has been.

## Decision

Use a SHA-256 hash over the canonical JSON of the document's content as a
tamper-evidence "signature," implemented in `shared/signing.py`. Canonical JSON
(sorted keys, no insignificant whitespace) makes the hash stable across runs and
machines. For risk assessments the hash is computed over the assessment content
*excluding* the signature field itself, stored on the record, and embedded in the
PDF footer.

State plainly, in code and in output, that this is **tamper-evidence, not
authentication**: it detects whether content changed between generation and a
later read; it does **not** prove who produced the document.

## Alternatives considered

- **Cryptographic signatures (e.g. ECDSA).** Authenticate the signer, not just
  detect change. Deferred: requires key management and an identity model that most
  reference-implementation users will not have set up. The hash design leaves room
  to add this later without changing the artifact structure.
- **No signature.** Rejected: even simple tamper-evidence is valuable for a
  governance record and cheap to provide.

## Consequences

- Any modification to the content yields a different hash, which is detectable by
  recomputation.
- The mechanism does not authenticate the assessor; documentation says so to avoid
  overclaiming.
- A future revision can add ECDSA signing for organizations that require
  authentication, reusing the same canonical-content approach.
