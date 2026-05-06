from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)
    name: str = Field(..., min_length=1, max_length=200)


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
