# Luckygames Shop

FastAPI + PostgreSQL storefront template (labs project).

## Run

Install dependencies with Poetry (`poetry install`). Start PostgreSQL. Copy `.env.example` to `.env` and adjust secrets.

Application entrypoint: `main.py`. Docker: `docker compose up --build`.

## Production vs lab-only content

- **Docker image:** `.dockerignore` excludes `LABS/`, `monitoring/` (Grafana/Prometheus files), `docs/`, `tests/`, lab compose files, and similar so production builds stay small. You do not need to delete those from Git for deployment.
- **`app/monitoring/`** stays in the image — it is application code for `/metrics`, not the Lab 7 stack.
- **Prod Git branch without lab folders:** see `docs/prod_branch.txt` (optional; has merge caveats).

## Lab 6 — API tests

Use the Poetry environment so all dependencies load (including `prometheus_client`):

`poetry run pytest`

Running plain `pytest` with system Python will fail or skip the HTTP tests.

Tests need PostgreSQL. By default they use `postgresql://postgres:postgres@localhost:5432/app_test` (database `app_test` is created automatically if missing).

If your DB listens on another host port (for example `15432` from root `docker-compose.yml`), set:

`TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:15432/app_test`

Run tests and generate HTML + logs under `docs/lab6/`:

`powershell -ExecutionPolicy Bypass -File .\scripts\run_lab6_tests.ps1` (Windows) or `bash ./scripts/run_lab6_tests.sh`.

Equivalent manual command:

`poetry run pytest tests/ -v --tb=short --html=docs/lab6/pytest_report.html --self-contained-html`

