"""Application settings (12-factor); override via environment variables."""

import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
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

    # Comma-separated or JSON array, e.g. CORS_ORIGINS=https://app.onrender.com,http://localhost:3000
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> list[str]:
        if v is None:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                return [str(x).strip() for x in json.loads(s) if str(x).strip()]
            return [x.strip() for x in s.split(",") if x.strip()]
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

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
