import asyncio
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy.exc import OperationalError, ProgrammingError
from starlette.templating import Jinja2Templates

from app.api.v1.router import api_router
from app.core.config import settings
from app.monitoring.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL
from app.web.routes import router as web_router

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ROOT_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(ROOT_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    if sys.modules.get("pytest") is not None:
        yield
        return
    if os.environ.get("AUTO_SEED", "1").lower() not in {"1", "true", "yes"}:
        yield
        return
    if os.environ.get("SKIP_SEED", "").lower() in {"1", "true", "yes"}:
        yield
        return
    from sqlalchemy import func, select

    from app.db.session import AsyncSessionLocal
    from app.models.game import Game

    async with AsyncSessionLocal() as db:
        n = (await db.execute(select(func.count()).select_from(Game))).scalar_one()
    if n == 0:
        r = subprocess.run(
            [sys.executable, str(ROOT_DIR / "scripts" / "seed_db.py")],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print(
                "Startup seed failed (empty catalog). Run: poetry run python scripts/seed_db.py",
                file=sys.stderr,
            )
            out = (r.stderr or r.stdout or "").strip()
            if out:
                print(out, file=sys.stderr)
    yield


_API_METRIC_BUCKETS: tuple[tuple[str, str], ...] = (
    ("/api/v1/auth", "/api/v1/auth/*"),
    ("/api/v1/games/by-slug", "/api/v1/games/by-slug/*"),
    ("/api/v1/games", "/api/v1/games/*"),
    ("/api/v1/users", "/api/v1/users/*"),
    ("/api/v1/orders", "/api/v1/orders/*"),
    ("/api/v1/order-lines", "/api/v1/order-lines/*"),
    ("/api/v1/genres", "/api/v1/genres/*"),
    ("/api/v1/profiles", "/api/v1/profiles/*"),
    ("/api/v1/cart", "/api/v1/cart/*"),
    ("/api/v1/checkout", "/api/v1/checkout/*"),
    ("/api/v1/account", "/api/v1/account/*"),
)


def _metrics_api_path(path: str) -> str:
    if not path.startswith("/api/v1"):
        return path
    for prefix, label in _API_METRIC_BUCKETS:
        if path == prefix or path.startswith(prefix + "/"):
            return label
    return path


app = FastAPI(title="Luckygames Shop API", lifespan=lifespan)


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start

    path = _metrics_api_path(request.url.path)
    method = request.method
    status = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(elapsed)
    return response


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _db_fail_message(exc: Exception) -> str:
    text = str(exc).strip()
    if "does not exist" in text.lower() and "database" in text.lower():
        return "PostgreSQL is running but the database name in DATABASE_URL does not exist."
    if "column" in text.lower() and ("does not exist" in text.lower() or "undefinedcolumn" in text.lower()):
        return "The database schema is out of date. Run: alembic upgrade head"
    if "connection" in text.lower() or "refused" in text.lower():
        return "Could not connect to PostgreSQL. Check DATABASE_URL and that the server is running."
    return "Could not complete a database operation."


@app.exception_handler(OperationalError)
async def handle_operational_error(request: Request, exc: OperationalError) -> JSONResponse | HTMLResponse:
    msg = _db_fail_message(exc)
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=503, content={"detail": msg})
    return templates.TemplateResponse(
        request,
        "error_db.html",
        {
            "request": request,
            "user": None,
            "title": "Unavailable",
            "app_name": settings.app_name,
            "message": msg,
        },
        status_code=503,
    )


@app.exception_handler(ProgrammingError)
async def handle_programming_error(request: Request, exc: ProgrammingError) -> JSONResponse | HTMLResponse:
    msg = _db_fail_message(exc)
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=503, content={"detail": msg})
    return templates.TemplateResponse(
        request,
        "error_db.html",
        {
            "request": request,
            "user": None,
            "title": "Unavailable",
            "app_name": settings.app_name,
            "message": msg,
        },
        status_code=503,
    )


app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")
app.include_router(web_router)
app.include_router(api_router)
