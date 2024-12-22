import secrets
from typing import List

from fastapi_mail import ConnectionConfig
from pydantic import  EmailStr, MongoDsn
from pydantic_settings import BaseSettings
from app.core.enums import LogLevel

class Settings(BaseSettings):
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = []
    UVICORN_HOST: str
    UVICORN_PORT: int
    USE_CORRELATION_ID: bool = True
    LOG_LEVEL: str = LogLevel.INFO
    MONGODB_URI: str = "mongodb://db:27017/"  # type: ignore[assignment]
    MONGODB_DB_NAME: str = "ci-portal"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 60 minutes * 24 hours * 1 = 1 day
    SECRET_KEY: str = secrets.token_urlsafe(32)
    RESET_TOKEN_EXPIRE_MINUTES: str = 60
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr | None = None
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    FRONTEND_URL: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    class Config:
        # Place your .env file under this path
        env_file = ".env"
        env_prefix = "CI_PORTAL_API_"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]

