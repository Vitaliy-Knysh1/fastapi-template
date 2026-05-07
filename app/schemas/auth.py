from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=200)

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v

    @field_validator("name", "password", mode="before")
    @classmethod
    def strip_text(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v

    @field_validator("password", mode="before")
    @classmethod
    def strip_password(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
