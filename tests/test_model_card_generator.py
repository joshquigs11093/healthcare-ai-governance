"""Tests for the model card generator (.spec §6.2, §9)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from healthcare_ai_governance.model_card.generator import (
    generate_model_card,
    render_markdown,
    slugify,
)
from healthcare_ai_governance.shared.pdf import pdf_available
from healthcare_ai_governance.shared.signing import content_hash, short_hash
from healthcare_ai_governance.types import GovernanceError

_GOLDEN = Path(__file__).parent / "fixtures" / "model_card_readmission.md"
_FIXED_DATE = date(2026, 6, 1)


def test_slugify() -> None:
    assert slugify("30-Day Readmission Risk") == "30-day-readmission-risk"
    assert slugify("guideline-gpt RAG Assistant!!") == "guideline-gpt-rag-assistant"
    assert slugify("???") == "model"


def test_markdown_golden(sample_model_card) -> None:
    rendered = render_markdown(sample_model_card, "Internal Use Only", _FIXED_DATE)
    if not _GOLDEN.exists():  # pragma: no cover - first-run bootstrap
        _GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        _GOLDEN.write_text(rendered, encoding="utf-8")
        pytest.skip("golden file created; re-run to compare")
    expected = _GOLDEN.read_text(encoding="utf-8")
    assert rendered == expected


def test_markdown_contains_hash_and_classification(sample_model_card) -> None:
    rendered = render_markdown(sample_model_card, "Confidential", _FIXED_DATE)
    assert content_hash(sample_model_card) in rendered
    assert short_hash(sample_model_card) in rendered
    assert "Confidential" in rendered


def test_generate_markdown_and_html(sample_model_card, tmp_path: Path) -> None:
    written = generate_model_card(
        sample_model_card, tmp_path, ["markdown", "html"], generation_date=_FIXED_DATE
    )
    assert set(written) == {"markdown", "html"}
    assert written["markdown"].name == "30-day-readmission-risk-v1.2.md"
    assert written["html"].name == "30-day-readmission-risk-v1.2.html"
    assert written["markdown"].read_text(encoding="utf-8").startswith("# Model Card")
    html = written["html"].read_text(encoding="utf-8")
    assert "<title>Model Card: 30-Day Readmission Risk</title>" in html
    assert "@bottom-right" in html  # page-number footer present


def test_unsupported_format_rejected(sample_model_card, tmp_path: Path) -> None:
    with pytest.raises(GovernanceError):
        generate_model_card(sample_model_card, tmp_path, ["docx"])


def test_empty_formats_rejected(sample_model_card, tmp_path: Path) -> None:
    with pytest.raises(GovernanceError):
        generate_model_card(sample_model_card, tmp_path, [])


@pytest.mark.skipif(not pdf_available(), reason="WeasyPrint not available")
def test_generate_pdf(sample_model_card, tmp_path: Path) -> None:
    written = generate_model_card(sample_model_card, tmp_path, ["pdf"], generation_date=_FIXED_DATE)
    pdf = written["pdf"]
    assert pdf.exists()
    assert pdf.read_bytes().startswith(b"%PDF")
