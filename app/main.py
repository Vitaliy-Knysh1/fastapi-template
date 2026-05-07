import asyncio
import sys
from pathlib import Path

# Async psycopg requires a selector-style loop on Windows (default Proactor breaks DB access).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError, ProgrammingError
from starlette.templating import Jinja2Templates

from app.api.v1.router import api_router
from app.core.config import settings
from app.web.routes import router as web_router

ROOT_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger("uvicorn.error")

templates = Jinja2Templates(directory=str(ROOT_DIR / "templates"))

app = FastAPI(title="Videogame Store API")


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
