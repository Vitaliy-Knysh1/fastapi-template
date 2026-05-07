from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.order_line import OrderLinePublic


class OrderBase(BaseModel):
    status: str = Field(default="pending", max_length=40)


class OrderCreate(OrderBase):
    user_id: int
    billing_snapshot_json: str | None = None


class OrderUpdate(BaseModel):
    status: str | None = Field(None, max_length=40)


class OrderPublic(OrderBase):
    id: int
    user_id: int
    total_cents: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderDetail(OrderPublic):
    lines: list[OrderLinePublic] = Field(default_factory=list)
