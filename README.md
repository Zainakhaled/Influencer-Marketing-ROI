# Influencer ROI Lab

Two entrances: **Influencer** (enter a campaign, get expected sales) and **Admin** (password protected: dataset analytics for all 150,000 campaigns + live submissions). `/guide` explains every term.

## Run locally
    pip install -r requirements.txt
    python app.py            # http://127.0.0.1:5000   (admin password locally: admin123)

## Deploy on Render
1. Push this folder to GitHub. 2. Render > New > Blueprint > pick the repo.
3. Environment tab shows the generated ADMIN_PASSWORD. Use it at /admin.

## Rebuild after changing the data or notebook logic
Put the CSV in `data/`, then run `python train.py` (model.joblib, meta.json) and `python build_stats.py` (stats.json).

## Notes
- Always set ADMIN_PASSWORD and SECRET_KEY in production. Locally it falls back to admin123.
- Submissions live in SQLite (roi.db). On Render's free plan it resets on deploy; add a disk and set DB_PATH, or use Postgres.
- Edit the guide text in the GLOSSARY list at the top of app.py.
