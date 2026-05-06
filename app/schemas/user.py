from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=320)
    name: str = Field(..., min_length=1, max_length=200)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, max_length=320)
    name: str | None = Field(None, min_length=1, max_length=200)


class UserPublic(UserBase):
    id: int

    model_config = {"from_attributes": True}
