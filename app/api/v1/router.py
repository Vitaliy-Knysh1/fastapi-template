from fastapi import APIRouter

from app.api.v1.endpoints import account, auth, cart, checkout, games, genres, order_lines, orders, profiles, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(genres.router, prefix="/genres", tags=["genres"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(checkout.router, prefix="/checkout", tags=["checkout"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(order_lines.router, prefix="/order-lines", tags=["order-lines"])
