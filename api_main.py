from scripts.api import authen, order, result, zns, output
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status, Depends
from ast import literal_eval
from fastapi.responses import JSONResponse

from scripts.auth.security import validate_token

app = FastAPI(
    title="API SUPERSHIP",
    description="There are APIs getting calculation result from history transactions of SUPERSHIP",
    docs_url="/",
    dependencies=[Depends(validate_token)],
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


app.include_router(authen.router, tags=[""], prefix="/superai/auth")
app.include_router(zns.router, tags=[""], prefix="/superai/zns")
app.include_router(order.router, tags=[""], prefix="/superai/order")
app.include_router(result.router, tags=[""], prefix="/superai/result")
app.include_router(output.router, tags=[""], prefix="/superai/output")
