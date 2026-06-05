"""Render model cards to Markdown, HTML, and PDF (.spec §6.2)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import jinja2

from healthcare_ai_governance.model_card.schema import ModelCard
from healthcare_ai_governance.shared.pdf import html_to_pdf
from healthcare_ai_governance.shared.signing import content_hash, short_hash
from healthcare_ai_governance.types import GovernanceError

SUPPORTED_FORMATS = ("markdown", "html", "pdf")

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=jinja2.select_autoescape(enabled_extensions=("html.j2",), default_for_string=False),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def slugify(value: str) -> str:
    """Filesystem-safe slug: lowercased, non-alphanumeric runs collapsed to '-'."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "model"


def _context(
    card: ModelCard, classification_label: str, generation_date: date
) -> dict[str, object]:
    full_hash = content_hash(card)
    return {
        "card": card,
        "doc_hash": full_hash,
        "short_hash": short_hash(card),
        "generation_date": generation_date.isoformat(),
        "classification": classification_label,
    }


def render_markdown(card: ModelCard, classification_label: str, generation_date: date) -> str:
    template = _env.get_template("model_card.md.j2")
    return template.render(**_context(card, classification_label, generation_date))


def render_html(card: ModelCard, classification_label: str, generation_date: date) -> str:
    template = _env.get_template("model_card.html.j2")
    return template.render(**_context(card, classification_label, generation_date))


def generate_model_card(
    card: ModelCard,
    output_dir: Path,
    formats: list[str],
    classification_label: str = "Internal Use Only",
    generation_date: date | None = None,
) -> dict[str, Path]:
    """Render ``card`` to the requested formats and write files to ``output_dir``.

    Returns a mapping of format name -> written path. Filenames follow
    ``{model_name_slug}-v{version}.{ext}`` (.spec §6.2).
    """
    unknown = [f for f in formats if f not in SUPPORTED_FORMATS]
    if unknown:
        raise GovernanceError(
            f"Unsupported format(s): {', '.join(unknown)}. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}."
        )
    if not formats:
        raise GovernanceError("No formats requested.")

    gen_date = generation_date or date.today()
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{slugify(card.model_name)}-v{card.version}"
    outputs: dict[str, Path] = {}

    if "markdown" in formats:
        md = render_markdown(card, classification_label, gen_date)
        path = output_dir / f"{base}.md"
        path.write_text(md, encoding="utf-8")
        outputs["markdown"] = path

    # HTML is rendered once and reused for the PDF.
    html: str | None = None
    if "html" in formats or "pdf" in formats:
        html = render_html(card, classification_label, gen_date)

    if "html" in formats and html is not None:
        path = output_dir / f"{base}.html"
        path.write_text(html, encoding="utf-8")
        outputs["html"] = path

    if "pdf" in formats and html is not None:
        path = output_dir / f"{base}.pdf"
        html_to_pdf(html, path)
        outputs["pdf"] = path

    return outputs
