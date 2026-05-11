# Luckygames Shop

FastAPI + PostgreSQL storefront.

## Run

Install dependencies with Poetry (`poetry install`). Start PostgreSQL. Copy `.env.example` to `.env` and adjust secrets.

Application entrypoint: `main.py`. Production: `docker compose up --build` (uses `docker-compose.yml` only).

`app/monitoring/` exposes Prometheus-format metrics at `/metrics` for your own scraping if you add a monitor stack elsewhere.
