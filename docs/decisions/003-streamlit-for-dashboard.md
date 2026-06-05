# ADR-003: Streamlit for the dashboard

**Status:** Accepted

## Context

The governance dashboard is read-mostly, low-traffic, and used by a small number
of committee members. It needs charts, tables, file previews, and a couple of
interactive workflows (risk assessment, board report). The team's priority is low
build complexity, not pixel-perfect custom UI.

## Decision

Build the dashboard with Streamlit. Keep all logic in non-UI modules
(`dashboard_support.py`, `inventory.queries`, the component generators) so the UI
layer is thin presentation glue and the logic stays testable. Exclude the `ui/`
package from the coverage gate; verify pages render via Streamlit's `AppTest`.

## Alternatives considered

- **Dash (Plotly).** More control over layout/callbacks. Rejected: more
  boilerplate for little gain at this scale.
- **FastAPI + React.** Full control, production-grade. Rejected: a separate
  frontend toolchain and build step is disproportionate for a read-mostly
  internal tool and a reference implementation.
- **Observable / notebooks.** Fast to prototype. Rejected: weaker as a deployable,
  multi-page application with downloads and file generation.

## Consequences

- Minimal frontend toolchain; one `streamlit run` (or `docker compose up`).
- Limited UI customization compared to a bespoke frontend — acceptable.
- Because logic lives outside the UI, the same functions power the CLI, the
  dashboard, and the tests, avoiding duplication.
- UI behavior is validated with `AppTest` rather than unit-covered, so the
  coverage gate targets non-UI code (matches the spec's "80% on non-UI").
