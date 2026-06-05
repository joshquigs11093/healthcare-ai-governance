# PRACTITIONERS.md

Engineering guide for people *producing* the governance artifacts. For the
governance program itself, start with [`docs/primer.md`](docs/primer.md).

> Reference implementation, not a compliance guarantee. See the README.

## Install

```bash
# Core only (inventory + CLI):
uv pip install -e .
# Everything (dashboard, PDF, fairness, audit, LLM):
uv pip install -e ".[all]"
# Dev tooling (tests, ruff, mypy):
uv pip install -e ".[dev]"
```

Plain `pip` works too (`python -m venv .venv && .venv/bin/pip install -e ".[dev]"`).

Some capabilities need native/runtime dependencies that are easiest in Docker:
- **PDF** (model cards, risk assessments, board reports) needs WeasyPrint's Pango/Cairo libraries.
- **Fairness demo** trains a scikit-learn model; Synthea (optional, for real data) needs a JVM.

If a capability's dependency is missing, the toolkit degrades with a clear message
rather than crashing.

## Configuration

Environment variables (see `.env.example`): `INVENTORY_DIR`, `ARTIFACTS_DIR`,
`LLM_PROVIDER`, `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL`, `OPENAI_API_KEY` /
`OPENAI_MODEL`, `PDF_CLASSIFICATION_LABEL`, `LOG_LEVEL`.

## Inventory

```bash
hag inventory list                 # tabular listing
hag inventory show sepsis-ews      # detail (JSON)
hag inventory validate             # lint all YAML against the schema
hag inventory overdue              # systems past their review date (exit 1 if any)
hag inventory compliance           # artifact-presence matrix
```

Each system is one YAML file in `inventory/systems/`. Recreate the demo:
`python scripts/seed_demo_data.py` (`--dry-run` to validate only).

## Model cards

```bash
hag model-card new card.yaml --model-name "My Model" --version 1.0   # scaffold
hag model-card validate card.yaml
hag model-card render card.yaml -f markdown -f html -f pdf -o artifacts/model_cards
```

Markdown follows the HTI-1 source-attribute order; HTML is self-contained; PDF is
WeasyPrint with a paginated, classification-labeled footer.

## Risk assessments

The questionnaire and scoring live in `data/questionnaire.yaml` and
`data/mitigations.yaml` — editable by non-developers.

```bash
hag risk-assessment from-yaml responses.yaml sepsis-ews \
    --output-dir artifacts/risk_assessments --update-inventory
```

`responses.yaml` carries `assessor_name`, `assessor_role`, `assessment_date`, and
a `responses` map of `question_id -> answer`. Output: a JSON record and a signed
PDF; `--update-inventory` links it back to the system. The interactive version is
the **AI Risk Assessment** Streamlit app:
`streamlit run src/healthcare_ai_governance/ui/risk_assessment_app.py`.

## Fairness evaluation

```bash
python scripts/generate_fairness_demo.py --population 5000
```

Trains a logistic-regression readmission model on a Synthea cohort (or a clearly
labeled synthetic cohort if Synthea/Java are absent), runs the evaluator across
demographic, healthcare, and intersectional slices, and writes an HTML report with
per-group ROC and calibration charts to `artifacts/fairness_reports/`. As a
library: `from healthcare_ai_governance.fairness.reporter import build_report`.

## Output auditing

```bash
# Write a JSON report:
hag audit run outputs.jsonl --config data/audit_config.yaml --system guideline-gpt
# CI gate (exit non-zero at/above severity):
hag audit ci outputs.jsonl --config data/audit_config.yaml --fail-on critical
```

`outputs.jsonl` is one JSON object per line: `{"id", "text", "context": [...]}`.
Checks: PHI leakage, unsupported claims (LLM-as-judge), jailbreak, tone, citation
validity. LLM-judge checks activate when `use_llm_judge: true` and an API key is
set; otherwise they return informational findings.

## Dashboard and board report

```bash
streamlit run src/healthcare_ai_governance/ui/dashboard.py   # or: docker compose up
```

Six pages: Portfolio Overview, AI Systems, Reviews Due, Risk Distribution,
Compliance Matrix, Board Report (generates an executive PDF to
`artifacts/board_reports/`).

## Regenerating demo artifacts

```bash
python scripts/regenerate_demo_artifacts.py      # model card(s) + demo audit report
python scripts/generate_fairness_demo.py         # fairness report
```

Generated artifacts under `artifacts/` are gitignored; the scripts recreate them.

## Development

```bash
ruff check src tests scripts && ruff format --check src tests scripts
mypy src
pytest --cov=healthcare_ai_governance --cov-report=term-missing --cov-fail-under=80
```

Architecture: the inventory is the source of truth; every artifact links back by
`system_id`. Logic lives in non-UI modules so it is shared by the CLI, the
dashboard, and the tests. PDF/PII/fairness dependencies are optional and gated. See
[`docs/decisions/`](docs/decisions/) for the rationale behind the major choices.
