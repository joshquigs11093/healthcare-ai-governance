# Dashboard screenshots

These PNGs are referenced from the project README. They are captured from the live
dashboard running against the committed Mountain Region Health demo inventory.

## Regenerate

```bash
# 1. Start the dashboard (pre-loaded with the demo data)
docker compose up -d        # or: streamlit run src/healthcare_ai_governance/ui/dashboard.py

# 2. Install the capture dependency
pip install playwright && python -m playwright install chromium

# 3. Capture
python scripts/capture_screenshots.py        # writes *.png here

# 4. Stop the dashboard
docker compose down
```

The capture script (`scripts/capture_screenshots.py`) drives the sidebar
navigation and screenshots each page. Note: the "Recent governance activity" feed
is empty in the container because the git history is not mounted; run locally for
a populated activity feed.
