import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    SQLALCHEMY_ASYNCIO_DATABASE_URI = os.getenv("SQLALCHEMY_ASYNCIO_DATABASE_URI", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = (
        365 * 24 * 60 * 60
    )  # Token expired after 365 days
    SECURITY_ALGORITHM = "HS256"
    USERNAME_AUTH = os.getenv("USERNAME_AUTH", "")
    PASSWORD_AUTH = os.getenv("PASSWORD_AUTH", "")
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, "logging.ini")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


settings = Settings()
