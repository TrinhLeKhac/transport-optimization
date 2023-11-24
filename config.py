import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Settings:
    SQL_DATABASE_URL = os.getenv('SQL_DATABASE_URL', '')
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 365 * 24 * 60 * 60  # Token expired after 7 days
    SECURITY_ALGORITHM = 'HS256'
    USERNAME_AUTH = os.getenv('USERNAME_AUTH', '')
    PASSWORD_AUTH = os.getenv('PASSWORD_AUTH', '')
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.ini')


settings = Settings()

# import json
#
# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)
#
#
# class Config:
#     SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI")
