from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.api.deps import DbSession, OptionalUser
from app.core.config import settings
from app.crud import game as game_crud
from app.crud import game_comment as comment_crud
from app.schemas.game import GameDetailPublic, GamePublic

router = APIRouter(tags=["ui"])

_base = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(_base / "templates"))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: DbSession, user: OptionalUser) -> HTMLResponse:
    rows = await game_crud.list_storefront_games(db)
    games = [GamePublic.from_game(g) for g in rows]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user": user,
            "title": "Home",
            "app_name": settings.app_name,
            "games": games,
        },
    )


@router.get("/games/{slug}", response_class=HTMLResponse)
async def game_detail(
    request: Request,
    slug: str,
    db: DbSession,
    user: OptionalUser,
) -> HTMLResponse:
    game = await game_crud.get_game_by_slug(db, slug)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    detail = GameDetailPublic(
        **GamePublic.from_game(game).model_dump(),
        genre_name=game.genre.name,
    )
    rows = await comment_crud.list_for_game_with_authors(db, game.id)
    comments = [
        {"id": c.id, "body": c.body, "created_at": c.created_at, "author_name": name}
        for c, name in rows
    ]
    return templates.TemplateResponse(
        request,
        "game.html",
        {
            "request": request,
            "user": user,
            "title": detail.title,
            "app_name": settings.app_name,
            "game": detail,
            "comments": comments,
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
