from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud import order as order_crud
from app.schemas.order import OrderCreate, OrderDetail, OrderPublic, OrderUpdate

router = APIRouter()


@router.get("/me", response_model=list[OrderPublic])
async def list_my_orders(user: CurrentUser, db: DbSession) -> list[OrderPublic]:
    orders = await order_crud.list_orders_for_user(db, user.id)
    return [OrderPublic.model_validate(o) for o in orders]


@router.get("/", response_model=list[OrderPublic])
async def list_orders(db: DbSession) -> list[OrderPublic]:
    orders = await order_crud.list_orders(db)
    return [OrderPublic.model_validate(o) for o in orders]


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(order_id: int, db: DbSession) -> OrderDetail:
    order = await order_crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderDetail.model_validate(order)


@router.post("/", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: DbSession) -> OrderPublic:
    order = await order_crud.create_order(db, payload)
    return OrderPublic.model_validate(order)


@router.patch("/{order_id}", response_model=OrderPublic)
async def patch_order(order_id: int, payload: OrderUpdate, db: DbSession) -> OrderPublic:
    order = await order_crud.update_order(db, order_id, payload)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderPublic.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: DbSession) -> None:
    if not await order_crud.delete_order(db, order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
