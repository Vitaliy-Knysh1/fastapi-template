from pydantic import BaseModel, Field


class OrderLineBase(BaseModel):
    quantity: int = Field(..., gt=0)
    unit_price_cents: int = Field(..., ge=0)
    wheel_adjustment_cents: int = Field(
        default=0,
        ge=-1000,
        le=1000,
        description="Per-unit luck adjustment in kopiykas (±100 = ±1 UAH).",
    )


class OrderLineCreate(OrderLineBase):
    order_id: int
    game_id: int


class OrderLineUpdate(BaseModel):
    quantity: int | None = Field(None, gt=0)
    unit_price_cents: int | None = Field(None, ge=0)
    wheel_adjustment_cents: int | None = Field(None, ge=-1000, le=1000)


class OrderLinePublic(OrderLineBase):
    id: int
    order_id: int
    game_id: int

    model_config = {"from_attributes": True}
