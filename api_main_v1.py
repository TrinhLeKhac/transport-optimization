from typing import Annotated

from scripts.api.router import result, output, order, zns
from scripts.api.auth import authen
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status, Depends, HTTPException
from ast import literal_eval
from fastapi.responses import JSONResponse

from scripts.api.auth.security import validate_token
from fastapi.security import OAuth2PasswordRequestFormStrict, OAuth2PasswordRequestForm
from scripts.api.auth.token import *

app = FastAPI(
    title="API SUPERSHIP",
    description="There are APIs getting calculation result from history transactions of SUPERSHIP",
    docs_url="/docs",
)


def create_str_err(exc_str):
    errs = literal_eval(exc_str)
    res = []
    for err in errs:
        s = str(err["loc"]) + " => " + err["msg"]
        res.append(s)
    return "; ".join(res)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    path = request.url.path
    if path == "/superai/auth":
        content = {"error": True, "message": create_str_err(exc_str), "data": {"token": "Invalid"}}
    else:
        content = {"error": True, "message": create_str_err(exc_str), "data": []}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if verify_password(username=form_data.username, password=form_data.password):
        print(form_data.username)
        print(form_data.password)
        app.include_router(authen.router, tags=[""], prefix="/superai/auth")
        app.include_router(zns.router, tags=[""], prefix="/superai/zns", dependencies=[Depends(validate_token)])
        app.include_router(order.router, tags=[""], prefix="/superai/order", dependencies=[Depends(validate_token)])
        app.include_router(result.router, tags=[""], prefix="/superai/result", dependencies=[Depends(validate_token)])
        app.include_router(output.router, tags=[""], prefix="/superai/output", dependencies=[Depends(validate_token)])
    else:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception
