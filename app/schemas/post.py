from pydantic import BaseModel


class PostResponse(BaseModel):
    id: int

