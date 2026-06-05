"""HTML-to-PDF rendering via WeasyPrint (.spec §3, ADR-004).

WeasyPrint requires native libraries (Pango, Cairo, GDK-PixBuf) that are awkward
to install on Windows but trivial in the Docker image. The import is therefore
deferred and wrapped: callers get a clear, actionable error if WeasyPrint is
unavailable, and the rest of the toolkit (Markdown/HTML output) keeps working.
"""

from __future__ import annotations

from pathlib import Path

from healthcare_ai_governance.types import GovernanceError


class PDFUnavailableError(GovernanceError):
    """Raised when PDF generation is requested but WeasyPrint cannot be imported."""


def pdf_available() -> bool:
    """Return True if WeasyPrint and its native dependencies are importable."""
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError):
        return False
    return True


def html_to_pdf(html: str, output_path: Path, base_url: str | None = None) -> Path:
    """Render an HTML string to a PDF file.

    The HTML is expected to carry its own ``@page`` CSS (footers, page numbers).
    ``base_url`` resolves any relative asset references; defaults to the output
    directory.

    Raises ``PDFUnavailableError`` if WeasyPrint is not installed/usable.
    """
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:  # pragma: no cover - env-dependent
        raise PDFUnavailableError(
            "PDF generation requires WeasyPrint and its native libraries "
            "(Pango/Cairo). Install the 'pdf' extra (`pip install -e \".[pdf]\"`) "
            "and the system libraries, or generate the PDF inside the Docker image "
            "where they are provided."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_base = base_url or str(output_path.parent)
    HTML(string=html, base_url=resolved_base).write_pdf(str(output_path))
    return output_path
