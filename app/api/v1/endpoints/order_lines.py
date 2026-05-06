from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.crud import order_line as line_crud
from app.schemas.order_line import OrderLineCreate, OrderLinePublic, OrderLineUpdate

router = APIRouter()


@router.get("/", response_model=list[OrderLinePublic])
async def list_order_lines(db: DbSession) -> list[OrderLinePublic]:
    rows = await line_crud.list_order_lines(db)
    return [OrderLinePublic.model_validate(r) for r in rows]


@router.get("/order/{order_id}", response_model=list[OrderLinePublic])
async def list_lines_for_order(order_id: int, db: DbSession) -> list[OrderLinePublic]:
    rows = await line_crud.lines_for_order(db, order_id)
    return [OrderLinePublic.model_validate(r) for r in rows]


@router.get("/{line_id}", response_model=OrderLinePublic)
async def get_order_line(line_id: int, db: DbSession) -> OrderLinePublic:
    row = await line_crud.get_order_line(db, line_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order line not found")
    return OrderLinePublic.model_validate(row)


@router.post("/", response_model=OrderLinePublic, status_code=status.HTTP_201_CREATED)
async def create_order_line(payload: OrderLineCreate, db: DbSession) -> OrderLinePublic:
    row = await line_crud.create_order_line(db, payload)
    return OrderLinePublic.model_validate(row)


@router.put("/{line_id}", response_model=OrderLinePublic)
async def replace_order_line(line_id: int, payload: OrderLineCreate, db: DbSession) -> OrderLinePublic:
    row = await line_crud.replace_order_line(db, line_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order line not found")
    return OrderLinePublic.model_validate(row)


@router.patch("/{line_id}", response_model=OrderLinePublic)
async def patch_order_line(line_id: int, payload: OrderLineUpdate, db: DbSession) -> OrderLinePublic:
    row = await line_crud.update_order_line(db, line_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order line not found")
    return OrderLinePublic.model_validate(row)


@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_line(line_id: int, db: DbSession) -> None:
    if not await line_crud.delete_order_line(db, line_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order line not found")
