from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.api.deps import DbSession, OptionalUser
from app.core.config import settings
from app.crud import cart as cart_crud
from app.crud import game as game_crud
from app.crud import game_comment as comment_crud
from app.crud import user as user_crud
from app.schemas.cart import cart_rows_to_public
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


@router.get("/account", response_model=None)
async def account_redirect(user: OptionalUser) -> RedirectResponse:
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url=f"/account/{user.id}", status_code=302)


@router.get("/account/{member_id}", response_class=HTMLResponse, response_model=None)
async def account_page(
    request: Request,
    member_id: int,
    db: DbSession,
    user: OptionalUser,
) -> HTMLResponse:
    member = await user_crud.get_user_with_profile(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="User not found")
    member_profile = member.profile
    is_own = user is not None and user.id == member_id
    title = "Your account" if is_own else f"{member.name}"
    return templates.TemplateResponse(
        request,
        "account.html",
        {
            "request": request,
            "user": user,
            "title": title,
            "app_name": settings.app_name,
            "member": member,
            "member_profile": member_profile,
            "is_own_profile": is_own,
        },
    )


@router.get("/cart", response_class=HTMLResponse, response_model=None)
async def cart_page(request: Request, db: DbSession, user: OptionalUser) -> HTMLResponse | RedirectResponse:
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    rows = await cart_crud.list_cart_items(db, user.id)
    cart = cart_rows_to_public(rows)
    return templates.TemplateResponse(
        request,
        "cart.html",
        {
            "request": request,
            "user": user,
            "title": "Cart",
            "app_name": settings.app_name,
            "cart": cart,
        },
    )


@router.get("/checkout", response_class=HTMLResponse, response_model=None)
async def checkout_page(
    request: Request,
    db: DbSession,
    user: OptionalUser,
) -> HTMLResponse | RedirectResponse:
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    rows = await cart_crud.list_cart_items(db, user.id)
    if not rows:
        return RedirectResponse(url="/cart", status_code=302)
    return templates.TemplateResponse(
        request,
        "checkout.html",
        {
            "request": request,
            "user": user,
            "title": "Checkout",
            "app_name": settings.app_name,
        },
    )
