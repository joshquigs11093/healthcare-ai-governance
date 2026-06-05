# ADR-005: Microsoft Presidio for PII detection, and its limits

**Status:** Accepted

## Context

The output auditor detects PHI leakage in LLM outputs. It must cover the HIPAA 18
identifier categories as well as is practical for a reference implementation, be
open-source and credible, and be honest about what it does and does not catch.
Clinical narrative is a hard target for general-purpose PII detection.

## Decision

Use Microsoft Presidio's `AnalyzerEngine` for NER-based entities (names,
locations) when it is available, **plus** a set of custom regex recognizers for
the pattern-detectable HIPAA identifiers (SSN, MRN, account, health-plan id,
license, device serial, phone, email, URL, IP, VIN, dates, ZIP+4, age over 89).
The regex recognizers run with or without Presidio, so the check is useful on any
host; Presidio adds the NER entities when its spaCy model is present.

Document the limits plainly: name/geographic/free-text identifiers require
Presidio's NER and an installed language model; full-face photographs are out of
scope for a text auditor; Presidio is general-purpose and not tuned for clinical
narrative.

## Alternatives considered

- **Presidio alone.** Rejected: its out-of-the-box recognizers miss or imperfectly
  cover several HIPAA-specific identifiers (MRN, account, device serials), and it
  requires a spaCy model that may be absent.
- **Regex alone.** Rejected: cannot detect names or locations, which are core PHI.
- **A commercial clinical de-identification system (e.g. John Snow Labs Medical
  NLP).** Higher recall on clinical text. Rejected for the reference
  implementation because it is not open-source; recommended as the production-grade
  alternative.

## Consequences

- The PHI check is recall-oriented and runs everywhere; regex recognizers are
  tightened to avoid false positives on common clinical phrasing ("Plan: ...").
- Findings include the entity type and a redacted excerpt; the value is replaced
  with `[ENTITY_TYPE]`.
- For higher-stakes production de-identification, organizations should evaluate a
  domain-specific clinical NLP system. This limitation is stated here and in the
  output auditor's documentation, consistent with the toolkit's honesty principle.
