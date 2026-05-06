from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Videogame Store API"
    # Standard sync URL form; async URL is derived for SQLAlchemy + asyncpg
    database_url: str = "postgresql://postgres:postgres@localhost:5432/app"

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
