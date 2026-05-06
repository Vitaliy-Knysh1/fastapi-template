from pydantic import BaseModel


class UserResponse(BaseModel):
    message: str

