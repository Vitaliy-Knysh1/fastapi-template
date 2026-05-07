from __future__ import annotations

import json

from pydantic import BaseModel, Field

from app.models.game import Game


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=8000)
    price_cents: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)


class GameCreate(GameBase):
    genre_id: int
    thumbnail_path: str | None = Field(None, max_length=300)
    price_uah: int = Field(0, ge=0)
    tags_json: str | None = Field(None, description='JSON array of tag strings, e.g. ["Indie"]')


class GameUpdate(BaseModel):
    genre_id: int | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=220, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=8000)
    price_cents: int | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    thumbnail_path: str | None = Field(None, max_length=300)
    price_uah: int | None = Field(None, ge=0)
    units_purchased: int | None = Field(None, ge=0)
    tags_json: str | None = None


class GamePublic(GameBase):
    id: int
    genre_id: int
    thumbnail_path: str | None = None
    price_uah: int = 0
    units_purchased: int = 0
    luck_wins_count: int = 0
    luck_losses_count: int = 0
    tags: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @classmethod
    def from_game(cls, game: Game) -> GamePublic:
        tags: list[str] = []
        if game.tags_json:
            try:
                parsed = json.loads(game.tags_json)
                if isinstance(parsed, list):
                    tags = [str(x) for x in parsed]
            except json.JSONDecodeError:
                tags = []
        return cls(
            id=game.id,
            genre_id=game.genre_id,
            title=game.title,
            slug=game.slug,
            description=game.description,
            price_cents=game.price_cents,
            stock=game.stock,
            thumbnail_path=game.thumbnail_path,
            price_uah=game.price_uah,
            units_purchased=game.units_purchased,
            luck_wins_count=game.luck_wins_count,
            luck_losses_count=game.luck_losses_count,
            tags=tags,
        )


class GameDetailPublic(GamePublic):
    genre_name: str

