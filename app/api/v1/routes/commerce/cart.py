from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud import cart as cart_crud
from app.crud import game as game_crud
from app.schemas.cart import CartItemAdd, CartItemQuantity, CartPublic, cart_rows_to_public

router = APIRouter()


@router.get("", response_model=CartPublic)
async def get_cart(db: DbSession, user: CurrentUser) -> CartPublic:
    rows = await cart_crud.list_cart_items(db, user.id)
    return cart_rows_to_public(rows)


@router.post("/items", status_code=status.HTTP_201_CREATED, response_model=CartPublic)
async def add_cart_item(
    payload: CartItemAdd,
    db: DbSession,
    user: CurrentUser,
) -> CartPublic:
    game = await game_crud.get_game(db, payload.game_id)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    await cart_crud.add_item(db, user.id, payload.game_id, payload.quantity)
    return await get_cart(db, user)


@router.patch("/items/{game_id}", response_model=CartPublic)
async def patch_cart_item_quantity(
    game_id: int,
    payload: CartItemQuantity,
    db: DbSession,
    user: CurrentUser,
) -> CartPublic:
    row = await cart_crud.set_quantity(db, user.id, game_id, payload.quantity)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    return await get_cart(db, user)


@router.delete("/items/{game_id}", response_model=CartPublic)
async def delete_cart_item(game_id: int, db: DbSession, user: CurrentUser) -> CartPublic:
    if not await cart_crud.remove_item(db, user.id, game_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    return await get_cart(db, user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(db: DbSession, user: CurrentUser) -> None:
    await cart_crud.clear_cart(db, user.id)
