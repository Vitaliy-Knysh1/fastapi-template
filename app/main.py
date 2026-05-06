from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(title="Videogame Store API")
app.include_router(api_router)

