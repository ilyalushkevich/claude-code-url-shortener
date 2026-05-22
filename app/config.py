from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/urlshortener"
    BASE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "changeme"


settings = Settings()
