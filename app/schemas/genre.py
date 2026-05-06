from pydantic import BaseModel, Field


class GenreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    slug: str = Field(..., min_length=1, max_length=140, pattern=r"^[a-z0-9\-]+$")


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    slug: str | None = Field(None, min_length=1, max_length=140, pattern=r"^[a-z0-9\-]+$")


class GenrePublic(GenreBase):
    id: int

    model_config = {"from_attributes": True}
