from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import secrets
from pathlib import Path

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "thefoxxstuff"
    secret_key: str = secrets.token_urlsafe(48)
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    access_token_expire_minutes: int = 1440
    upload_dir: str = str(Path(__file__).parent / "uploads")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    thumb_size: tuple = (400, 400)
    medium_size: tuple = (1200, 1200)
    allowed_extensions: set = {"jpg", "jpeg", "png", "gif", "webp"}

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
