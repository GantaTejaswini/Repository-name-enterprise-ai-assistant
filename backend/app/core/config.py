from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Assistant"
    app_version: str = "0.1.0"

    elasticsearch_url: str = "http://localhost:9200"
    redis_url: str = "redis://localhost:6379/0"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "enterprise_ai"
    postgres_user: str = "enterprise_user"
    postgres_password: str = "enterprise_password"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    llm_provider: str = "extractive"

    cors_origins: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_cors_origins() -> list[str]:
    return [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]