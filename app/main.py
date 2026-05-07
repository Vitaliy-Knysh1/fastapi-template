import asyncio
import sys
from pathlib import Path

# Async psycopg requires a selector-style loop on Windows (default Proactor breaks DB access).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.web.routes import router as web_router

ROOT_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Videogame Store API")

app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")

app.include_router(web_router)
app.include_router(api_router)
