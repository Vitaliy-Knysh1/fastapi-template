import asyncio
import sys
from pathlib import Path

# Async psycopg requires a selector-style loop on Windows (default Proactor breaks DB access).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging

import time

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

ROOT_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger("uvicorn.error")

templates = Jinja2Templates(directory=str(ROOT_DIR / "templates"))

app = FastAPI(title="Luckygames Shop API")


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start

    path = request.url.path
    method = request.method
    status = str(response.status_code)

    # Keep label cardinality bounded for built-in routes.
    if path.startswith("/api/v1/"):
        if path.startswith("/api/v1/auth/"):
            path = "/api/v1/auth/*"
        elif path.startswith("/api/v1/games/by-slug/"):
            path = "/api/v1/games/by-slug/*"
        elif path.startswith("/api/v1/games/"):
            path = "/api/v1/games/*"
        elif path.startswith("/api/v1/users/"):
            path = "/api/v1/users/*"
        elif path.startswith("/api/v1/orders/"):
            path = "/api/v1/orders/*"
        elif path.startswith("/api/v1/order-lines/"):
            path = "/api/v1/order-lines/*"
        elif path.startswith("/api/v1/genres/"):
            path = "/api/v1/genres/*"
        elif path.startswith("/api/v1/profiles/"):
            path = "/api/v1/profiles/*"
        elif path.startswith("/api/v1/cart/"):
            path = "/api/v1/cart/*"
        elif path.startswith("/api/v1/checkout/"):
            path = "/api/v1/checkout/*"
        elif path.startswith("/api/v1/account/"):
            path = "/api/v1/account/*"

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
    logger.warning("Database operational error: %s", exc)
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
    logger.warning("Database programming error: %s", exc)
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
