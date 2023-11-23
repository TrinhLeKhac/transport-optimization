from datetime import datetime

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import ValidationError

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'


def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> str:
    """
    Decode JWT token to get username => return username
    """
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        print(payload.get('exp'))
        if payload.get('exp') < int(datetime.now().strftime("%Y%m%d%H%M%S")):
            raise HTTPException(status_code=403, detail="Token expired")
        return payload.get('username')
    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )
