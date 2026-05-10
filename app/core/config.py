"""Application settings (12-factor); override via environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    secret_key: str = "change-me-use-openssl-rand-hex-32-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = (
        "postgresql+asyncpg://soc:soc@localhost:5432/soc_copilot"
    )

    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # LLM: OpenAI-compatible; optional — RAG still works with retrieval-only fallback
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    expose_docs: bool = True

    # Rate limits (SlowAPI)
    rate_limit_default: str = "60/minute"
    rate_limit_rag: str = "20/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()
