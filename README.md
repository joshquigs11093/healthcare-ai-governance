# healthcare-ai-governance

A reference implementation of governance tooling for healthcare AI programs. It
produces the artifacts a compliance officer, AI governance committee, or hospital
board needs to review an AI portfolio: a risk-classified system inventory, model
cards, NIST AI RMF–mapped risk assessments, fairness reports, and LLM output
audits.

> This is a **reference implementation**, not a production governance platform and
> not legal or compliance advice. See `.spec/SPEC-healthcare-ai-governance.md` for
> the full build specification and `docs/` for context.

## Status

Under active construction. See milestone progress in the spec (§13). Currently
implemented:

- **Inventory foundation** — YAML-in-git system registry with Pydantic schema
  validation, pure query functions, and the `hag inventory` CLI.

## Quickstart

```bash
# Install (core + dev tooling)
uv pip install -e ".[dev]"

# Explore the CLI
hag --help
hag inventory --help

# Validate and browse the inventory
hag inventory validate
hag inventory list
hag inventory overdue
hag inventory compliance
```

Optional capabilities install as extras: `.[pdf]`, `.[dashboard]`, `.[fairness]`,
`.[audit]`, `.[llm]`, or `.[all]`.

## Configuration

All configuration is via environment variables (see `.env.example` and spec §8).

## License

Apache-2.0.
