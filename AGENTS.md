# Repository Guidelines

## Project Structure & Module Organization
- `app.py` holds the Flask app, routes (`/`, `/webhook`, `/updates`, `/updates/list`, `/updates/summary`), and file-based storage logic keyed by `image`.
- `updates.json` is the single data store (mount this file when running in Docker to persist state).
- `requirements.txt` pins runtime deps; `Dockerfile` builds a Python 3.11 image; `README.md` documents runtime setup; `LICENSE` covers usage.

## Build, Test, and Development Commands
- Local env (recommended): `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Run locally: `APP_PORT=5000 APP_IP=0.0.0.0 python app.py` (debug off by default).
- Docker build/run: `docker build -t diun-homepage:latest .` then `docker run -d -p 5000:5000 -v $(pwd)/updates.json:/app/updates.json diun-homepage:latest`.
- Compose example lives in `README.md`; ensure `updates.json` exists before starting the container.

## Coding Style & Naming Conventions
- Python 3.11, PEP 8 with 4-space indents; keep functions and variables in `snake_case`; constants/env vars in `UPPER_SNAKE_CASE`.
- Route handlers stay small and focused; prefer explicit keys matching webhook payload (`image`, `status`, `provider`, `digest`, `created`, `platform`, `hub-link`, `hostname`, `metadata`, `detected_at`).
- Keep JSON responses deterministic; when adding fields, update sorting/filtering logic in list/summary endpoints.

## Testing Guidelines
- Automated: `. .venv/bin/activate && pytest -q` (create the venv first with `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`).
- Manual sanity: `curl http://localhost:5000/` (health), `curl -X POST -H "Content-Type: application/json" -d '{"image":"repo:tag","status":"update"}' http://localhost:5000/webhook`, then `curl http://localhost:5000/updates/list` to confirm ordering and deduping.
- Validate that a >1h gap between webhooks clears prior updates; adjust `one_hour_ms` if making timing changes.
- If adding tests, mirror route-level behavior with pytest and use a temp file for `STORAGE_FILE`.

## Commit & Pull Request Guidelines
- Follow the existing imperative, concise style (`add X`, `update Y`); include scope when relevant (e.g., `add webhook validation`).
- PRs: describe behavior changes, note API or payload adjustments, link any issue/ticket, and include manual verification steps or sample `curl` commands. Add screenshots from Homepage if UI-facing behavior is affected.

## Security & Configuration Tips
- Keep the webhook endpoint behind network controls; do not expose `/webhook` publicly without auth on the surrounding network.
- Mount `updates.json` with least-privilege permissions, and avoid committing instance-specific data or secrets.
