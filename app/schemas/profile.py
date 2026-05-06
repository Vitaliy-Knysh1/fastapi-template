from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    display_name: str = Field(default="", max_length=200)
    bio: str | None = Field(None, max_length=4000)
    country: str | None = Field(None, max_length=80)


class ProfileCreate(ProfileBase):
    user_id: int


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=200)
    bio: str | None = Field(None, max_length=4000)
    country: str | None = Field(None, max_length=80)


class ProfilePublic(ProfileBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}
