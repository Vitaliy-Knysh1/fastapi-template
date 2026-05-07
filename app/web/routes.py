from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.api.deps import OptionalUser
from app.core.config import settings

router = APIRouter(tags=["ui"])

_base = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(_base / "templates"))

# Static storefront (UAH). Images under /static/images/games/.
STOREFRONT_GAMES: list[dict[str, object]] = [
    {
        "title": "Balatro",
        "image_url": "/static/images/games/balatro.png",
        "price_uah": 325,
    },
    {
        "title": "Geometry Dash",
        "image_url": "/static/images/games/geometry_dash.png",
        "price_uah": 124,
    },
    {
        "title": "Monster Hunter: World",
        "image_url": "/static/images/games/mh_world.png",
        "price_uah": 949,
    },
    {
        "title": "Persona 3 Reload",
        "image_url": "/static/images/games/persona3.png",
        "price_uah": 1799,
    },
    {
        "title": "Persona 4 Golden",
        "image_url": "/static/images/games/persona4.png",
        "price_uah": 649,
    },
    {
        "title": "Clair Obscur: Expedition 33",
        "image_url": "/static/images/games/expedition_33.png",
        "price_uah": 1499,
    },
    {
        "title": "Hollow Knight: Silksong",
        "image_url": "/static/images/games/silksong.png",
        "price_uah": 415,
    },
    {
        "title": "Minecraft",
        "image_url": "/static/images/games/minecraft.png",
        "price_uah": 2302,
    },
]


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: OptionalUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user": user,
            "title": "Home",
            "app_name": settings.app_name,
            "games": STOREFRONT_GAMES,
        },
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: OptionalUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "request": request,
            "user": user,
            "title": "Register",
            "app_name": settings.app_name,
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: OptionalUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "request": request,
            "user": user,
            "title": "Login",
            "app_name": settings.app_name,
        },
    )


@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request, user: OptionalUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "account.html",
        {
            "request": request,
            "user": user,
            "title": "Account",
            "app_name": settings.app_name,
        },
    )
