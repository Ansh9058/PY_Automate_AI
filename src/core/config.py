from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

# -------------------------------------------------
# BASE PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


# -------------------------------------------------
# SETTINGS
# -------------------------------------------------
class Settings(BaseSettings):
    # -----------------------------
    # APP
    # -----------------------------
    APP_NAME: str = "PyAutomate AI"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # -----------------------------
    # SECURITY
    # -----------------------------
    SECRET_KEY: str = "dev-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # -----------------------------
    # DATABASE (SQLite default)
    # -----------------------------
    DATABASE_URL: Optional[str] = None

    # PostgreSQL (optional – prod)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: Optional[str] = None

    # -----------------------------
    # REDIS / CELERY
    # -----------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # -----------------------------
    # MONGO (optional)
    # -----------------------------
    MONGO_URL: Optional[str] = None
    MONGO_DB: str = "pyautomate"

    # -----------------------------
    # INIT LOGIC
    # -----------------------------
    def model_post_init(self, __context):
        """
        Post-init logic for derived values
        """

        # SQLite for local/dev
        if not self.DATABASE_URL:
            sqlite_path = BASE_DIR / "pyautomate.db"
            self.DATABASE_URL = f"sqlite:///{sqlite_path}"

        # Celery defaults
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL

        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL

    # -----------------------------
    # CONFIG
    # -----------------------------
    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True


# -------------------------------------------------
# SINGLETON
# -------------------------------------------------
settings = Settings()
