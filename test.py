import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from config import settings

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))

print(settings.SECRET_KEY)
print(settings.SQL_DATABASE_URL)
print(settings.USERNAME_AUTH)
print(settings.PASSWORD_AUTH)