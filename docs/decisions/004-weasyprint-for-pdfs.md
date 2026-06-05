# ADR-004: WeasyPrint for PDF generation

**Status:** Accepted

## Context

The toolkit produces several PDF artifacts — model cards, signed risk
assessments, and board reports — that must look professional (tables, headers,
page numbers, footers with classification labels and content hashes). The HTML
representations of these artifacts already exist, so the natural question is how to
turn HTML/CSS into PDF.

## Decision

Use WeasyPrint to render HTML/CSS to PDF. Each artifact has an HTML Jinja2
template carrying its own `@page` CSS (margins, paginated footers). A single
`shared/pdf.py` wrapper performs the conversion and raises a clear
`PDFUnavailableError` if WeasyPrint or its native libraries are missing, so the
Markdown/HTML paths keep working on hosts without them.

## Alternatives considered

- **ReportLab.** Powerful, pure-Python, no native deps. Rejected: programmatic
  layout is verbose and we already have HTML/CSS; visual iteration is slower.
- **pdfkit / wkhtmltopdf.** Also HTML-to-PDF. Rejected: wkhtmltopdf is
  effectively unmaintained and bundles an old WebKit; WeasyPrint has better,
  standards-based CSS support including `@page`.
- **Headless Chromium (Playwright).** Excellent fidelity. Rejected: a full
  browser is a heavy dependency for static document rendering.

## Consequences

- Layout is expressed in CSS, which designers and developers can both edit, and
  HTML/PDF stay visually consistent.
- WeasyPrint needs native libraries (Pango, Cairo, GDK-PixBuf) that are awkward on
  Windows but trivial in the Docker image; the Dockerfile installs them.
- PDF generation degrades gracefully off-Docker: the wrapper raises a typed,
  actionable error and callers fall back to Markdown/HTML or skip the PDF.
