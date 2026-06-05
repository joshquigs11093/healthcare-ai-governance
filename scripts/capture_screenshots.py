"""Capture dashboard screenshots for the README (.spec §14, M10).

Drives the running dashboard with Playwright and saves PNGs to docs/images/.

Prerequisites:
    pip install -e ".[dashboard]" playwright
    python -m playwright install chromium
    # Dashboard running, e.g.:  docker compose up   (or streamlit run ...)

Usage:
    python scripts/capture_screenshots.py [--url http://localhost:8501]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"

# (sidebar page label, output filename)
_PAGES = [
    ("Portfolio Overview", "portfolio-overview.png"),
    ("Compliance Matrix", "compliance-matrix.png"),
    ("Risk Distribution", "risk-distribution.png"),
    ("Board Report", "board-report.png"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture dashboard screenshots.")
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--timeout", type=int, default=30000)
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. See this script's docstring.")
        return 1

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1024})
        page.goto(args.url, timeout=args.timeout, wait_until="networkidle")
        page.wait_for_timeout(2500)
        sidebar = page.locator('section[data-testid="stSidebar"]')

        for label, filename in _PAGES:
            try:
                sidebar.get_by_text(label, exact=True).click(timeout=args.timeout)
            except Exception as exc:  # noqa: BLE001
                print(f"Could not select '{label}': {exc}")
                continue
            page.wait_for_timeout(2500)  # let charts render
            dest = IMAGES_DIR / filename
            page.screenshot(path=str(dest), full_page=True)
            print(f"saved {dest.relative_to(IMAGES_DIR.parent.parent)}")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
