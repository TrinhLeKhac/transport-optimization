from typing import Union, Any
from datetime import timedelta, datetime
import jwt

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'


def verify_password(username, password):
    if username == 'admin' and password == 'admin':
        return True
    return False


def generate_token(username: Union[str, Any], password: Union[str, Any]) -> str:
    expire = int((datetime.now() + timedelta(
        seconds=60 * 30  # Expired after 30 minutes
    )).strftime("%Y%m%d%H%M%S"))
    to_encode = {
        "exp": expire, "username": username, "password": password
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt
