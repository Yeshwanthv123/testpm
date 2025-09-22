from pydantic_settings import BaseSettings

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

    # This now matches the variable in your .env file
    SECRET_KEY: str = "a-very-secret-key-that-you-should-change"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()