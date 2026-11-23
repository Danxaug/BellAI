from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Bellia"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = False
    APP_BASE_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "http://localhost:8000"

    # Groq
    GROQ_API_KEY: str = Field(..., min_length=1)
    GROQ_MODEL_PRIMARY: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_FALLBACK: str = "llama3-8b-8192"
    GROQ_TIMEOUT: int = 30

    # DB
    DATABASE_URL: str = "sqlite+aiosqlite:////tmp/bellia.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Seguridad
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True

    # Observabilidad
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    # WhatsApp
    WHATSAPP_PHONE: str = "573168331986"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret(cls, v: str, info) -> str:
        env = info.data.get("APP_ENV", "development")
        if env == "production" and ("change-me" in v or len(v) < 32):
            raise ValueError("SECRET_KEY must be strong (>=32 chars) in production")
        return v

    @field_validator("GROQ_API_KEY")
    @classmethod
    def validate_groq(cls, v: str) -> str:
        if v and "DUMMY" in v.upper():
            raise ValueError("GROQ_API_KEY cannot be a dummy value")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()