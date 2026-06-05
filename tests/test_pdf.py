"""Tests for the shared PDF utility (.spec §6.2, ADR-004).

When WeasyPrint is unavailable (e.g. on a Windows dev host without the native
libraries), generation must fail with a clear, typed error rather than a raw
ImportError — and the rest of the toolkit keeps working.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from healthcare_ai_governance.shared.pdf import (
    PDFUnavailableError,
    html_to_pdf,
    pdf_available,
)


def test_pdf_available_returns_bool() -> None:
    assert isinstance(pdf_available(), bool)


@pytest.mark.skipif(pdf_available(), reason="WeasyPrint IS available; tests the missing path")
def test_html_to_pdf_raises_when_unavailable(tmp_path: Path) -> None:
    with pytest.raises(PDFUnavailableError):
        html_to_pdf("<html><body>hi</body></html>", tmp_path / "x.pdf")
