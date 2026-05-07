from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Luckygames Shop"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/app"

    jwt_secret: str = Field(
        default="dev-insecure-jwt-key-change-in-production",
        description="Set JWT_SECRET in .env for production",
        validation_alias=AliasChoices("jwt_secret", "JWT_SECRET"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    auth_cookie_name: str = "access_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    @field_validator("cookie_secure", mode="before")
    @classmethod
    def parse_cookie_secure(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in {"1", "true", "yes"}
        return False

    @property
    def database_url_async(self) -> str:
        url = self.database_url
        if url.startswith(("postgresql+psycopg_async://", "postgresql+asyncpg://")):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg_async://", 1)
        return url

    @property
    def database_url_sync(self) -> str:
        url = self.database_url
        if url.startswith("postgresql+psycopg_async://"):
            return url.replace("postgresql+psycopg_async://", "postgresql://", 1)
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url


settings = Settings()
