# Contributing

Thanks for your interest in improving **healthcare-ai-governance**. This is a
reference implementation; contributions that keep it accurate, honest, and
maintainable are very welcome.

> By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ground rules

- **It is a reference implementation, not a product.** Changes should not imply
  regulatory compliance, clinical validation, or capabilities the toolkit does
  not have. When the toolkit cannot guarantee something, say so plainly.
- **Documentation is first-class.** The primer, templates, and framework mappings
  are reviewed with the same care as code. Framework citations
  (`docs/mappings/`) must be accurate against primary sources.
- **The inventory is the single source of truth.** Every artifact links back to a
  system by `system_id`.

## Development setup

```bash
git clone https://github.com/joshquigs11093/healthcare-ai-governance.git
cd healthcare-ai-governance
uv venv && uv pip install -e ".[dev]"     # or: python -m venv .venv && pip install -e ".[dev]"
```

PDF, fairness, and PII features need extra system/runtime dependencies that are
easiest in Docker (`docker compose up`). See [PRACTITIONERS.md](PRACTITIONERS.md).

## Before you open a pull request

Run the full local gate — it mirrors CI:

```bash
ruff check src tests scripts
ruff format --check src tests scripts
mypy src
pytest --cov=healthcare_ai_governance --cov-report=term-missing --cov-fail-under=80
```

All four must pass. Coverage is enforced at 80% on non-UI code (`ui/` is excluded
and verified separately via Streamlit `AppTest`).

## Conventions

- **Python 3.11+**, fully type-annotated; `mypy --strict` must pass. No untyped
  dictionaries cross module boundaries — use the Pydantic schemas.
- **Logic lives in non-UI modules** so it is shared by the CLI, dashboard, and
  tests. Keep Streamlit pages thin.
- **Optional heavy dependencies** (WeasyPrint, scikit-learn, Presidio, LLM SDKs)
  must be imported lazily and degrade gracefully when absent.
- **Tests** accompany behavior changes. Prefer deterministic, hand-computed
  expectations; mock LLM calls.
- **Commits**: clear, imperative subject lines; explain the "why" in the body.

## Pull requests

1. Branch from `main` (e.g. `feat/...`, `fix/...`, `docs/...`).
2. Make the change with tests and docs.
3. Ensure the local gate passes.
4. Open a PR using the template; describe what and why.
5. CI (`test (3.11)`, `test (3.12)`, `docker`) must be green — `main` is
   protected and requires it.

## Reporting bugs and proposing features

Use the GitHub issue templates. For anything security- or PHI-related, follow the
[Security Policy](SECURITY.md) instead of opening a public issue.
