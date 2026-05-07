from datetime import datetime

from pydantic import BaseModel, Field


class GameCommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=4000)


class GameCommentPublic(BaseModel):
    id: int
    body: str
    created_at: datetime
    author_name: str

    model_config = {"from_attributes": True}
