import json
import random

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud import cart as cart_crud
from app.crud import order as order_crud
from app.crud import order_line as line_crud
from app.schemas.checkout import CheckoutBilling, CheckoutCompleteResponse, CheckoutLuckLine
from app.schemas.order import OrderCreate
from app.schemas.order_line import OrderLineCreate

router = APIRouter()


@router.post("/complete", response_model=CheckoutCompleteResponse)
async def checkout_complete(
    payload: CheckoutBilling,
    db: DbSession,
    user: CurrentUser,
) -> CheckoutCompleteResponse:
    rows = await cart_crud.list_cart_items(db, user.id)
    if not rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    for row in rows:
        game = row.game
        if game.stock < row.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for «{game.title}»",
            )

    luck_lines: list[CheckoutLuckLine] = []
    luck_snapshot: list[dict] = []

    order = await order_crud.create_order(
        db,
        OrderCreate(user_id=user.id, status="pending", billing_snapshot_json=None),
    )

    for row in rows:
        game = row.game

        won = random.random() < 0.5
        wheel_adjustment_cents = -100 if won else 100
        adjustment_uah_per_unit = -1 if won else 1

        await line_crud.create_order_line(
            db,
            OrderLineCreate(
                order_id=order.id,
                game_id=game.id,
                quantity=row.quantity,
                unit_price_cents=game.price_cents,
                wheel_adjustment_cents=wheel_adjustment_cents,
            ),
        )

        if won:
            game.luck_wins_count += 1
        else:
            game.luck_losses_count += 1

        game.stock -= row.quantity
        game.units_purchased += row.quantity

        luck_lines.append(
            CheckoutLuckLine(
                game_id=game.id,
                title=game.title,
                quantity=row.quantity,
                won=won,
                adjustment_uah_per_unit=adjustment_uah_per_unit,
            ),
        )
        luck_snapshot.append(
            {
                "game_id": game.id,
                "title": game.title,
                "quantity": row.quantity,
                "won": won,
                "adjustment_uah_per_unit": adjustment_uah_per_unit,
            },
        )

    await cart_crud.clear_cart(db, user.id)

    snapshot = {
        "billing": payload.model_dump(mode="json"),
        "luck": luck_snapshot,
    }
    order.billing_snapshot_json = json.dumps(snapshot, ensure_ascii=False)
    order.status = "paid"
    await db.flush()
    await db.refresh(order)

    total_cents = order.total_cents
    total_uah = round(total_cents / 100.0, 2)

    return CheckoutCompleteResponse(
        order_id=order.id,
        lines=luck_lines,
        total_cents=total_cents,
        total_uah=total_uah,
    )
