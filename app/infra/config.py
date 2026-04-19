from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    pexels_api_key: str = Field(..., alias="PEXELS_API_KEY")
    wp_base_url: str = Field(..., alias="WP_BASE_URL")
    wp_user: str = Field(..., alias="WP_USER")
    wp_app_password: str = Field(..., alias="WP_APP_PASSWORD")
    linkedin_access_token: str = Field(..., alias="LINKEDIN_ACCESS_TOKEN")
    linkedin_person_urn: str = Field(..., alias="LINKEDIN_PERSON_URN")

    app_db_path: Path = Field(default=Path("data/app.db"), alias="APP_DB_PATH")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
