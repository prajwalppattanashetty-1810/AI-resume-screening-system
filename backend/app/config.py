import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "resume_screener.db").replace("\\", "/")
DEFAULT_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True
    database_url: str = f"sqlite:///{DEFAULT_DB_PATH}"
    max_upload_size_mb: int = 10
    upload_dir: str = DEFAULT_UPLOAD_DIR
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-this-to-a-random-secret-key"

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra="ignore"
    )


@lru_cache()
def get_settings():
    return Settings()
