# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_Nothing yet._

## [0.1.0] - 2026-06-06

Initial reference implementation.

### Added
- Project governance and community files: `LICENSE` (Apache-2.0), `NOTICE`,
  `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue/PR templates, and
  README status badges.
- **Inventory** — YAML-in-git system registry with Pydantic validation, pure
  query functions, and the `hag inventory` CLI; six-system Mountain Region Health
  demo with an idempotent seed script.
- **Governance dashboard** — six-page Streamlit app (portfolio, systems, reviews
  due, risk distribution, compliance matrix, board report) with Docker.
- **Model card generator** — Markdown / HTML / signed PDF aligned to ONC HTI-1
  source attributes (`hag model-card`).
- **Risk assessment** — data-driven questionnaire (NIST AI RMF + Generative AI
  Profile), deterministic scoring with tier-override floors, mitigations, signed
  PDF, and an interactive Streamlit workflow (`hag risk-assessment`).
- **Fairness evaluator** — demographic parity, equalized odds, equal opportunity,
  PPV parity, and calibration with bootstrap CIs across demographic, healthcare,
  and intersectional slices; HTML report with ROC/calibration charts; Synthea/
  scikit-learn demo pipeline.
- **Output auditor** — PHI leakage (Presidio + custom HIPAA recognizers),
  unsupported-claims LLM-as-judge, jailbreak, tone, and citation validity checks
  with `hag audit run|ci`.
- **Board report generator** — executive PDF from an inventory snapshot.
- **Documentation** — ~3,500-word primer, four templates, three framework
  mappings, and six Architecture Decision Records.
- **CI** — ruff, mypy (strict), pytest with coverage on Python 3.11 and 3.12,
  inventory validation, seed dry-run, and a Docker build smoke test.

[Unreleased]: https://github.com/joshquigs11093/healthcare-ai-governance/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/joshquigs11093/healthcare-ai-governance/releases/tag/v0.1.0
