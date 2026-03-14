# CLAUDE.md — SeaForge

The open-source life-at-sea platform. Flask + SQLite + Leaflet in Docker.

## Tech Stack
- Backend: Flask (Python 3.12), SQLite (WAL mode), gunicorn
- Frontend: Leaflet.js + vanilla JS, Jinja2 templates
- Deployment: Single Docker container on port 5000
- Data: Free APIs (Open-Meteo, RainViewer, EMODnet, NOAA, aisstream.io)

## Key Files
- `app.py` — Flask app factory, blueprint registration
- `src/api/{navigation,wellbeing,training,ops}.py` — REST endpoints
- `src/core/{colregs,ais,nmea,mob}.py` — Business logic
- `src/data/{models,fleet_db,lights_db}.py` — Data layer
- `static/js/app.js` — Frontend (map, API calls, views)
- `templates/index.html` — SPA shell with dark nautical theme

## Commands
```bash
docker compose up --build -d    # Build and run
docker compose down              # Stop
docker logs seaforge -f          # Logs
curl localhost:5000/api/health   # Health check
```

## Conventions
- API routes: `/api/<module>/<resource>` (REST, JSON)
- New endpoint: add to `src/api/*.py`, register blueprint in `app.py`
- Database: raw SQL in `src/data/models.py`, WAL mode, foreign keys
- No ORM, no frontend framework, no auth (self-hosted single-user)
- Keep dependencies minimal (`requirements.txt` < 10 packages)

## Constraints
- Never commit `.env` (API keys). Only `.env.example` with empty placeholders.
- SQLite only — no Postgres, no Redis. Single file = simple backup.
- All external APIs must be free/no-key or optional.
- Offline-first: core features must work without internet.
