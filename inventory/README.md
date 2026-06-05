# Inventory

The AI system inventory is the **single source of truth** for the governance
toolkit (.spec §15.1). It is stored as YAML files in version control so it can be
reviewed through pull requests, read without running software, and carries full
version history (ADR-002).

## Layout

```
inventory/
  organization.yaml      # Org-level metadata (header, board report)
  systems/
    <system-id>.yaml     # One file per AI system
```

Each `systems/*.yaml` file validates against the `AISystem` schema
(`src/healthcare_ai_governance/inventory/schema.py`). Run `hag inventory validate`
to lint all files.

## Demo data

This directory ships pre-populated for a **fictional** organization,
*Mountain Region Health*, so the dashboard is immediately useful on clone. The six
demo systems have intentionally varied artifact completeness to exercise the
compliance matrix and "reviews due" views. Regenerate with
`python scripts/seed_demo_data.py`.

| System | Type | Risk | Lifecycle |
|---|---|---|---|
| Sepsis Early Warning System v2 | predictive | high | production |
| 30-Day Readmission Risk | predictive | medium | production |
| guideline-gpt RAG Assistant | generative | medium | validation |
| Radiology Triage Prioritizer | predictive | high | validation |
| CDI Documentation Assistant | generative | low | development |
| Scheduling Optimizer | operational | low | production |
