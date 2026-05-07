from pydantic import BaseModel, EmailStr, Field


class CheckoutBilling(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=40)
    address_line1: str = Field(..., min_length=1, max_length=300)
    city: str = Field(..., min_length=1, max_length=120)
    postal_code: str = Field(..., min_length=1, max_length=32)
    country: str = Field(default="UA", max_length=80)


class CheckoutLuckLine(BaseModel):
    game_id: int
    title: str
    quantity: int
    won: bool
    adjustment_uah_per_unit: int = Field(
        ...,
        description="-1 if luck reduced price per unit, +1 if increased",
    )


class CheckoutCompleteResponse(BaseModel):
    order_id: int
    lines: list[CheckoutLuckLine]
    total_cents: int
    total_uah: float
