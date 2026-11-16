"""Application settings shared with TV1 (contract H4)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    encryption_key_b64: str
    key_version: str = "v1"
    admin_token: str
    viewer_token: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
