import os
from pydantic_settings import BaseSettings


# Prefer `.env` if present; otherwise fall back to `.env.local` which is a
# safe, committable local defaults file included in the repo to make on-clone
# runs easier for developers.
_env_file = ".env"
if not os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env")):
    # look in the package root
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env.local")):
        _env_file = ".env.local"


class Settings(BaseSettings):
    APP_NAME: str = "PMBOT Auth Backend"
    JWT_SECRET: str = "dev-secret"
    JWT_REFRESH_SECRET: str = "dev-refresh-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./app.db"

    # OAuth + Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    OAUTH_REDIRECT_BASE: str = "http://localhost:8000"

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    LINKEDIN_CLIENT_ID: str | None = None
    LINKEDIN_CLIENT_SECRET: str | None = None

    SECRET_KEY: str = "a-very-secret-key-that-you-should-change"

    # ✅ NEW: recognize your CSV path env var
    PM_QUESTIONS_CSV: str | None = None

    class Config:
        env_file = _env_file
        case_sensitive = False
        extra = "ignore"  # ✅ allow future envs without crashing

settings = Settings()
