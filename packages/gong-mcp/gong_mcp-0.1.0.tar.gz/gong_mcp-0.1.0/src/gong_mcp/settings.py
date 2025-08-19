"""Settings."""

from __future__ import annotations

__all__: tuple[str, ...] = ("Settings",)


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    gong_api_key: str
    gong_api_secret: str
