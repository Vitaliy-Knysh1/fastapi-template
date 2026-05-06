from pydantic import BaseModel, Field


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=8000)
    price_cents: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)


class GameCreate(GameBase):
    genre_id: int


class GameUpdate(BaseModel):
    genre_id: int | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=220, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=8000)
    price_cents: int | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)


class GamePublic(GameBase):
    id: int
    genre_id: int

    model_config = {"from_attributes": True}
