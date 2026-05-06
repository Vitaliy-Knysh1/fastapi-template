from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FastAPI Template"
    database_url: str = "postgresql://postgres:postgres@db:5432/app"


settings = Settings()

